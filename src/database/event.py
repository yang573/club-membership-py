import csv, re
from flask import Blueprint, request

from . import *
from .utility import *
from .db_func import *
from .external_api import update_member_newsletter

bp = Blueprint('event', __name__)

EMAIL_REGEX = re.compile(r"([A-Z0-9_.+-]+@[A-Z0-9-]+\.[A-Z0-9-.]+)", re.IGNORECASE)
EVENT_COLUMNS = ["First Name", "Last Name", "Year", "Email", "(Mailing List|Newsletter)"];

# Add or update a member from an event
# row: A list representing a row from the sign-in csv
# header_order: A list for converting the order of the header
#   from the csv to the order specfied in EVENT_COLUMNS
# use_mailchimp: A tuple where #1 indicates whether to use mailchimp
#   and #2 indicates whether to unsub if needed
# Returns: A 3-tuple with the MemberID, a bool
def insert_member_from_event(row, header_order, use_mailchimp):
    sql = None
    result = None
    memberID = -1
    email = row[header_order[3]].lower()
    row[header_order[3]] = email
    email_index = header_order[3]
    cursor = conn.cursor()

    print(row)

    # Check if record is in database, and get MemberID
    if EMAIL_REGEX.match(email):
        sql = select(members, columns=[members[0]], conditions=[(members[4], email)])
    else:
        header_order[3] = -1 # Ignore invalid email for rest of function
        sql = select(members,
                columns=[members[0]],
                conditions=[
                    (members[1], row[header_order[0]]),
                    (members[2], row[header_order[1]]),
                ])

    cursor.execute(sql)
    result = cursor.fetchone()
    #TODO: More than one record edge case
    if result:
        memberID = result[0]

    # Get the academic year of the member
    result = None
    if header_order[2] != -1:
        sql = "SELECT IFNULL(({}), ({})) AS {}".format(
            select(academic_year,
                    columns=[academic_year[0]],
                    conditions=[(academic_year[1], row[header_order[2]], "LIKE")]),
            select(academic_year,
                    columns=[academic_year[0]],
                    order=(academic_year[0], 1),
                    limit=1),
            academic_year[0])
        #print(sql)
        cursor.execute(sql)
        result = cursor.fetchone()
    if result:
        row[header_order[2]] = result[0]

    # Insert/Update member
    sql = None
    # Check if newsletter sub was marked
    newsletter_sub = -1
    if header_order[4] != -1:
        if re.search(r"no", row[header_order[4]], re.IGNORECASE):
            row[header_order[4]] = 0
            newsletter_sub = 0
        elif not row[header_order[4]]:
            row[header_order[4]] = -1
            newsletter_sub = -1
        else:
            row[header_order[4]] = 1
            newsletter_sub = 1

    if memberID != -1:
        # Update
        update_columns = []
        update_values = []
        # academic year
        if result:
            update_columns.append(members[3])
            update_values.append(result[0])
        # newsletter
        if newsletter_sub != -1:
            update_columns.append(members[5])
            update_values.append(newsletter_sub)

        if update_columns:
            sql = update(members, update_columns, update_values, memberID)
    else:
        # Insert
        columns = []
        values = []
        for i in range(len(header_order)):
            if header_order[i] != -1:
                columns.append(members[i+1])
                values.append(row[header_order[i]])
        sql = insert(members, values, columns)

    # If a row was modified, update newsletter setting
    # This could be an existing member updating their academic year,
    # but the wasted calls should only occur at the beginning of the academic year.
    newsletter_status = -1
    if use_mailchimp[0] and newsletter_sub != -1 and cursor.rowcount == 1:
        newsletter_ret = update_member_newsletter(email,
                             row[header_order[0]],
                             row[header_order[1]],
                             row[header_order[4]],
                             use_mailchimp[1])
        if newsletter_ret:
            newsletter_status = newsletter_sub

    # Return MemberID, whether the member is new, and changes in newsletter sub
    if sql:
        cursor.execute(sql)

    if use_mailchimp[0]:
        if memberID != -1:
            result = (memberID, True, newsletter_status)
        else:
            result = (cursor.lastrowid, False, newsletter_status)
    else:
        if memberID != -1:
            result = (memberID, True)
        else:
            result = (cursor.lastrowid, False)

    header_order[3] = email_index # Restore email index
    cursor.close()
    return result


# Routing

# Upload CSV from an event
# TODO: Get date and semester from the csv
# TODO: Get name from the csv title
@bp.route('/upload/csv', methods=["POST"])
def upload_csv():
    number_new = 0
    number_returning = 0
    newsletter_sub = 0
    newsletter_unsub = 0
    members_present = []

    # Verify a csv file was uploaded
    if 'file' not in request.files:
        flash('You forgot the file')
        return "Error uploading csv"
    f = request.files['file']
    if f.filename == '' or not allowed_file(f.filename):
        flash('Please select a csv')
        return "Error uploading csv"

    # Parse file as CSV
    contents = f.read().decode("utf-8")
    csv_list = contents.split('\r\n')

    reader = csv.reader(csv_list)
    header = next(reader)
    print(header)
    header_order = get_header_index(header, EVENT_COLUMNS)

    # Check that full name and email are in csv
    if header_order[0] == -1 or header_order[1] == -1 or header_order[3] == -1:
        return {message: "Could not find first and last name, and email in the csv header"}, 400

    # Go through each row and insert/modify member data
    members_present = []

    mailchimp = False
    unsub = False
    if request.form['mailchimp']:
        mailchimp = str(request.form['mailchimp']).lower() in ('yes','true','1')
        if request.form['unsub']:
            unsub = str(request.form['unsub']).lower() in ('yes','true','1')

    for row in reader:
        result = insert_member_from_event(row, header_order, (mailchimp, unsub))
        members_present.append(result[0])
        if result[1]:
            number_returning += 1
        else:
            number_new += 1

        if mailchimp:
            if result[2] == 0:
                newsletter_unsub += 1
            elif result[2] == 1:
                newsletter_sub += 1

    # Get SemesterID
    sql = None
    cursor = conn.cursor()
    if request.form['semester']:
        sql = select(semester, conditions=[(semester[1], request.form['semester'])])
    else:
        sql = select(semester, order=(semester[0], 1), limit=1)

    cursor.execute(sql)
    result = cursor.fetchone()[0]

    # Insert the event into the table
    sql = insert(events,
            [request.form['eventName'],
                request.form['eventDate'],
                result,
                len(members_present)
                ],
            events[1:])
    cursor.execute(sql)

    # Map EventID to MemberID in Member_Event table
    eventID = cursor.lastrowid
    for i in members_present:
        sql = insert(member_event, [i, eventID])
        cursor.execute(sql)

    cursor.close()
    conn.commit()

    # Return event upload info to user

#    path = absolute_upload_path(f)
#    save_file(f, path)
#
#    with open(path, newline='') as csvfile:
#        print('Contents:')
#        print(csvfile.read())
#        print(csvfile)
#
#    delete_file(path)
    response = {'EventID': eventID,
            'Attendance': len(csv_list) - 1,
            'Number_Returning': number_returning,
            'Number_New': number_new}
    if mailchimp:
        response['Number_Subscriptions'] = newsletter_sub
        response['Number_Unsubscriptions'] = newsletter_unsub

    return response, 200

