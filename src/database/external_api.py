import hashlib
import requests

from . import MAILCHIMP_URL, MAILCHIMP_USER, MAILCHIMP_KEY, MAILCHIMP_LIST_ID

MAILCHIMP_CONTACT = "/lists/{}/members/".format(MAILCHIMP_LIST_ID)

# Mailchimp
def get_hash(email):
    email = email.lower()
    return hashlib.md5(email.encode('utf-8')).hexdigest()

# member_email: The email of the subscriber to update on Mailchimp
# is_subscribed: Bool indicating if the member wants to subscribe
# Returns: True on 200 status code, False otherwise
def update_member_newsletter(email: str, first_name: str, last_name: str, is_subscribed: bool):
    url_params = {'fields': 'email_addresss,status'}
    if is_subscribed:
        # Create & subscribe
        body = {
                "email_address": email,
                "status": "subscribed",
                "merge_fields": {
                    "FNAME": first_name,
                    "LNAME": last_name
                }
            }
        req = requests.request('POST',
                        MAILCHIMP_URL + MAILCHIMP_CONTACT,
                        params=url_params,
                        json=body,
                        auth=(MAILCHIMP_USER, MAILCHIMP_KEY))

        # If create fails, then update
        if req.status_code == requests.codes.bad_request:
            body = { "status": "subscribed" }
            req = requests.request('PATCH',
                            MAILCHIMP_URL + MAILCHIMP_CONTACT + get_hash(email),
                            params=url_params,
                            json=body,
                            auth=(MAILCHIMP_USER, MAILCHIMP_KEY))
            print(req.text)

        return req.status_code == requests.codes.ok

    else:
        # Unsubscribe
        # If the email doesn't exist, then it'll fail without consequence
        body = { "status": "unsubscribed" }
        req = requests.request('PATCH',
                        MAILCHIMP_URL + MAILCHIMP_CONTACT + get_hash(email),
                        params=url_params,
                        json=body,
                        auth=(MAILCHIMP_USER, MAILCHIMP_KEY))

        print(req.text)
        return req.status_code == requests.codes.ok

