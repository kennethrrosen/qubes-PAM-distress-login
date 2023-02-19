# qubes-PAM-distress-login
A simple setup for sending a distress email if forced to login to desktop beyond LUKS passwords

here is a step-by-step guide to set up a system service in Qubes OS to send a distress email on boot using ProtonMail's SMTP server. The service will run silently in dom0, and will start an AppVM to send the email. The guide assumes you are using Qubes OS 4.x.

1. Create a new AppVM for email, or use an existing one. For this guide, let's call it `emailvm`.

2. Install the `pam` and `smtplib` Python libraries in `emailvm`. Open a terminal in `emailvm` and run the following command:
```
sudo pip install pam smtplib
```

3. Modify the Python script in this repo to include the ProtonMail SMTP server and your login credentials. Open a text editor in the `emailvm` and create a new file for the script. Replace your-email-address@protonmail.com and your-protonmail-password with your actual ProtonMail email address and password.

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

After the system reboots, the send_distress_email service will run automatically in the background, start the emailvm, and run the Python script to send the distress email. To make sure that the system service runs even when the screen is locked, you can add a script to xScreenSaver that prevents the screen from locking during the boot process. Open a terminal in dom0 and run the following commands:

```
sudo mkdir /etc/xscreensaver
echo "mode: off" | sudo tee /etc/xscreensaver/disabled
```

This creates a new directory for xScreenSaver and adds a configuration file that disables the screen locking.
