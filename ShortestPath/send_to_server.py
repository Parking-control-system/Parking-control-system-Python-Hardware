# 웹서버와 아두이노로 데이터를 정제하여 전송

import socketio
import time
import queue
import json
import serial
import numpy as np
import cv2
import platform


# 웹 페이지 각 구역 좌표
web_coordinates = {
        1: [(-50, 100), (0, 200)],
        2: [(0, 100), (300, 200)],
        3: [(300, 100), (650, 200)],
        4: [(650, 100), (1150, 200)],
        5: [(10, 200), (300, 430)],
        6: [(650, 200), (1150, 430)],
        7: [(0, 430), (300, 550)],
        8: [(350, 430), (650, 550)],
        9: [(650, 430), (1150, 550)],
        10: [(0, 550), (300, 780)],
        11: [(650, 550), (1150, 780)],
        12: [(0, 780), (300, 860)],
        13: [(300, 780), (650, 860)],
        14: [(650, 780), (1150, 860)],
        15: [(-50, 780), (0, 860)]
}

# 아두이노로 전송할 데이터
arduino_data = {}

# 이전에 아두이노로 전송한 데이터
previous_arduino_data = None

# 경로를 안내하는 디스플레이의 구역 번호 (아두이노의 메트릭스 순서에 맞게 조정)
DISPLAY_SPACE = (12, 7, 2, 14, 9, 4)

# 이동 구역의 좌표
walking_space = {}

# 사각형의 중심점 계산 함수
def calculate_center(points):
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    center_x = sum(x_coords) / len(points)
    center_y = sum(y_coords) / len(points)
    return (center_x, center_y)


def transform_point_in_quadrilateral_to_rectangle(point, quadrilateral, arg_web_coordinate):
    """
    사각형 내부의 특정 점을 웹 좌표 내 직사각형의 대응 위치로 변환

    :param point: (px, py) 사각형 내부의 특정 점의 좌표
    :param quadrilateral: [(x1, y1), (x2, y2), (x3, y3), (x4, y4)] 사각형의 네 꼭짓점 좌표 (좌상단, 우상단, 우하단, 좌하단 순서)
    :param arg_web_coordinate: 변환 대상 구역의 웹 좌표 내 직사각형 [(x1, y1), (x2, y2)] 좌상단 및 우하단 좌표
    :return: 변환된 웹 내 점의 좌표 (x, y)
    """

    # 사각형의 네 꼭짓점 좌표 배열화
    quad_pts = np.array(quadrilateral, dtype="float32")

    # 웹 좌표 내 직사각형 꼭짓점 설정
    web_top_left, web_bottom_right = arg_web_coordinate
    rect_pts = np.array([
        [web_top_left[0], web_top_left[1]],
        [web_bottom_right[0], web_top_left[1]],
        [web_bottom_right[0], web_bottom_right[1]],
        [web_top_left[0], web_bottom_right[1]]
    ], dtype="float32")

    # 투시 변환 행렬 계산
    transform_matrix = cv2.getPerspectiveTransform(quad_pts, rect_pts)

    # 특정 점을 배열로 변환하여 투시 변환 적용
    point_array = np.array([[point]], dtype="float32")  # (px, py)
    transformed_point = cv2.perspectiveTransform(point_array, transform_matrix)

    # 결과 좌표 반환
    transformed_x, transformed_y = transformed_point[0][0]
    return float(transformed_x), float(transformed_y)


def reflect_point_in_rectangle(point, rectangle_corners):
    """
    직사각형의 좌상단과 우하단 좌표만을 이용해 특정 점을 상하좌우 반전시킨 좌표로 변환합니다.

    :param point: (px, py) 특정 점의 좌표
    :param rectangle_corners: [(x1, y1), (x2, y2)] 직사각형의 좌상단 및 우하단 좌표
    :return: 상하좌우 반전된 새로운 좌표 (x', y')
    """
    px, py = point

    top_left, bottom_right = rectangle_corners

    # 직사각형 중심 계산
    center_x = (top_left[0] + bottom_right[0]) / 2
    center_y = (top_left[1] + bottom_right[1]) / 2

    # 상하좌우 반전
    reflected_x = 2 * center_x - px
    reflected_y = 2 * center_y - py

    return reflected_x, reflected_y


# 경로에 따라 아두이노로 전송할 데이터 생성
def set_arduino_data(route, value):
    display_area = walking_space[route[1]]
    next_area = walking_space[route[2]]
    display_area_id = DISPLAY_SPACE.index(route[1]) + 1

    display_center = calculate_center(display_area["position"])  # display_area의 중심점
    next_center = calculate_center(next_area["position"])  # next_area의 중심점

    # display_area와 next_area의 중심점 좌표 차이 계산
    delta_x = abs(display_center[0] - next_center[0])
    delta_y = abs(display_center[1] - next_center[1])

    # X 좌표의 차이가 더 큰 경우
    if delta_x > delta_y:
        if display_center[0] < next_center[0]:
            arduino_data[display_area_id] = {"car_number": value.get("car_number", "No Number"), "direction": "left"}
        elif display_center[0] > next_center[0]:
            arduino_data[display_area_id] = {"car_number": value.get("car_number", "No Number"), "direction": "right"}

    # Y 좌표의 차이가 더 큰 경우
    else:
        if display_center[1] < next_center[1]:
            arduino_data[display_area_id] = {"car_number": value.get("car_number", "No Number"), "direction": "up"}
        elif display_center[1] > next_center[1]:
            arduino_data[display_area_id] = {"car_number": value.get("car_number", "No Number"), "direction": "down"}


