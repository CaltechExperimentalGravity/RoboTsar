# RoboTsar
JC reminder service python script

To install needed packages in your local environment.  This can be done using pip:

```bash
pip install -r requirements.txt
```

To run the script you must have the environment in which the pip installed packages activated.  If running from crontab you should give the **FULL** path to python in virtual environment and full path to the TsarMailer.py script.  Another option is to wrap the script inside a bash script.

To run the weekly alert:
```bash
python TsarMailer.py --weeklyreminder
```

To run reminder on days
```bash
python TsarMailer.py --dayreminder
```

There are also options to run a dry run (--dryrun) which generates the email but skips the very last step of sending.  Note that in the dryrun mode the script logs into the email server using the credentials provided, skips the send command and then closes the connection: this is a good way to test if the script can see the server and correctly compose an email without triggering an actual email send.

You can also run the script in --debug mode.  The position in the list and names of presenters will be displayed in the command prompt.  This can be handy for checking what the script is doing with the list and for setting the phase.

For help and script usage run
```bash
python TsarMailer.py --help
```

## Credentials
The credentials for email service SMTP login are stored in a folder .credentials/ .  You need to edit the script TsarMailer.py.  At the top there will be a variable credentialsFile in which you give the *full* path to the credentials file.  This is a YML with login details of the JournalClubRoboTsar@gmail.com account. These are application specific login and not the root access credentials to the account; they only give access to send/receive actions in the account.


Ask awade for the RoboTsar credentials.
