import tkinter as tk
from tkinter import messagebox
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import cv2
import numpy as np
import torch
from time import time
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

class EmailConfig:
    def __init__(self):
        self.password = "yjer ghzz mcfh dwka"
        self.from_email = ""  # Must match the email used to generate the password
        self.to_email = ""  # Receiver email
        self.server = smtplib.SMTP('smtp.gmail.com: 587')
        self.server.starttls()
        self.server.login(self.from_email, self.password)

    def send_email(self, to_email, from_email, image):
        message = MIMEMultipart()
        message['From'] = from_email
        message['To'] = to_email
        message['Subject'] = "Security Alert"

        # Add message body
        message_body = 'ALERT - Weapon detected!!'
        message.attach(MIMEText(message_body, 'plain'))

        # Attach the image to the email
        _, img_encoded = cv2.imencode('.jpg', image)
        attachment = MIMEImage(img_encoded.tobytes(), 'jpg')
        message.attach(attachment)

        # Send the email
        self.server.sendmail(from_email, to_email, message.as_string())
        self.server.quit()  # Quit the server after sending the email

class ObjectDetection:
    def __init__(self, camera_url, to_email, from_email):
        # Default parameters
        self.camera_url = camera_url
        self.to_email = to_email
        self.from_email = from_email
        self.email_sent = False

        # Model information
        self.model = YOLO(r"C:\Users\hp\Downloads\best.pt")

        # Visual information
        self.annotator = None
        self.start_time = 0
        self.end_time = 0

        # Device information
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def predict(self, im0):
        results = self.model(im0)
        return results

    def display_fps(self, im0):
        self.end_time = time()
        fps = 1 / np.round(self.end_time - self.start_time, 2)
        text = f'FPS: {int(fps)}'
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
        gap = 10
        cv2.rectangle(im0, (20 - gap, 70 - text_size[1] - gap), (20 + text_size[0] + gap, 70 + gap), (255, 255, 255), -1)
        cv2.putText(im0, text, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

    def plot_bboxes(self, results, im0):
        class_ids = []
        self.annotator = Annotator(im0, 3, results[0].names)
        boxes = results[0].boxes.xyxy.cpu()
        clss = results[0].boxes.cls.cpu().tolist()
        names = results[0].names
        for box, cls in zip(boxes, clss):
            class_ids.append(cls)
            self.annotator.box_label(box, label=names[int(cls)], color=colors(int(cls), True))
        return im0, class_ids

    def __call__(self):
        cap = cv2.VideoCapture(self.camera_url)
        assert cap.isOpened()
        frame_count = 0
        while True:
            self.start_time = time()
            ret, im0 = cap.read()
            assert ret
            results = self.predict(im0)
            im0, class_ids = self.plot_bboxes(results, im0)

            if len(class_ids) > 0:  # Only send email if not sent before
                if not self.email_sent:
                    email_config = EmailConfig()
                    email_config.send_email(self.to_email, self.from_email, im0)
                    self.email_sent = True
            else:
                self.email_sent = False

            self.display_fps(im0)
            cv2.imshow('YOLOv8 Detection', im0)
            frame_count += 1
            if cv2.waitKey(5) & 0xFF == 27:
                break
        cap.release()
        cv2.destroyAllWindows()

class CameraApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Camera IP Input")
        self.root.geometry("400x200")  # Larger window size
        self.root.configure(bg="#f0f0f0")
        self.label = tk.Label(self.root, text="For Camera Access:", font=("Helvetica", 12), bg="#f0f0f0")
        self.label.pack(pady=10)  # Increased padding
        self.entry = tk.Entry(self.root, font=("Helvetica", 12), width=30)  # Increased width
        self.entry.pack(pady=10)  # Increased padding
        self.submit_button = tk.Button(self.root, text="Start Detection", font=("Helvetica", 12), bg="#4CAF50", fg="white", command=self.start_detection)
        self.submit_button.pack(pady=10)  # Increased padding

    def start_detection(self):
        camera_url = self.entry.get()
        if not camera_url:
            messagebox.showerror("Error", "Please enter a valid camera URL.")
            return
        to_email = "chauhanvanshita53@gmail.com"  # Receiver email
        from_email = "amazingai86@gmail.com"  # Sender email
        detector = ObjectDetection(camera_url, to_email, from_email)
        detector()
        self.root.destroy()

def main():
    app = CameraApp()
    app.root.mainloop()

if __name__ == "__main__":
    main()