def cal_web_position(space_id, car_id, cars):
    transformed_x, transformed_y = transform_point_in_quadrilateral_to_rectangle(cars[car_id]["position"],
                                                                                 walking_space[space_id]["position"],
                                                                                 web_coordinates[space_id])

    reflect_x, reflect_y = reflect_point_in_rectangle((transformed_x, transformed_y), web_coordinates[space_id])

    return reflect_x, reflect_y


# 소켓 지정
sio = socketio.Client(reconnection=True, reconnection_attempts=5, reconnection_delay=2)

@sio.event
def connect():
    print("Connection established")

@sio.event
def disconnect():
    print("Disconnected from server")

def send_to_server(uri, route_data_queue, parking_space_path, walking_space_path, serial_port, serial_port2):
    # 서버 연결
    global arduino_data
    global previous_arduino_data
    global walking_space

    # 서버 연결
    sio.connect(uri)

    # 시리얼 통신 설정
    if platform.system() == "Linux":
        ser = serial.Serial(serial_port, 9600, timeout=1)
        ser2 = serial.Serial(serial_port2, 9600, timeout=1)

    # walking_space의 키를 숫자형으로 변환
    with open(walking_space_path,
              "r") as f:
        walking_space = json.load(f)
        walking_space = {int(key): value for key, value in walking_space.items()}  # 문자열 키를 숫자로 변환

    while True:
        try:
            # Queue에서 데이터가 있을 때까지 대기
            data = route_data_queue.get(timeout=1)
            # Sending path: {'cars': {1: {'car_number': '1234', 'status': 'parking', 'parking': 22, 'route': [], 'parking_time': 1728125835.2989068},
            #                                   2: {'car_number': '5678', 'status': 'parking', 'parking': 23, 'route': [], 'parking_time': 1728125835.298909}}}

            print(f"send_to_server 에서 받은 데이터 : {data}")
            cars = data["cars"] # 차량 데이터    {car_id: {car_number, status, parking, route, parking_time}}
            parking_data = data["parking"]  # 주차 구역 데이터 {space_id: {name, status, car_id, car_number, position, entry_time, exit_time}}

            send_data = {"time": time.time()}   # 서버로 전송할 데이터

            moving_data = {}    # 이동 중인 차량 데이터

            for car_id, value in cars.items():
                print("car_id = ", car_id)
                print("value = ", value)
                if value["status"] == "entry":
                    parking_data[value["parking"]]["entry_time"] = value["entry_time"]
                    moving_data[car_id] = {"entry_time": value["entry_time"], "car_number": value["car_number"], "status": value["status"]}
                elif value["status"] == "exit":
                    moving_data[car_id] = {"entry_time": value["entry_time"], "car_number": value["car_number"],"status": value["status"]}

            print("movingData = ", moving_data)

            # 이동 중인 차량 좌표 계산
            walking_cars = data["walking"]  # 이동 중인 차량 데이터 {space_id: car_id}
            print("walking_cars", walking_cars)

            for space_id, car_ids in walking_cars.items():  # car_ids는 리스트가 됨
                for car_id in car_ids:
                    # 차량 목록에 없는 경우 무시
                    if car_id not in cars:
                        continue

                    # 웹페이지에 표시할 좌표 계산
                    x, y = cal_web_position(space_id, car_id, cars)
                    if car_id not in moving_data:
                        moving_data[car_id] = {"car_number": cars[car_id]["car_number"],
                                               "status": cars[car_id]["status"],
                                               "entry_time": cars[car_id]["entry_time"]}
                    moving_data[car_id]["position"] = (x, y)

            # 전송할 데이터 세팅
            send_data["parking"] = parking_data
            send_data["moving"] = moving_data

            print(f"Sending path: {send_data}")

            # 서버로 데이터 전송
            sio.emit('message', send_data)

            # Arduino로 전송할 데이터 초기화
            arduino_data.clear()
            # 차량의 경로에 따라 아두이노로 전송할 데이터 생성
            processed_display_areas = set()  # 이미 처리된 디스플레이 구역을 추적
            for car_id, value in data["cars"].items():
                route = value["route"]
                if route and len(route) > 2 and route[1] in DISPLAY_SPACE:
                    display_area_id = DISPLAY_SPACE.index(route[1]) + 1
                    if display_area_id not in processed_display_areas:
                        set_arduino_data(route, value)
                        processed_display_areas.add(display_area_id)

            print(f"Arduino data: {arduino_data}")
            print(f"Previous arduino data: {previous_arduino_data}")

            # 생성한 데이터가 이전 데이터와 다를 경우 아두이노로 데이터 전송
            if arduino_data != previous_arduino_data:
                previous_arduino_data = arduino_data
                if platform.system() == "Linux":
                    ser.write((str(arduino_data) + "\n").encode())
                    ser2.write((str(arduino_data) + "\n").encode())
                print("Data sent!")

        except queue.Empty:
            # Queue가 비었을 때는 잠시 대기
            print("Queue is empty")
            time.sleep(1)
            continue


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
