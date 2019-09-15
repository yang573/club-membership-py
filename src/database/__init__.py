import os, sys, inspect
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import MySQLdb
import MySQLdb.cursors
import config
from .db import *

# Establish Connection
db_host = '127.0.0.1'
db_port = 3306
db_name = config.database_name
db_user = config.database_user
db_password = config.database_password

conn = MySQLdb.connect(host=db_host,
                             port=db_port,
                             user=db_user,
                             passwd=db_password,
                             db=db_name)
                             #cursorclass=MySQLdb.cursors.CursorDictRowsMixIn)

print("DB Loaded")

academic_year = Academic_Year()
events = Event()
members = Members()
member_event = Member_Event()
semester = Semester()

MAILCHIMP_URL = "https://{}.api.mailchimp.com/3.0".format(config.mailchimp_dc)
MAILCHIMP_USER = config.mailchimp_user
MAILCHIMP_KEY = config.mailchimp_api_key
MAILCHIMP_LIST_ID = config.mailchimp_main_audience_id

