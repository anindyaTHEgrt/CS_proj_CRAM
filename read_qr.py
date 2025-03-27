import cv2
from pyzbar.pyzbar import decode


def read_qr_from_image(img):

    try:
        decoded_objects = decode(img)

        if not decoded_objects:
            print("No QR code found in the image.")
            return None

        for obj in decoded_objects:
            print(f"QR Code Data: {obj.data.decode('utf-8')}")
            return obj.data.decode('utf-8')

    except Exception as e:
        print(f"Error reading QR code: {e}")
        return None
