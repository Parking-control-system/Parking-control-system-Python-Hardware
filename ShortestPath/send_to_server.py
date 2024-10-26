import socketio
import time
import queue
import json
import serial
import numpy as np
import cv2


# 사각형의 중심 계산 함수
def calculate_center(points):
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    center_x = sum(x_coords) / len(points)
    center_y = sum(y_coords) / len(points)
    return (center_x, center_y)

def transform_to_web_coordinates(zone_id, x, y):
    """주차장 좌표를 웹 좌표로 변환"""
    point = np.array([[[x, y]]], dtype="float32")
    transformed_point = cv2.perspectiveTransform(point, transform_matrices[zone_id])
    return transformed_point[0][0]

# 소켓 지정
sio = socketio.Client(reconnection=True, reconnection_attempts=5, reconnection_delay=2)

@sio.event
def connect():
    print("Connection established")

@sio.event
def disconnect():
    print("Disconnected from server")

def send_to_server(uri, route_data_queue, parking_space_path, walking_space_path, serial_port):
    # 서버 연결
    sio.connect(uri)
    # 시리얼 통신 설정
    ser = serial.Serial(serial_port, 9600, timeout=1)

    # walking_space의 키를 숫자형으로 변환
    with open(walking_space_path,
              "r") as f:
        walking_space = json.load(f)
        walking_space = {int(key): value for key, value in walking_space.items()}  # 문자열 키를 숫자로 변환

    web_coordinates = {
        1: [(10, 160), (10, 240)],
        2: [(10, 160), (350, 240)],
        3: [(350, 160), (710, 240)],
        4: [(710, 160), (1200, 240)],
        5: [(10, 240), (350, 495)],
        6: [(710, 240), (1200, 495)],
        7: [(10, 495), (350, 600)],
        8: [(350, 495), (710, 600)],
        9: [(710, 495), (1200, 600)],
        10: [(10, 600), (350, 845)],
        11: [(710, 600), (1200, 845)],
        12: [(10, 845), (350, 920)],
        13: [(350, 845), (710, 920)],
        14: [(710, 845), (1200, 920)],
        15: [(10, 845), (10, 920)]
    }

    for zone_id, parking_pts in walking_space.items():
        # 주차장의 네 개 좌표를 numpy 배열로 변환
        parking_pts_array = np.array(parking_pts["position"], dtype="float32")

        # 웹 구역의 네 개 좌표 생성 (직사각형이므로 자동으로 구할 수 있음)
        web_top_left, web_bottom_right = web_coordinates[zone_id]
        web_pts_array = np.array([
            [web_top_left[0], web_top_left[1]],
            [web_bottom_right[0], web_top_left[1]],
            [web_bottom_right[0], web_bottom_right[1]],
            [web_top_left[0], web_bottom_right[1]]
        ], dtype="float32")

        # 투시 변환 행렬 계산 (주차장에서 웹으로 변환)
        transform_matrix = cv2.getPerspectiveTransform(parking_pts_array, web_pts_array)
        transform_matrices[zone_id] = transform_matrix

    while True:
        try:
            # Queue에서 데이터가 있을 때까지 대기
            data = route_data_queue.get(timeout=1)
            # Sending path: {'cars': {1: {'car_number': '1234', 'status': 'parking', 'parking': 22, 'route': [], 'parking_time': 1728125835.2989068},
            #                                   2: {'car_number': '5678', 'status': 'parking', 'parking': 23, 'route': [], 'parking_time': 1728125835.298909}}}

            print(f"send_to_server 에서 받은 데이터 : {data}")
            cars = data["cars"]

            parking_data = data["parking"]

            print("parkingData = ", parking_data)

            send_data = {"time": time.time()}

            moving_data = {}

            print("cars (send to server) = ", cars)

            for id, value in cars.items():
                print("id = ", id)
                print("value = ", value)
                transformed_x, transformed_y = transform_to_web_coordinates(id, value["position"][0], value["position"][1])
                if value["status"] == "entry":
                    parking_data[value["parking"]]["entry_time"] = value["entry_time"]
                    moving_data[id] = {"position": (transformed_x, transformed_y), "entry_time": value["entry_time"], "car_number": value["car_number"], "status": "entry"}
                elif value["status"] == "exit":
                    moving_data[id] = {"position": (transformed_x, transformed_y), "entry_time": value["entry_time"], "car_number": value["car_number"], "status": "exit"}

            send_data["parking"] = parking_data
            send_data["moving"] = moving_data

            print(f"Sending path: {send_data}")

            # 서버로 데이터 전송
            sio.emit('message', send_data)

            # Arduino로 전송할 데이터 생성
            arduino_data = {}

            for car, value in data["cars"].items():
                # 3개 이상의 경로가 있고 경로의 두 번째 값이 2, 4, 7, 9, 12, 14인 경우
                route = value["route"]
                if route and len(route) > 2 and route[1] in (2, 4, 7, 9, 12, 14):
                    display_area = walking_space[route[1]]
                    next_area = walking_space[route[2]]
                    display_area_id = route[1]

                    current_center = calculate_center(display_area["position"])  # display_area의 중심점
                    next_center = calculate_center(next_area["position"])  # next_area의 중심점

                    # X와 Y의 차이를 절대값으로 계산
                    delta_x = abs(current_center[0] - next_center[0])
                    delta_y = abs(current_center[1] - next_center[1])

                    # X 좌표의 차이가 더 큰 경우
                    if delta_x > delta_y:
                        if current_center[0] < next_center[0]:
                            arduino_data[display_area_id] = {"car_number": car, "direction": "right"}
                        elif current_center[0] > next_center[0]:
                            arduino_data[display_area_id] = {"car_number": car, "direction": "left"}

                    # Y 좌표의 차이가 더 큰 경우
                    else:
                        if current_center[1] < next_center[1]:
                            arduino_data[display_area_id] = {"car_number": car, "direction": "down"}
                        elif current_center[1] > next_center[1]:
                            arduino_data[display_area_id] = {"car_number": car, "direction": "up"}

            print(f"Arduino data: {arduino_data}")

            ser.write((str(arduino_data) + "\n").encode())

            # ser.write(("Data sent!" + str(time.time()) + "\n").encode()) # TEST 테스트 데이터

        except queue.Empty:
            # Queue가 비었을 때는 잠시 대기
            time.sleep(1)
            continue

transform_matrices = {}

if __name__ == "__main__":

    serial_port = "/dev/ttyACM0"

    ser = serial.Serial(serial_port, 9600, timeout=1)

    arduino_data = {
        2: {"car_number": "12가3456", "direction": "right"},
        4: {"car_number": "34나7890", "direction": "down"},
        7: {"car_number": "56다1234", "direction": "left"}
    }

    while True:
        ser.write((str(arduino_data) + "\n").encode())
        print("Data sent!")
        time.sleep(0.2)
