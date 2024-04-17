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
video_path = "/Users/javierdeazkue/Documents/MAE/tesis/qr_test_black.mp4"

class Preserbot:
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

preserbot = Preserbot(capture=True, skip_interval=10)
preserbot.write_blank()
preserbot.open_svg(output_path)

try:
    while True:
        ret, frame = preserbot.cap.read()
        if not ret:
            preserbot.cap.release()
            preserbot.cap = cv2.VideoCapture(video_path)
            continue
        
        preserbot.frame_count += 1
        if preserbot.frame_count % preserbot.skip_interval != 0:
            continue
        
        qr_data = preserbot.read_qr(frame)
        print("QR code data:", qr_data)
        
        preserbot.refresh_svg()

except KeyboardInterrupt:
    print("Stopping the capture")
    preserbot.release_cap()
    preserbot.quit()
