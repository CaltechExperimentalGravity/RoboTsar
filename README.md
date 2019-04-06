# RoboTsar
JC reminder service python script

To install needed packages in your local environment.  This can be done using pip:

```bash
pip install -r requirements.txt
```

To run the script you must have the environment in which the pip installed packages activated.  If running from crontab you should give the **FULL** path to python in virtual environment and full path to the TsarMailer.py script.  Another option is to wrap the script inside a bash script.

## Running the script from cmdline

To run the weekly alert:
```bash
python TsarMailer.py --weeklyreminder
```

To run reminder on day of journal club run
```bash
python TsarMailer.py --dayreminder
```

There are also options to run a dry run (--dryrun) which generates the email but skips the very last step of sending.  Note that in the dryrun mode the script logs into the email server using the credentials provided, skips the send command and then closes the connection: this is a good way to test if the script can see the server and correctly compose an email without triggering an actual email send.

You can also run the script in --debug mode.  The position in the list and names of presenters will be displayed in the command prompt.  This can be handy for checking what the script is doing with the list and for setting the phase.

For help and script usage run
```bash
python TsarMailer.py --help
```

## Configuring crontab

For a weekly reminder you'll want to insert a line into the crontab, something along the lines of
```
0 9 * * 0 /path/to/virtual/env/bin/python /path/to/script/RoboTsar/TsarMailer.py --weeklyreminder >> /path/to/script/RoboTsar/log_TsarMailer.log 2>&1
```

Similarly a reminder on the day can be configured as
```
0 9 * * 5 /path/to/virtual/env/bin/python /path/to/script/RoboTsar/TsarMailer.py --dayreminder >> /path/to/script/RoboTsar/log_TsarMailer.log 2>&1
```

## Variables, email text and configuring to, from and cc
After the python import commands there are a bunch of variables that can be configured for the script.  These include the script path (scriptPath), a path to a file containing the veto dates (vetodateFile) and a html link to to google spreadsheet with all the names and email addresses (jchostgsheet).  

You also need to set a start date from which the weeks are counted.  You will want to choose this date carefully so that you start the year on the nearst possible Sunday (even if its from the year before).  This way the Sunday and Friday reminders will count the same number of weeks.

All of the content of the emails and their header meta data is configured in the main function.  Email text is encoded in html (for most users) and the email sending engine will generate a plain text version for people who prefer that.  

## The google spreadsheet
Names are picked off a list hosted as a google spreadsheet.  This is to make it easier for the participants to self organize.  It means that people don't need to access nodus to be able to adjust the list.  There is no special API used for accessing these google drive documents.  It is as easy as sharing the link to the CSV version of the document from google sheets and importing using requests.  

The google spreadsheet must be publicly viewable.  Google does have APIs but it is a pain in the neck to get them to authenticate.  Public access to the csv version is the easiest way.

## Credentials
The credentials for email service SMTP login are stored in a folder .credentials/ .  You need to edit the script TsarMailer.py.  At the top there will be a variable credentialsFile in which you give the *full* path to the credentials file.  This is a YML with login details of the JournalClubRoboTsar@gmail.com account. These are application specific login and not the root access credentials to the account; they only give access to send/receive actions in the account.


Ask awade for the RoboTsar credentials.
