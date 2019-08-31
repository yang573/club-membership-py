import os, sys, inspect
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from sqlalchemy import *
import config

#class Table:
#    name = None
#    columns = None
#
#class Event(Table):
#    name = "events"
#    columns = ["EventID", "Name", "Date", "SemesterID", "Attendance"]
#
#class Members(Table):
#    name = "members"
#    columns = ["MemberID", "FirstName", "LastName", "YearID", "Email", "Newsletter"]
#
#class Member_Event(Table):
#    name = "member_event"
#    columns = ["MemberID", "EventID"]

db_host = '127.0.0.1'
db_port = 3306
db_name = config.database_name
db_user = config.database_user
db_password = config.database_password

engine_url = "mysql+mysqldb://{}:{}@{}:{}/{}".format(db_user,
                                                     db_password,
                                                     db_host,
                                                     db_port,
                                                     db_name)
engine = create_engine(engine_url)

metadata = MetaData(bind=engine)
metadata.reflect()

tables = metadata.tables
conn = engine.connect()

print("DB Loaded");

