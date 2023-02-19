/******
*    name: Qubes PAM distress login (GMAIL)
*    date: 19 February 2023
*    NOTES:
*    see https://github.com/kennethrrosen/ for license and contact.
******/

import smtplib
import getpass
import pam

# Set up the SMTP server
server = smtplib.SMTP('smtp.protonmail.com', 587)
server.starttls()

# Prompt the user for their login credentials
username = input('Enter your username: ')
password = getpass.getpass('Enter your password: ')

# Set up the PAM service
service = 'login'

# Authenticate the user
if pam.authenticate(username, password, service):
    # Prompt the user for the passphrase
    passphrase = getpass.getpass('Enter the passphrase: ')

    # Check if the passphrase is correct
    if passphrase == 'password123':
        # Send the distress email
        recipients = ['email1@example.com', 'email2@example.com']
        subject = 'Distress signal'
        body = 'I am in need of assistance. Please help.'
        message = 'Subject: {}\n\n{}'.format(subject, body)

        # Log in to the ProtonMail SMTP server
        pm_username = 'your-email-address@protonmail.com'
        pm_password = 'your-protonmail-password'
        server.login(pm_username, pm_password)

        # Send the email
        server.sendmail(pm_username, recipients, message)

        # Disconnect from the server
        server.quit()
    else:
        print('Incorrect passphrase')
else:
    print('Incorrect username or password')
