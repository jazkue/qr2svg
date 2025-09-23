import os
import re
import sys
import time
import urllib.parse
import numpy as np
import pyboof as pb
import cv2
from selenium import webdriver

current_dir = os.getcwd()
video_path = None  # Using camera

class QR_Extractor:
    def __init__(self):
        self.detector = pb.FactoryFiducial(np.uint8).qrcode()
    
    def extract(self, img):
        image = pb.ndarray_to_boof(img)
        self.detector.detect(image)
        qr_codes = []
        for qr in self.detector.detections:
            qr_codes.append({
                'text': qr.message,
                'points': qr.bounds.convert_tuple()
            })
        return qr_codes

class Capture:
    def __init__(self, skip_interval=0):
        self.frame_count = 0
        self.skip_interval = skip_interval
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Failed to open camera")
            sys.exit(1)

    def read(self):
        ret, frame = self.cap.read()
        if ret:
            return frame

    def skip(self):
        if self.skip_interval:
            self.frame_count += 1
            if self.frame_count % self.skip_interval != 0:
                return True

    def contrast(self, frame, brightness=0, contrast=1):
        return cv2.addWeighted(frame, contrast, np.zeros(frame.shape, frame.dtype), 0, brightness)

    def desaturate(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def show_preview(self, frame):
        try:
            cv2.imshow('Preview', frame)
            cv2.waitKey(1)
        except Exception as e:
            print("Error in displaying preview:", e)

    def release_cap(self):
        self.cap.release()
        cv2.destroyAllWindows()

class Qrbot:
    def __init__(self, show_text=False):
        self.qr_scanner = QR_Extractor()
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--kiosk")
        self.options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.driver = webdriver.Chrome(self.options)
        self.buffer = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 384 240'><path d='M0 0h384v240H0z'/></svg>"
        self.new_opacity = 0.0
        self.show_text = show_text
        self.last_qr_text = None  # Track last QR content

        # Prepare static HTML page with container for dynamic SVG updates
        html_template = f"""
        <html><body style='margin:0; background:black;'>
        <div id='qr_container'>
        <div style="opacity:0;">{self.buffer}</div>
        </div>
        </body></html>
        """
        self.driver.get("data:text/html," + urllib.parse.quote(html_template))

        if self.show_text:
            self.svg_name = ''
            self.svg_text = ''
            self.text_format = '<text x="6" y="10" fill="rgb(255,255,255)" font-size="5" font-family="Arial">'
            self.svg_no_qr = self.text_format + "QR Code: False" + '</text>'

    def read_qr(self, frame):
        decoded_objs = self.qr_scanner.extract(frame)

        if decoded_objs:
            decoded, = decoded_objs
            qr_data = decoded["text"]

            # Always reset opacity if QR detected
            self.new_opacity = 1.0

            # Update buffer only if content changed
            if qr_data != self.last_qr_text:
                self.last_qr_text = qr_data

                if self.show_text:
                    pattern = r'<!--\s*(\w+\.svg)'
                    match = re.search(pattern, qr_data)
                    if match:
                        self.svg_name = match.group(1)
                        self.svg_text = f'{self.text_format}{self.svg_name}</text>'
                        qr_data = qr_data.replace('</svg>', f'{self.svg_text}</svg>')

                self.buffer = qr_data

        else:
            # Fade-out
            if self.new_opacity > 0:
                self.new_opacity = max(0.0, self.new_opacity - 0.01)  # adjust fade speed

        # Always render with current opacity
        svg_to_render = f'<div style="opacity:{self.new_opacity};">{self.buffer}</div>'
        self.driver.execute_script(
            "document.getElementById('qr_container').innerHTML = arguments[0];",
            svg_to_render
        )

        return bool(decoded_objs)

    def quit(self):
        self.driver.quit()


qrbot = Qrbot(show_text=True)
cap = Capture(skip_interval=0)

try:
    while True:
        frame = cap.read()
        if frame is None:
            # Skip failed frames
            print("Warning: Failed to capture frame, retrying...")
            time.sleep(0.01)
            continue

        if cap.skip():
            continue

        frame = cap.contrast(frame)
        frame = cap.desaturate(frame)
        # cap.show_preview(frame)

        qr_detected = qrbot.read_qr(frame)
        print("QR code detected:", qr_detected)

except KeyboardInterrupt:
    print("Stopping the capture")
    cap.release_cap()
    qrbot.quit()
    sys.exit()
