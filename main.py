import cv2 as cv
from datetime import datetime
import time
import glob
import os, shutil
from emailing import send_email
from threading import Thread

video = cv.VideoCapture(0)
time.sleep(1)

first_frame = None
status_list = []
count = 1
prev_object_count = 1

directory = "images"
parent_dir = os.getcwd()
images_path = os.path.join(parent_dir, directory)
if os.path.exists(images_path):
    shutil.rmtree(images_path)
os.makedirs(images_path, exist_ok=True)

while True:
    check, frame = video.read()

    now = datetime.now()
    cv.putText(img=frame, text=now.strftime("%A"), org=(30, 50), \
               fontFace=cv.FONT_HERSHEY_PLAIN ,fontScale=2,  color=(255, 255, 255), thickness=2)
    cv.putText(img=frame, text=now.strftime("%H:%M:%S"), org=(30, 90), \
               fontFace=cv.FONT_HERSHEY_PLAIN ,fontScale=2,  color=(0, 255, 0), thickness=2)
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    gray_frame_gau = cv.GaussianBlur(gray_frame, (21, 21), 0)

    if first_frame is None:
        first_frame = gray_frame_gau
    status = 0
    delta_frame = cv.absdiff(first_frame, gray_frame_gau)
    threshold_frame = cv.threshold(delta_frame, 60, 255, cv.THRESH_BINARY)[1]
    dil_frame = cv.dilate(threshold_frame, None, iterations=2)
    contours, check = cv.findContours(dil_frame, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv.contourArea(contour) < 10000:
            continue
        x, y, w, h = cv.boundingRect(contour)
        rectangle = cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        if rectangle.any():
            status = 1
            cv.imwrite(f"images/{count}.png", frame)
            count += 1
            

    status_list.append(status)
    status_list = status_list[-2:]
    if status_list[0]==1 and status_list[1]==0:
        all_images = glob.glob("images/*.png")
        index = prev_object_count+int((len(all_images)-prev_object_count)/3)
        image_path = f"images/{index}.png"
        
        email_thread = Thread(target=send_email, args=(image_path,))
        email_thread.daemon = True
        email_thread.start()
        # send_email(image_path)
        prev_object_count = count

    cv.imshow("My Video", frame)
    key = cv.waitKey(1)

    if key == ord("q"):
        break

video.release()
