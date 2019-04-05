#!/Users/awade/Git/RoboTsar/env/bin/python
from __future__ import print_function
import os
from datetime import datetime
import datetime as dt
import argparse
import configparser

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import html2text

import pandas as pd  # Tools for opening csv files
import numpy as np

from StringIO import StringIO
import requests

# Configurable variables
vetodateFile = '/Users/awade/Git/RoboTsar/vetodates.csv'
credentialsFile = '/Users/awade/Git/RoboTsar/.credentials/JCTcred.secret'
jchostgsheet = ('https://docs.google.com/spreadsheets/d/'
                '1TxTmFStB9jT1xCvscr5xKY5ovuA4nme58XK4IrqI6_0/'
                'pub?gid=0&single=true&output=csv')
ListStartDate = datetime(2018, 12, 30)
# this is set for 2019, careful to include the full week or the Friday
# reminders will be out of sink with Sunday reminders.


def grabInputArgs():
    ''' Function for grabbing arguments parsed from
        cmd launch'''

    parser = argparse.ArgumentParser(
        description="Python script for sending reminders"
                    "to journal club leads to present "
                    "a paper")
    parser.add_argument(
        '--weeklyreminder',
        help="Send weekly reminder directly to this weeks presenter and the "
             " next week's presenter (advanced notice).",
        action='store_true')
    parser.add_argument(
        '--dayreminder',
        help="Send reminder on day to full journal club list.  Also cc'ed is "
             "the presenter for that day. See text in main() of script to "
             "edit details of text.",
        action='store_true')
    parser.add_argument(
        '--debug',
        help="activate debug mode of script for verbose"
             " feedback on action of script.",
        action='store_true')
    parser.add_argument(
        '--dryrun',
        help="run script without sending email",
        action='store_true')
    return parser.parse_args()


def main(vetodateFile=None, jchostgsheet=None,
         ListStartDate=datetime(2019, 1, 1)):

    # type and checking, throw assert errors on failure
    assert isinstance(vetodateFile, str), "Argument must be string"
    assert os.path.exists(vetodateFile), "vetodateFile not found in path"
    assert isinstance(jchostgsheet, str), "Argument must be string"

    args = grabInputArgs()  # import cmdline/bash argments

    CurrentDate = dt.datetime.now()  # get current date at time of script run
    # CurrentDate = datetime(2019, 3, 31)

    # Get csv version of google spreadsheet name list
    r = requests.get(jchostgsheet)
    jchosts = pd.read_csv(StringIO(r.text),
                          index_col=0,
                          header=0)  # make pandas array

    # grab local copy of dates to veto
    vetodates = pd.read_csv(vetodateFile,
                            header=0,
                            index_col=False)

    # Compute total number of weeks from start date to now
    absolute_weekcount = (CurrentDate-ListStartDate).days/7

    # grab list of veto dates and count how many to today
    num_skips = np.sum(pd.to_datetime(vetodates.vetodate) <= CurrentDate)

    # phase adj num from google spreadsheet
    phase_adj = jchosts.phase_adj[0]

    # Work out position in list given veto dates and abitrary phase factor
    total_wkcount = (absolute_weekcount - num_skips + phase_adj)

    # compute position in the list with modulo list length
    JCHostListPosition = total_wkcount % jchosts.shape[0]
    JCHostListPosition_next = (total_wkcount + 1) % jchosts.shape[0]

    if args.debug:  # report when in debug mode
        print("Absolute number of weeks = {}".format(absolute_weekcount))
        print("Number of weeks skipped due to holidays = {}".format(num_skips))
        print("Manual adjust week phase  = {}".format(phase_adj))
        print("Listphase = {}".format(total_wkcount % jchosts.shape[0]))
        print("Next person to lead is {}".format(
            jchosts.people[JCHostListPosition]))
        print("Person after that is {}".format(
            jchosts.people[JCHostListPosition_next]))

    # choose alert type and assemble email content accordingly
    if args.weeklyreminder:
        # Now set up email to send to JC list
        sender = 'JournalClubRoboTsar@gmail.com'
        # to = jchosts.email[JCHostListPosition]
        to = 'wadean@gmail.com'
        # cc = (jchosts.email[JCHostListPosition_next] + '; ' +
        #       'JournalClubRoboTsar@gmail.com' + '; ' +
        #       'awade@ligo.caltech.edu')
        cc = ('wadean+JC1@gmail.com' + '; ' +
              'wadean+JC2@gmail.com' + '; ' +
              'awade@ligo.caltech.edu')
        subject = 'Upcoming week: journal club presenters'
        message_text = '''
<p>Journal club this week will be lead by {leadnext}.</p>


<p>The following week {leadnextnext} will lead discussions with a paper.</p>


<p>By Tuesday please choose a paper, reply to this list with a link and post it
 to the 40m wiki here:
 <a href="https://wiki-40m.ligo.caltech.edu/Journal_Club">
 https://wiki-40m.ligo.caltech.edu/Journal_Club<a>.</p>

<p>If you are unable to present a paper, check the Journal club roster and
 negotiate with someone for a swap. The roster can be found here:
<a href="https://docs.google.com/spreadsheets/d/1TxTmFStB9jT1xCvscr5xKY5ovuA4nme58XK4IrqI6_0/edit?usp=sharing">
 LIGO Journal Club Hosts List</a>.</p>
        '''.format(leadnext=jchosts.people[JCHostListPosition],
                   leadnextnext=jchosts.people[JCHostListPosition_next])

        sendEmail(sender=sender, to=to, cc=cc,
                  subject=subject, message_text=message_text,
                  host='smtp.gmail.com', port='587',
                  credentialsFile=credentialsFile, dryrun=args.dryrun)

    if args.dayreminder:
        # Now set up email to send to JC list
        sender = 'JournalClubRoboTsar@gmail.com'
        # to = 'ligo-journal-club@caltech.edu'
        to = 'wadean@gmail.com'
        # cc = (jchosts.email[JCHostListPosition] + '; ' +
        #       jchosts.email[JCHostListPosition_next] + '; ' +
        #       'JournalClubRoboTsar@gmail.com' + '; ' +
        #       'awade@ligo.caltech.edu')
        cc = ("wadean+JC1day@gmail.com" + "; " +
              "wadean+JC2day@gmail.com" + "; " +
              "awade@ligo.caltech.edu")
        subject = 'Reminder: LIGO journal club today 3.00 pm'
        message_text = '''
<p>Just a friendly reminder that journal club is on today at 3.00 pm in the
West Bridge 2nd floor seminar room 265.</p>

<p>{leadnext} will be leading the discussion. Links this week's articles can be
found at: <a href="https://wiki-40m.ligo.caltech.edu/Journal_Club">
https://wiki-40m.ligo.caltech.edu/Journal_Club<a>.</p>

<hr>

<p>This is an automatically generated reminder.</p>
        '''.format(leadnext=jchosts.people[JCHostListPosition],
                   leadnextnext=jchosts.people[JCHostListPosition_next])

        sendEmail(sender=sender, to=to, cc=cc,
                  subject=subject, message_text=message_text,
                  host='smtp.gmail.com', port='587',
                  credentialsFile=credentialsFile, dryrun=args.dryrun)


