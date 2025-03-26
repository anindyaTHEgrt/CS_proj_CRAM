import cv2
from pyzbar.pyzbar import decode


def read_qr_from_image(file_path):
    """Read QR code from an image file"""
    try:
        # Read the image
        img = cv2.imread(file_path)

        # Decode QR code
        decoded_objects = decode(img)

        if not decoded_objects:
            print("No QR code found in the image.")
            return None

        # Extract and return data
        for obj in decoded_objects:
            print(f"QR Code Data: {obj.data.decode('utf-8')}")
            return obj.data.decode('utf-8')

    except Exception as e:
        print(f"Error reading QR code: {e}")
        return None


# Example usage
if __name__ == "__main__":
    file_path = "qr.png"  # Replace with your QR image path
    qr_data = read_qr_from_image(file_path)
    if qr_data:
        print(f"Extracted Data: {qr_data}")