#!/usr/bin/env python

# Script broadly based on python documnetation standard vanilla first examples

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



#Configure SMTP settings

HOST = "smtp.gmail.com"
PORT = "587"
USR = "JournalClubRoboTsar@gmail.com"
PSSSWD = "" # This is temp measure until seperate key file can be enacted drawn from local dir





# Some intial test values for email addresses
me = "JournalClubRoboTsar@gmail.com"
you = "wadean@gmail.com"



def main():

    # # Now generate the body content of the email
    # text = "Hi anon!\n This is a first message with some line breaks.\n \n And here is the rest of the message.\n You are welcome."
    # html = """\
    # <html>
    #   <head></head>
    #   <body>
    #     <p>Hi anon!<br>
    #        This is a first message with some line breaks.<br>
    #        This version is the HTML formatted message
    #         Here is a cool link: <a href="https://www.python.org">link</a>.
    #     </p>
    #   </body>
    # </html>
    # """



    # s = smtplib.SMTP('localhost') # Send the message via local SMTP server.

    # Connect with custom server
    s = smtplib.SMTP()
    s.connect(HOST,PORT)

    s.starttls()
    s.login(USR,PSSSWD)



    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(me, you, msg.as_string())
    s.quit()


def create_message(sender,to,subject,message_text):
    """Create a message for an email, this includes html and plain text versions depending on user preference.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

    Returns:
    An object containing a base64url encoded email object for send.
    """

    # Create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to

    # Quick hack for input text -> html & plaintext no format niceness
    text = message_text
    html = message_text

    # Make MIMText in plain and html to deliver according to user preference format
    msg_plaintext = MIMEText(text, 'plain')
    msg_html = MIMEText(html, 'html')
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(msg_plaintext)
    msg.attach(msg_html)
    return {'raw': base64.urlsafe_b64encode(msg.as_string())}



if __name__ == '__main__':
    main()