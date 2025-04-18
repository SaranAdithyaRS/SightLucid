import cv2
import pywhatkit as kit
import geocoder
import time
from datetime import datetime

# Dummy function to simulate human detection
def detect_human(method, contact, country_code):
    # OpenCV for real-time webcam feed and human detection
    cap = cv2.VideoCapture(0)  # Using the default camera

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to grayscale for easier human detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # If faces are detected, alert the user
        if len(faces) > 0:
            print("Human detected!")

            # Get the user's location
            g = geocoder.ip('me')
            location = g.city

            # Send alert based on the selected method
            if method == 'WhatsApp':
                send_alert_via_whatsapp(contact, country_code, location)
            elif method == 'Email':
                send_alert_via_email(contact, location)
            
            break  # For demo purposes, stop detection after one detection (you can modify this)

        # Display the frame (for debugging purposes)
        cv2.imshow('LucidSight - Human Detection', frame)

        # Break if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

def send_alert_via_whatsapp(contact, country_code, location):
    # Send WhatsApp alert using pywhatkit
    message = f"Alert: Human detected at {location} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    phone_number = f"+{country_code}{contact}"
    kit.sendwhatmsg_instantly(phone_number, message)
    print(f"Sent WhatsApp alert to {phone_number}")

def send_alert_via_email(contact, location):
    # Send Email alert (using Python's built-in smtplib)
    import smtplib
    from email.mime.text import MIMEText

    message = f"Alert: Human detected at {location} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    msg = MIMEText(message)
    msg['Subject'] = 'LucidSight: Intruder Alert'
    msg['From'] = 'sightlucid@gmail.com'
    msg['To'] = contact

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('sightlucid@gmail.com', 'prfh ywjc uvea uaeh')  # Use app password if using Gmail
        server.sendmail('sightlucid@gmail.com', contact, msg.as_string())

    print(f"Sent email alert to {contact}")
