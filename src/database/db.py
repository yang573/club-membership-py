from collections.abc import Sequence

# Tables
class Table(Sequence):
    name = None
    columns = None

    def __getitem__(self, i):
        return self.columns[i]
    
    def __len__(self):
        return len(self.columns)

class Academic_Year(Table):
    name = "academic_year"
    columns = ["YearID", "Value"]

class Event(Table):
    name = "events"
    columns = ["EventID", "Name", "Date", "SemesterID", "Attendance"]

class Members(Table):
    name = "members"
    columns = ["MemberID", "FirstName", "LastName", "YearID", "Email", "Newsletter"]

class Member_Event(Table):
    name = "member_event"
    columns = ["MemberID", "EventID"]

class Semester(Table):
    name = "semester"
    columns = ["SemesterID", "Value"]

