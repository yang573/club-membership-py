# club-membership-py
Compile attendance data from sign-in sheets across different club events. Rebuilt from the JavaScript version.

*This app is a work in progress. You will probably need to tweak some code and configurations to get it functional. Use at your own discretion.*

To use this application, you will need:
* A MySQL database
* Flask
* mysqlclient
* requests

The scripts for populating the database schema can be found in the scripts/ folder.

You will need to create a config.py file in the src/ folder. There, add the following variables:
```Python
database_name=[database name]
database_user=[username] # make sure you have read/write permissions
database_password=[password]

mailchimp_user=[username]
mailchimp_api_key=[api key]
mailchimp_dc=[data center] # found at the end of your api key as eg. 'us5'
mailchimp_main_audience_id=[id] # found in the under audience settings
```

Right now, this application supports the following end-points:
```
POST /database/event/upload/csv
```
Upload a csv containing sign-ins the the database. The csv must contain 'First Name', 'Last Name', "Email', & 'Newsletter' or 'Mailing List' in the headers. Adds any subscriptions or unsubscriptions to Mailchimp.

```
POST /database/member/
```
Add a member to the database. Requires the following parameters in the body:
  'firstName', 'lastName', 'yearID', 'email', newsletter'

```
GET /database/misc/newsletter
```
Get the number of members subscribed to the newsletter according to the database.

Major TODO's:
* Look at MySQLAlchemy for constructing SQL strings
* Add more endpoints
* Host on an internal or cloud server
* And many more
