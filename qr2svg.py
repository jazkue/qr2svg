import os
import time
import subprocess
import urllib.parse

import cv2
from selenium import webdriver
from pyzbar.pyzbar import decode
import svgwrite

current_dir = os.getcwd()
video_path = "/Users/javierdeazkue/Documents/MAE/tesis/qr.mov"

class Qrbot:
    def __init__(self, use_video=True, skip_interval=1):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--kiosk")
        self.options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.driver = webdriver.Chrome(self.options)

        self.skip_interval = skip_interval
        self.frame_count = 0
        if use_video:
            self.cap = cv2.VideoCapture(video_path)
        else:
            self.cap = cv2.VideoCapture(0)

    def read_qr(self, frame):
        decoded_objs = decode(frame)
        if decoded_objs:
            qr_data = decoded_objs[0].data.decode('utf-8')
            svg_data_url = "data:image/svg+xml;charset=utf-8," + urllib.parse.quote(qr_data)
            self.driver.get(svg_data_url)
            return True
        else:
            blank = "<?xml version='1.0' encoding='ascii'?><svg xmlns='http://www.w3.org/2000/svg' version='1.1' width='1920' height='1200'> <rect width='100%' height='100%' fill='black' /></svg>"
            svg_data_url = "data:image/svg+xml;charset=utf-8," + blank
            self.driver.get(svg_data_url)
            return False

    def release_cap(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def quit(self):
        self.driver.quit()

qrbot = Qrbot(use_video=True, skip_interval=1)
try:
    while True:
        ret, frame = qrbot.cap.read()
        if not ret:
            print("Error: Failed to capture frame")
            break
        
        qrbot.frame_count += 1
        if qrbot.frame_count % qrbot.skip_interval != 0:
            continue
        
        qr_data = qrbot.read_qr(frame)
        print("QR code data:", qr_data)
except KeyboardInterrupt:
    print("Stopping the capture")
    qrbot.release_cap()
    qrbot.quit()
