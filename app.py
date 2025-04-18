from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import threading
import cv2
import geocoder
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import logging
import time
import os

app = Flask(__name__)
CORS(app, origins=["https://lucidsight.netlify.app"], supports_credentials=True)
detection_active = False

logging.basicConfig(level=logging.INFO)

# Function to check if the environment is headless (no display)
def is_headless():
    return 'DISPLAY' not in os.environ

def detect_human(method, contact, country_code):
    global detection_active

    # Use default webcam (0 or cv2.CAP_DSHOW) for webcam input
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    if not cap.isOpened():
        logging.error("Unable to access camera")
        return

    while detection_active:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))

        if len(faces) > 0:
            logging.info("Human detected!")

            image_path = "static/intruder.jpg"
            cv2.imwrite(image_path, frame)

            g = geocoder.ip('me')
            location = g.city or "Unknown"

            try:
                if method == 'Email':
                    send_alert_via_email(contact, location, image_path)
                logging.info("Alert sent successfully.")
            except Exception as e:
                logging.error(f"Error sending alert: {e}")
            break

        # Only show the camera feed if not in a headless environment
        if not is_headless():
            cv2.imshow('LucidSight - Human Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    if not is_headless():
        cv2.destroyAllWindows()

def send_alert_via_email(contact, location, image_path):
    message = f"🚨 Alert: Human detected at {location} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    msg = MIMEMultipart()
    msg['Subject'] = 'LucidSight: Intruder Alert'
    msg['From'] = 'sightlucid@gmail.com'
    msg['To'] = contact

    msg.attach(MIMEText(message))

    with open(image_path, 'rb') as img_file:
        img = MIMEImage(img_file.read())
        img.add_header('Content-Disposition', 'attachment', filename="intruder.jpg")
        msg.attach(img)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('sightlucid@gmail.com', os.getenv('EMAILPWD'))  # Use environment variable for password
            server.sendmail(msg['From'], msg['To'], msg.as_string())
        logging.info(f"Email alert sent to {contact}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

# ---------- Flask Routes ----------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_detection', methods=['POST'])
def start_detection():
    global detection_active
    method = request.form['method']
    contact = request.form['contact']
    country_code = request.form.get('country_code', '')

    detection_active = True
    detection_thread = threading.Thread(target=detect_human, args=(method, contact, country_code))
    detection_thread.start()

    return jsonify({"status": "Detection Started"})

@app.route('/stop_detection', methods=['POST'])
def stop_detection():
    global detection_active
    detection_active = False
    return jsonify({"status": "Detection Stopped"})

if __name__ == '__main__':
    app.run(debug=True)
