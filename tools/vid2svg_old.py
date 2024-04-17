import cv2
import os
import time
import subprocess

from selenium import webdriver
import svgwrite

current_dir = os.getcwd()
input_path = os.path.join(current_dir, "input/input.png")
output_path = os.path.join(current_dir, "output/output.svg")
blank_qr = os.path.join(current_dir, "output/blank.svg")

class Qrbot:
    def __init__(self, capture):
        self.driver = webdriver.Firefox()
        self.capture = capture
        if self.capture:
            self.cap = cv2.VideoCapture(0)
    
    def quit(self):
        self.driver.quit()
    def open_svg(self, svg_path):
        self.driver.get("file:///{}".format(svg_path))
    
    def refresh_svg(self):
        self.driver.refresh()

    def capture_image(self):
        if not self.capture:
            return
        
        # Create a directory to save the images if it doesn't exist
        output_dir = os.path.join(current_dir, "input")
        os.makedirs(output_dir, exist_ok=True)

        # Check if the webcam is opened successfully
        if not self.cap.isOpened():
            print("Error: Could not open webcam")
            exit()

        ret, frame = self.cap.read()
        if not ret:
            print("Error: Failed to capture frame")
            return

        # Save the frame to the same file each time
        filename = os.path.join(output_dir, "input.png")
        success = cv2.imwrite(filename, frame)
        # time.sleep(1)
        return success
    
    def release_cam(self):
        # Release the webcam and close the output file
        self.cap.release()
        cv2.destroyAllWindows()

    def read_qr(self, input):
        try:
            # Execute zbarimg command to extract QR code data
            commands = ["zbarimg", "--nodbus", "--raw", "-Sbinary", input]
            result1 = subprocess.run(commands, capture_output=True, text=True, check=True)
            # Write the output to the output file
            with open(output_path, "w") as f:
                f.write(result1.stdout)

            print("QR code data successfully written to", output_path)
            return True

        except subprocess.CalledProcessError as e:
            # Handle errors
            print("Error:", e)
            print("Command stderr:", e.stderr)
            return False

    def write_blank(self):
        blank_path = os.path.join(current_dir, "output/output.svg")
        blank = svgwrite.Drawing(filename=blank_path)
        blank.save()


qrbot = Qrbot(capture=False)
if not os.path.exists(output_path):
    qrbot.write_blank()
qrbot.open_svg(output_path)

try:
    while True:
        qrbot.capture_image()
        qr_true = qrbot.read_qr(input_path)
        print(qr_true)
        if not qr_true:
            qrbot.write_blank()
        qrbot.refresh_svg()
except KeyboardInterrupt:
    print("Stopping the capture")
    qrbot.release_cam()
    qrbot.quit()