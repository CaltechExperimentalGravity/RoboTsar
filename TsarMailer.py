from __future__ import print_function
import httplib2
import os
from datetime import datetime
import datetime as dt

#Import packages used for email sending
from apiclient import discovery
from apiclient import errors

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import base64
from email.mime.text import MIMEText

import pandas as pd # Tools for opening csv files
import numpy as np

from StringIO import StringIO
import requests

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


# Flags for debug and disabling the actual email send
debug = 1
dryrun = 0

jchostgsheet = 'https://docs.google.com/spreadsheets/d/1TxTmFStB9jT1xCvscr5xKY5ovuA4nme58XK4IrqI6_0/pub?gid=0&single=true&output=csv'

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'JCTsar'


def main():
    r = requests.get(jchostgsheet)  # Grab csv version of google spreadsheet name list
    jchosts = pd.read_csv(StringIO(r.text), index_col=0, header=0)  # refactor into pandas array

    vetodates = pd.read_csv('vetodates.csv', header=0, index_col=False)  # grab local copy of dates to veto

    phase_adj = jchosts.phase_adj[0]  # grab phase adjust factor from google spreadsheet

    ListStartDate = datetime(2017, 1, 1)  # set reference start date to value
    CurrentDate = dt.datetime.now()  # get current date as of today
    # CurrentDate = datetime(2017,5,18) #dummy debug date uncomment for testing
    absolute_weekcount = (CurrentDate-ListStartDate).days/7  # compute total number of weeks from start date to now
    num_skips = np.sum(pd.to_datetime(vetodates.vetodate)<= CurrentDate)  # take list of veto dates and count how many to today

    total_wkcount = (absolute_weekcount - num_skips + phase_adj) # Work out total number of weeks, less holidays and an abitrary phase factor

    if debug == 1:
        print("Absolute number of weeks = {}".format(absolute_weekcount))
        print("Number of weeks skipped due to holidays = {}".format(num_skips))
        print("Manual adjust week phase  = {}".format(phase_adj))
        print("Listphase = {}".format(total_wkcount % jchosts.shape[0]))
        print("Next person to lead is {}".format(jchosts.people[total_wkcount % (jchosts.shape[0])]))
        print("Person after that is {}".format(jchosts.people[(total_wkcount +1) % (jchosts.shape[0])]))

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)


    # Now set up email to send to JC list
    sender = 'JournalClubRoboTsar@gmail.com'
    to = 'ligo-journal-club@caltech.edu'
    # cc = ''
    cc = (jchosts.email[total_wkcount % jchosts.shape[0]] + "; " + jchosts.email[(total_wkcount+ 1) % jchosts.shape[0]] + "; " + "awade@ligo.caltech.edu")
    subject = 'Upcoming week: journal club presenters'
    message_text = """
Journal club this week will be lead by {leadnext}.

The following week {leadnextnext} will lead discussions with a paper.

By Tuesday please choose a paper, reply to this list with a link and post it to the 40m wiki here: https://wiki-40m.ligo.caltech.edu/Journal_Club

If you are unable to present a paper, check the Journal club roster and negotiate with someone for a swap. The roster can be found here: https://docs.google.com/spreadsheets/d/1TxTmFStB9jT1xCvscr5xKY5ovuA4nme58XK4IrqI6_0/edit?usp=sharing
    """.format(leadnext=jchosts.people[total_wkcount % (jchosts.shape[0])],leadnextnext=jchosts.people[(total_wkcount+1) % (jchosts.shape[0])])
    userId_set = 'me'


    mkMessage = create_message(sender, to, cc, subject, message_text)  # Make the message
    send_message(service,"me",mkMessage) # Send the message


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,'gmail-python-quickstart.json')


    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def create_message(sender, to, cc, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text)
  message['to'] = to
  message['cc'] = cc
  message['from'] = sender
  message['subject'] = subject

  if debug == 1:
      print('')
      print('--- Message to send ---')
      print(message)
      print('--- End message ---')
      print('')

  return {'raw': base64.urlsafe_b64encode(message.as_string())}


def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """

  if dryrun == 0:
      try:
          message = (service.users().messages().send(userId=user_id, body=message).execute())
          print('Message Id: %s' % message['id'])
          return message

      except errors.HttpError, error:
          print('An error occurred: %s' % error)

  elif dryrun == 1:
      print('No message sent')


if __name__ == '__main__': # Make it run, bitch
    main()

