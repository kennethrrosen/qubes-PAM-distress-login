# qubes-PAM-distress-login
A simple setup for sending a distress email if forced to login to desktop beyond LUKS passwords. Requires VPN or sys-net to connect automatically to a known network, i.e. mobile hotspot or public WiFi, preferably in a disposable sys-net.

In this example we will set up a system service in QubesOS to send a distress email on boot using ProtonMail's SMTP server. The service will run silently in dom0, and will start an AppVM to send the email. The guide assumes you are using Qubes OS 4.1.

1. Create a new AppVM for email, or use an existing one. For this guide, let's call it `emailvm`.

2. Install the `pam` and `smtplib` Python libraries in `emailvm`. Open a terminal in `emailvm` and run the following command:
```
sudo pip install pam smtplib
```

3. Modify the Python script in this repo to include the ProtonMail SMTP server and your login credentials. Open a text editor in the `emailvm` and create a new file for the script. Replace your-email-address@protonmail.com and your-protonmail-password with your actual ProtonMail email address and password (I've also uploaded a version which uses Gmail SMTP instead of ProtonMail SMTP).

4. Save the `qubes-PAM-distress-login` script to a location in `emailvm`, such as /home/user/send_distress_email.py.

5. Test the script by running it manually in the emailvm. Open a terminal in `emailvm` and run the following commands:
```
cd /home/user
python send_distress_email.py
```
Make sure the script runs without errors and sends the email to the specified recipients. Shut down the emailvm.

```
sudo shutdown now
```

7. In dom0, enable then reload the systemctl daemon for the `qubes-gui-agent` service. Open a terminal in dom0 and run the following command:
```
sudo systemctl enable qubes-gui-agent
sudo systemctl daemon-reload
```

8. Create a system service in dom0 that starts the `emailvm` and runs the script automatically on boot. Open a text editor in dom0 and create a new file for the service. Paste the following contents into the file:

```
[Unit]
Description=Send distress email on boot
Requires=qubes-gui-agent.service

[Service]
Type=oneshot
ExecStart=/usr/bin/qvm-start emailvm && sleep 10 && qvm-run -a emailvm /usr/bin/python /home/user/send_distress_email.py

[Install]
WantedBy=multi-user.target
```

Replace `emailvm` with the name of the AppVM you created for email, and replace /home/user/qubes_PAM_distress_login.py with the actual path to the Python script in the `emailvm`. (The sleep 10 command gives the AppVM enough time to start up before running the Python script.)

9. Save the service file to the /etc/systemd/system directory in dom0. Replace /path/to/send_distress_email.service with the actual path to the service file, then set the correct file permissions for the service file. Open a terminal in dom0 and run the following command:
```
sudo mv /path/to/send_distress_email.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/qubes_PAM_distress_login.service
```

10. Enable the system service to start automatically on boot, then reboot the system (this will shutdown your client, so make sure all work is saved). Run the following commands in dom0:
```
sudo systemctl enable send_distress_email.service
sudo shutdown -r now
```

After the system reboots, the send_distress_email service will run automatically in the background, start the emailvm, and run the Python script to send the distress email. To make sure that the system service runs even when the screen is locked, you can add a script to `xScreenSaver` that prevents the screen from locking during the boot process. Open a terminal in dom0 and run the following commands:

```
sudo mkdir /etc/xscreensaver
echo "mode: off" | sudo tee /etc/xscreensaver/disabled
```

This creates a new directory for xScreenSaver and adds a configuration file that disables the screen locking. 

## Plausible Deniability

Note that the password in the Python script is not related to the `xscreensaver` login password. The password in the script is used as a passphrase to trigger the distress email, and it is separate from the login password used to unlock the screen.

If you want to use the same password to unlock `xscreensaver` as well, you can set it up separately in `xscreensaver` for plausible deniability. To do this, open a terminal in dom0:
```
sudo nano /etc/pam.d/xscreensaver
```
Add the following line to the end of the file:
```
auth required pam_unix.so
```
Save the file, exit, then issue the `xscreensaver-demo` command. Click through Advanced>Change Password and enter the same passphrase used in the Python script, then click OK to save.

## Additional thoughts
Note that the password in the Python script is not related to the xscreensaver login password. The password in the script is used as a passphrase to trigger the distress email, and it is separate from the login password used to unlock the screen.

## Enhance login security
If you want to tweak `xscreensaver` further, you can included `pam_tty_audit` and `pam_tally2` to setup a lockout policy, to prevent brute-force attacks, or add monitoring and record authentication events, respectively. The `pam_unix module` is used to authenticate the user's password, and the `pam_tally2` and `pam_tty_audit` modules are added for lockout policy and auditing.

The `pam_tally2` module will deny access after three failed login attempts and will unlock the account after 20 minutes (1200 seconds). The pam_tty_audit module will log all authentication events to the system log.

After you modify the PAM configuration file, you can save the changes and test the modified configuration by locking the screen and entering the password. Make sure that the changes are working as expected and that you can log in successfully.

```
auth required pam_unix.so
auth required pam_tally2.so deny=3 unlock_time=1200 audit
auth required pam_tty_audit.so enable=*
```
## 2FA for xscreensaver
To add two-factor authentication to the PAM script, you can use the `pam_google_authenticator` module, which implements the Time-based One-Time Password (TOTP) algorithm, also in the `/etc/pam.d/xscreensaver` file in dom0. 

To set up two-factor authentication for the xscreensaver login, you can create a new AppVM in Qubes OS and install the google-authenticator-libpam package in the AppVM. Here are the steps you can follow:

1. Create a new AppVM, something like `otpvm`.

2. Start the "otpvm" and open a terminal.

3. Install the `google-authenticator-libpam` package using the package manager (DNF assumes Fedora, so apply to your distro as necessary): 
```
sudo dnf install google-authenticator-libpam
```

4. Run the google-authenticator command in the terminal to generate a secret key and a QR code and scan the QR code with the Google Authenticator app on your phone or another device.

5. Modify the PAM configuration for `xscreensaver` to include `pam_unix` and `pam_google_authenticator`. Open a terminal in dom0 and run the following command to edit the `/etc/pam.d/xscreensaver` file:
```
auth required pam_unix.so
auth required pam_google_authenticator.so
```
6. Save the changes to the file and exit the text editor.

7. In the `xscreensaver-demo` window, set the "Mode" to "One screen with password" and click "Advanced". In the "Advanced" window, set the "Authentication Program" to /usr/bin/xscreensaver-auth, and click "OK" to save the changes.

Lock the screen and enter your username, password, and the one-time code generated by the Google Authenticator app.
