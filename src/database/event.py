import csv, re
from flask import Blueprint, request

from . import *
from .utility import *
from .db_func import *

bp = Blueprint('event', __name__)

EMAIL_REGEX = re.compile(r"([A-Z0-9_.+-]+@[A-Z0-9-]+\.[A-Z0-9-.]+)", re.IGNORECASE)
EVENT_COLUMNS = ["First Name", "Last Name", "Year", "Email", "(Mailing List|Newsletter)"];

def insert_member_from_event(row, header_order):
    sql = None
    result = None
    memberID = -1
    email = row[header_order[3]].lower()
    row[header_order[3]] = email
    cursor = conn.cursor()

    print(row)

    # Check if record is in database, and get MemberID
    if EMAIL_REGEX.match(email):
        sql = select(members, columns=[members[0]], conditions=[(members[4], email)])
    else:
        sql = select(members,
                columns=[members[0]],
                conditions=[
                    (members[1], row[header_order[0]]),
                    (members[2], row[header_order[1]]),
                ])

    cursor.execute(sql)
    result = cursor.fetchone()
    #TODO: More than one record edge case
    print(result)
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
        cursor.execute(sql)
        result = cursor.fetchone()

    # Insert/Update member
    sql = None
    if header_order[4] != -1:
        if re.search(r"no", row[header_order[4]], re.IGNORECASE):
            row[header_order[4]] = 0
        else:
            row[header_order[4]] = 1

    if memberID != -1:
        # Update
        update_columns = []
        update_values = []
        # academic year
        if result:
            update_columns.append(members[3])
            update_values.append(result)
        # newsletter
        if header_order[4] != -1:
            update_columns.append(members[5])
            update_values.append(row[header_order[4]])

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

    # Return MemberID and whether the member is new
    if sql:
        cursor.execute(sql)

    if memberID != -1:
        result = (memberID, True)
    else:
        result = (cursor.lastrowid, False)

    cursor.close()
    return result

@bp.route('/upload/csv', methods=["POST"])
def upload_csv():
    number_new = 0
    number_returning = 0
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
    print(f)
    print(f.mimetype_params)
    contents = f.read().decode("utf-8")
    csv_list = contents.split('\r\n')

    reader = csv.reader(csv_list)
    header = next(reader)
    print(header)
    header_order = get_header_index(header, EVENT_COLUMNS)

    # Go through each row and insert/modify member data
    members_present = []
    for row in reader:
        result = insert_member_from_event(row, header_order)
        members_present.append(result[0])
        if result[1]:
            number_returning += 1
        else:
            number_new += 1

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
    #conn.commit()

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
    return {'EventID': eventID,
            'Attendance': len(csv_list) - 1,
            'Number_Returning': number_returning,
            'Number_New': number_new}, 200

