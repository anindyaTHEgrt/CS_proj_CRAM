import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import qrcode
import random
import string
from datetime import datetime, timedelta
from email_config import EMAIL_CONFIG
import pyotp


class OTPSender:
    def __init__(self):
        self.otp_expiry_minutes = 5
        self.otp_length = 6

    def generate_otp(self):
        """Generate a random OTP"""
        # Using pyotp for time-based OTP
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret, digits=self.otp_length, interval=self.otp_expiry_minutes * 60)
        otp = totp.now()
        print(otp)
        return otp, datetime.now() + timedelta(minutes=self.otp_expiry_minutes)

    def generate_qr_code(self, otp, filename='otp_qr.png'):
        """Generate QR code with the OTP"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(otp)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)
        return filename

    def send_otp_email(self, recipient_email):
        """Send OTP via email with QR code"""
        # Generate OTP
        otp, expiry_time = self.generate_otp()

        # Generate QR code
        qr_filename = self.generate_qr_code(otp)

        # Create email message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['SENDER_EMAIL']
        msg['To'] = recipient_email
        msg['Subject'] = 'Your One-Time Password (OTP)'

        # Attach HTML body
        with open('templates/otp_email.html', 'r') as file:
            html_content = file.read()
        msg.attach(MIMEText(html_content, 'html'))

        # Attach QR code image
        with open(qr_filename, 'rb') as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', '<qr_code>')
            img.add_header('Content-Disposition', 'inline', filename='otp_qr.png')
            msg.attach(img)

        # Send email
        try:
            with smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT']) as server:
                if EMAIL_CONFIG['USE_TLS']:
                    server.starttls()
                server.login(EMAIL_CONFIG['SMTP_USERNAME'], EMAIL_CONFIG['SMTP_PASSWORD'])
                server.send_message(msg)

            print(f"OTP sent to {recipient_email}")
            return True, "OTP sent successfully"
        except Exception as e:
            print(f"Failed to send OTP: {e}")
            return False, str(e)
        finally:
            # Clean up QR code file
            if os.path.exists(qr_filename):
                os.remove(qr_filename)


if __name__ == "__main__":
    sender = OTPSender()
    email = input("Enter recipient email: ")
    success, message = sender.send_otp_email(email)
    if success:
        print("OTP sent successfully!")
    else:
        print(f"Failed to send OTP: {message}")