import os
import time
import subprocess

import cv2
from selenium import webdriver
from pyzbar.pyzbar import decode
import svgwrite

current_dir = os.getcwd()
output_path = os.path.join(current_dir, "output/output.svg")
blank_qr = os.path.join(current_dir, "output/blank.svg")
video_path = "/Users/javierdeazkue/Documents/MAE/tesis/qr_white.mp4"

class Qrbot:
    def __init__(self, capture, skip_interval=1):
        self.driver = webdriver.Firefox()
        self.capture = capture
        self.skip_interval = skip_interval
        self.frame_count = 0
        if self.capture:
            self.cap = cv2.VideoCapture(video_path)
    
    def open_svg(self, svg_path):
        self.driver.get("file:///{}".format(svg_path))

    def read_qr(self, frame):
        decoded_objs = decode(frame)
        if decoded_objs:
            qr_data = decoded_objs[0].data.decode('utf-8')
            with open(output_path, "w") as f:
                f.write(qr_data)
            return True
        return False
    
    def refresh_svg(self):
        self.driver.refresh()
    
    def write_blank(self):
        blank_path = os.path.join(current_dir, "output/output.svg")
        blank = svgwrite.Drawing(filename=blank_path)
        blank.save()

    def release_cap(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def quit(self):
        self.driver.quit()

qrbot = Qrbot(capture=True, skip_interval=10)
qrbot.write_blank()
qrbot.open_svg(output_path)

try:
    while True:
        ret, frame = qrbot.cap.read()
        if not ret:
            qrbot.cap.release()
            qrbot.cap = cv2.VideoCapture(video_path)
            continue
        
        qrbot.frame_count += 1
        if qrbot.frame_count % qrbot.skip_interval != 0:
            continue
        
        qr_data = qrbot.read_qr(frame)
        print("QR code data:", qr_data)
        
        qrbot.refresh_svg()

except KeyboardInterrupt:
    print("Stopping the capture")
    qrbot.release_cap()
    qrbot.quit()
