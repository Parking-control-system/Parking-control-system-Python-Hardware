# 젯슨 나노로부터 UART 통신을 이용하여 차량 번호를 수신

import serial
import time
import platform

def get_car_number(car_number_data_queue, serial_port):
    """젯슨 나노로부터 UART 통신을 이용하여 차량 번호를 수신하는 함수"""
    # 젯슨 나노와 UART 통신 설정
    if platform.system() == "Linux":
        ser = serial.Serial(serial_port, 9600, timeout=1)

    while True:
    
        # 젯슨 나노로부터 차량 번호 수신
        if platform.system() == "Linux":
            car_number = ser.readline().decode().strip()
            print("uart = ", repr(car_number))
        
            if car_number != "" and car_number != "[]" and len(car_number.strip()) == 4:
                print("uart send = ", car_number)
                print("uart send repr = ", repr(car_number))
                car_number_data_queue.put(car_number)  # 데이터 큐에 넣기

        time.sleep(1)

if __name__ == "__main__":
    ser = serial.Serial('/dev/ttys044', 9600, timeout=1)

    while True:
        data = ser.readline().decode().strip()

        print(data)