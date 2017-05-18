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

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


## Test flags these will be replaced with python option flags
debug = 1
dryrun = 1


phaseAdj = 0 # Add and arbitrary phase shift (integer) to offset additions/subtractions from the list


def main():
    # Load names and dates to veto
    jchosts = pd.read_csv('jchosts.csv', header=0, index_col=False)
    vetodates = pd.read_csv('vetodates.csv', header=0, index_col=False)

    #TODO: change to dt.datetime.now()
    ListStartDate = datetime(2017, 1, 1)
    CurrentDate = datetime(2017,7,16) # Dummy test date

    AbsolutePhase = (CurrentDate-ListStartDate).days/7
    NumSkips = np.sum(pd.to_datetime(vetodates.vetodate)<= CurrentDate)

    # Workout total weeks start date, ommitting skips and adding manual phase adjust then modulo against length of list of people
    Listphase = (AbsolutePhase - NumSkips + phaseAdj) % (jchosts.shape[0]-1)


    if debug == 1:
        print("Absolute phase = {}".format(AbsolutePhase))
        print("Number of weeks skipped due to holidays = {}".format(NumSkips))
        print("Manual adjust twiddle factor  = {}".format(phaseAdj))

        # print("Dates that are vetoed:")
        # print(vetodates)

    print(Listphase)

    print(jchosts['people'][Listphase])

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)


    # Now set up email to send to JC list
    sender = 'JournalClubRoboTsar@gmail.com'
    to = 'wadean@gmail.com'
    cc = (jchosts['email'][Listphase] + "; " + jchosts['email'][Listphase+ 1] + "; " + "awade@ligo.caltech.edu")
    subject = 'Upcoming week: journal club presenters'
    message_text = """
    Journal club this week will be lead by {leadnext}.
    
    The following week {leadnextnext} will lead discussions with a paper.
    
    Please choose a paper, reply to this list with a link and post it to the 40m wiki here: https://wiki-40m.ligo.caltech.edu/Journal_Club
    
    If you are unable to present a paper, check the Journal club roster at the above link and negogiate with someone for a swap. Reply to this list with the change so that the list order can be updated.
    """.format(leadnext=jchosts['people'][Listphase],leadnextnext=jchosts['people'][Listphase+1])
    userId_set = 'me'

    # Make the message
    # mkMessage = create_message(msgsender, tousr, cc, msgsubject, message_text)
    mkMessage = create_message(sender, to, cc, subject, message_text)
    # Send the message
    send_message(service,"me",mkMessage)




# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'JCTsar'


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