def sendEmail(sender='', to='', cc='', subject='', message_text='',
              credentialsFile=None, port=None, host=None, dryrun=False):
    '''Function constructs and sends email given varioius parameters. '''

    # Generate MIME formated email message with headers for email
    msg = create_message(sender=sender,
                         to=to,
                         cc=cc,
                         subject=subject,
                         message_text=message_text)

    # Make smpt object using given host and port details else use defaults
    if host is not None:
        if port is not None:
            s = smtplib.SMTP(host, port)
        else:
            s = smtplib.SMTP(host)  # port default to SSL 465
    else:
        s = smtplib.SMTP()  # Case host not given, use localhost
    s.starttls()

    if credentialsFile is not None:
        creds = get_credentials(credentialsFile)
        s.login(creds.usr, creds.passw)

    if dryrun is False:
        s.sendmail(
            sender,
            to + "; " + cc,
            msg.as_string())
    else:
        print("Dry run: executed all steps except final one of sending email.")
        print("Message that would have been sent:")
        print(msg.as_string())
    s.quit()
    return 1


def create_message(sender='', to='', cc='', subject='', message_text=''):
    """Create a MIME structured message for an email. Puts all necessary
       headers together for the email and generates html + plain text versions
       of the emails.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEMultipart('alternative')
    message['to'] = to
    message['cc'] = cc
    message['from'] = sender
    message['subject'] = subject

    plainText = html2text.html2text(message_text)  # make plaintext version
    html = message_text

    part1 = MIMEText(plainText, 'plain')  # included to accommodate pltext req
    part2 = MIMEText(html, 'html')
    message.attach(part1)
    message.attach(part2)
    return message


class get_credentials():
    """ Gets user credentials from secrets file. """
    def __init__(self, credentialsFile):
        """ Generate credential values from file provided. """

        # type and checking, throw assert errors on failure
        assert isinstance(credentialsFile, str), "Argument must be string"
        assert os.path.exists(credentialsFile), "cred File not found in path"

        config = configparser.SafeConfigParser()
        config.read(credentialsFile)

        self.usr = config.get(
            "Credentials",
            "usr")
        self.passw = config.get(
            "Credentials",
            "pass")
        # todo: add more configuration options for authentication and usage


if __name__ == '__main__':  # Make it run, bitch
    main(vetodateFile=vetodateFile,
         jchostgsheet=jchostgsheet,
         ListStartDate=ListStartDate)
