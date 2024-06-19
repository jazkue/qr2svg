import os
import re
import sys
import urllib.parse
import numpy as np
import pyboof as pb

import cv2
from selenium import webdriver
from pyzbar.pyzbar import decode, ZBarSymbol

current_dir = os.getcwd()
try:
    video_path = sys.argv[1]
except IndexError:
    video_path = None

# pb.init_memmap() #Optional

class QR_Extractor:
    # Src: github.com/lessthanoptimal/PyBoof/blob/master/examples/qrcode_detect.py
    def __init__(self):
        self.detector = pb.FactoryFiducial(np.uint8).qrcode()
    
    def extract(self, img_path):
        # if not os.path.isfile(img_path):
        #     print('File not found:', img_path)
        #     return None
        image = pb.ndarray_to_boof(img_path)

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
        if video_path:
            self.cap = cv2.VideoCapture(video_path)
        else:
            self.cap = cv2.VideoCapture(0)

    def read(self):
        ret, frame = self.cap.read()
        if ret:
            return frame

    def loop(self):
        print("LOOP")
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def skip(self):
        if self.skip_interval:
            self.frame_count += 1
            if self.frame_count % self.skip_interval != 0:
                return True

    def contrast(self, frame, brightness=0, contrast=2):
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
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--kiosk")
        self.options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.driver = webdriver.Chrome(self.options)
        self.buffer = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 384 240'><path d='M0 0h384v240H0z'/></svg>"
        self.qr_scanner = QR_Extractor()

    def read_qr(self, frame):
        # decoded_objs = decode(frame, symbols=[ZBarSymbol.QRCODE])
        decoded_objs = self.qr_scanner.extract(frame)
        if decoded_objs:
            decoded, = decoded_objs
            qr_data = decoded["text"]
            match = re.search(r'<svg.*?>.*?</svg>', qr_data, re.DOTALL)
            if match:
                qr_data = match.group(0).strip()
            else:
                print("Pattern not found, using whole data")
            self.buffer = qr_data
            svg_data_url = "data:image/svg+xml," + urllib.parse.quote(qr_data)
            self.driver.get(svg_data_url)
            return True
        else:
            svg_data_url = "data:image/svg+xml;charset=utf-8," + self.buffer
            self.driver.get(svg_data_url)
            return False
        
    def quit(self):
        self.driver.quit()

qrbot = Qrbot()
cap = Capture(skip_interval=1)

try:
    while True:
        frame = cap.read()
        if frame is None:
            if video_path:
                cap.loop()
                continue
            else:
                print("Error: Failed to capture frame")
                break

        if cap.skip():
            continue

        # frame = cap.contrast(frame)
        frame = cap.desaturate(frame)
        cap.show_preview(frame)

        qr_data = qrbot.read_qr(frame)
        print("QR code data:", qr_data)

except KeyboardInterrupt:
    print("Stopping the capture")
    cap.release_cap()
    qrbot.quit()
    sys.exit()