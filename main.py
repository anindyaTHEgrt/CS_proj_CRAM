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
import streamlit as st
from PIL import Image
import read_qr

class OTPSender:
    def __init__(self):
        self.otp_expiry_minutes = 5
        self.otp_length = 6

    def generate_otp(self):

        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret, digits=self.otp_length, interval=self.otp_expiry_minutes * 60)
        otp = totp.now()
        print(otp)
        return otp, datetime.now() + timedelta(minutes=self.otp_expiry_minutes)

    def generate_qr_code(self, otp, filename='otp_qr.png'):

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
        return filename, img

    def send_otp_email(self, recipient_email):

        otp, expiry_time = self.generate_otp()

        # Generate QR code
        qr_filename, img = self.generate_qr_code(otp)

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
            return True, "OTP sent successfully", otp
        except Exception as e:
            print(f"Failed to send OTP: {e}")
            return False, str(e)
        finally:
            # Clean up QR code file
            if os.path.exists(qr_filename):
                os.remove(qr_filename)


st.header('OTP Sender')
rec_email = st.text_input("Enter the email of the recipient.")
sender = OTPSender()
if st.button('Send OTP'):


    with st.spinner("Sending OTP ..."):
        success, message, otp = sender.send_otp_email(rec_email)
    if success:
        st.write(message)
        st.write(f"OTP is: {otp}")
    else:
        st.write(f"Failed to send OTP: {message}")

uploaded_file = st.file_uploader("Upload QR", type=["png", "jpg", "jpeg"])
image = None
if uploaded_file is not None:
    image = Image.open(uploaded_file)

if image is not None:
    st.image(image, caption="Selected QR", use_container_width=True)
    if st.button('Reveal OTP'):
        qr_data= read_qr.read_qr_from_image(image)
        st.write(qr_data)
