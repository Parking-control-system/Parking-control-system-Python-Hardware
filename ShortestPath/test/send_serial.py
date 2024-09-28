import serial
import time

# 송신 포트 설정 (예: /dev/ttys002)
ser = serial.Serial('/dev/ttys043', 9600, timeout=1)

# 데이터 송신
try:
    while True:
        msg = input("Enter message: ")
        ser.write((msg + "\n").encode())
        print("Data sent!")
        time.sleep(1)
except KeyboardInterrupt:
    ser.close()
