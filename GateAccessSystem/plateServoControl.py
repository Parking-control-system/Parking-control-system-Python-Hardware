import os
import tkinter as tk
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
import easyocr
import torch
import serial
import time
import Jetson.GPIO as GPIO
import subprocess
import threading

# UART 설정
uart_port = "/dev/ttyTHS1"
uart_baudrate = 9600
uart_timeout = 1
uart = serial.Serial(uart_port, baudrate=uart_baudrate, timeout=uart_timeout)

# YOLOv8 모델 로드
engine_path = "/ocryolo/best.engine"
model = YOLO(engine_path)

cap = cv2.VideoCapture(0)
recognizer_model_path = '/ocryolo/custom.pth'
reader = easyocr.Reader(['ko'], recognizer=recognizer_model_path)

zone_x1, zone_y1 = 0, 0
zone_x2, zone_y2 = 640, 480
frame_count = 0

# Tkinter 윈도우 생성
root = tk.Tk()
label = tk.Label(root)
label.pack()

# Set up GPIO pins for servo
servo_pin = 32  # PWM-capable pin for servo motor
GPIO.setmode(GPIO.BOARD)
GPIO.setup(servo_pin, GPIO.OUT)

# Configure PWM on servo
servo = GPIO.PWM(servo_pin, 50)  # 50Hz for servo motor
servo.start(0)

# 서보 각도 설정 함수
def set_servo_angle(angle):
    duty_cycle = 2 + (angle / 18)
    servo.ChangeDutyCycle(duty_cycle)
    time.sleep(0.5)
    servo.ChangeDutyCycle(0)

# 현재 각도 초기화
current_angle = 90  # 90도로 초기 위치 설정
set_servo_angle(current_angle)  # 초기 위치로 설정

def control_servo():
    global current_angle
    target_angle = 180  # 위로 이동할 목표 각도

    # 서보를 135도로 이동
    set_servo_angle(target_angle)
    print("모터를 135도로 이동하여 위로 올립니다.")
    time.sleep(5)  # 5초 대기

    # 서보를 다시 90도로 복귀
    set_servo_angle(90)
    current_angle = 90  # 현재 각도를 90도로 업데이트
    print("모터가 90도로 돌아옵니다.")

last_recognized_plate = None
last_recognized_time = 0
block_time = 15

def show_frame():
    global frame_count, last_recognized_plate, last_recognized_time
    ret, frame = cap.read()
    if not ret:
        return

    frame = cv2.resize(frame, (640, 480))
    frame_count += 1

    cv2.rectangle(frame, (zone_x1, zone_y1), (zone_x2, zone_y2), (255, 0, 0), 2)

    if frame_count % 3 == 0:
        results = model(frame)
        for result in results:
            for box in result.boxes:
                xyxy = box.xyxy[0].cpu().numpy().astype(int)
                conf = box.conf[0].cpu().numpy()

                if conf > 0.5:
                    x1, y1, x2, y2 = xyxy
                    if (x1 >= zone_x1 and x2 <= zone_x2 and y1 >= zone_y1 and y2 <= zone_y2):
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                        plate_texts = reader.readtext(frame[y1:y2, x1:x2])

                        if plate_texts:
                            plate_text_build = "".join([c[1] for c in plate_texts if c[1].strip()])
                            filtered_plate_text = "".join(filter(str.isdigit, plate_text_build))
                            if filtered_plate_text:
                                cv2.putText(frame, filtered_plate_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                                print(f"인식된 숫자: {filtered_plate_text}")

                                if len(filtered_plate_text) == 4:
                                    print(f"인식된 번호 {filtered_plate_text}가 4글자 숫자입니다.")

                                    current_time = time.time()

                                    if filtered_plate_text != last_recognized_plate or (current_time - last_recognized_time) > block_time:
                                        last_recognized_plate = filtered_plate_text
                                        last_recognized_time = current_time

                                        servo_thread = threading.Thread(target=control_servo)
                                        servo_thread.start()

                                        uart.write((filtered_plate_text + '\n').encode('utf-8'))
                                        time.sleep(5)
                                    else:
                                        print(f"{block_time}초 이내에 같은 번호가 재인식됨. 무시.")
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    imgtk = ImageTk.PhotoImage(image=img)

    label.imgtk = imgtk
    label.configure(image=imgtk)

    root.after(1, show_frame)

show_frame()
root.mainloop()

cap.release()
cv2.destroyAllWindows()
uart.close()
servo.stop()
GPIO.cleanup()
