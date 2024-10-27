import heapq
import time
import json
import numpy as np
import cv2
import serial


def main(yolo_data_queue, car_number_data_queue, route_data_queue, event, parking_space_path, walking_space_path, serial_port):

    yolo_data_queue.get()
    yolo_data_queue.get()
    init(yolo_data_queue)

    global parking_space
    global walking_space

    # parking_space의 키를 숫자형으로 변환
    with open(parking_space_path,
              "r") as f:
        parking_space = json.load(f)
        parking_space = {int(key): value for key, value in parking_space.items()}  # 문자열 키를 숫자로 변환

    # walking_space의 키를 숫자형으로 변환
    with open(walking_space_path,
              "r") as f:
        walking_space = json.load(f)
        walking_space = {int(key): value for key, value in walking_space.items()}  # 문자열 키를 숫자로 변환

    # tracking 쓰레드 루프 시작
    event.set()

    roop(yolo_data_queue, car_number_data_queue, route_data_queue, serial_port)

# 최초 주차된 차량 아이디 부여
def init(yolo_data_queue):
    tracking_data = yolo_data_queue.get()["vehicles"]

    print("최초 실행 데이터", tracking_data)

    for key, value in tracking_data.items():
        print(key)
        print(value)
        car_number = input(f"id {key}번 차량 번호: ")
        set_car_numbers[car_number] = value["position"]

def roop(yolo_data_queue, car_number_data_queue, route_data_queue, serial_port):
    """차량 추적 데이터와 차량 번호 데이터를 받아오는 메인 함수"""

    ser = serial.Serial(serial_port, 9600, timeout=1)

    print("최초 실행 시 설정된 차량 번호", set_car_numbers)
    while True:
        # 큐에서 데이터 가져오기
        tracking_data = yolo_data_queue.get()

        if tracking_data is None:  # 종료 신호 (None) 받으면 종료
            break

        # 데이터 처리
        vehicles = tracking_data["vehicles"]

        print("최단 경로 수신 데이터", vehicles)

        # 최초 실행의 경우 주차된 차량 아이디 부여
        if isFirst:
            isFirst_func(vehicles)

        parking_positions = {}  # 주차한 차량의 위치 정보 {구역 아이디: 차량 아이디}
        walking_positions = {}  # 이동 중인 차량의 위치 정보 {구역 아이디: 차량 아이디}

        print(parking_positions)

        for car_id, value in vehicles.items():
            check_position(car_id, value, car_numbers, parking_positions, walking_positions)
            if car_id in car_numbers:
                car_numbers[car_id]["position"] = value["position"]

        set_parking_space(parking_positions)
        set_walking_space(walking_positions)

        # 주차 구역 차량 시간 기록 또는 주차 처리
        for key, value in parking_positions.items():
            vehicle_parking_time(key, value)

        # 차량 입차 확인
        if 15 in walking_positions:
            print("입차 하는 차량이 있습니다.")
            if car_number_data_queue.qsize() > 0:
                car_number = car_number_data_queue.get()
                print(f"2번 쓰레드: 입출차기에서 수신한 차량 번호: {car_number}")
                if car_number == "[]":
                    continue
                car_numbers[walking_positions[15]] = {"car_number": car_number, "status": "entry", "parking": set_goal(car_number), "route": [], "entry_time": time.time(), "position": vehicles[walking_positions[15]]["position"]}
                print("car_numbers", car_numbers)

        if 1 in walking_positions:
            print("출차 하는 차량이 있습니다.")
            exit(walking_positions[1], ser)

        vehicles_to_route = {}  # 경로를 계산할 차량

        # 이동 구역에 있는 차량이 경로가 없는 경우 또는 경로에서 벗어난 경우
        for key, value in walking_positions.items():
            print("이동 중인 차량", key, value, vehicles)
            vehicle_moving(value, vehicles) # 주차 시간 삭제 및 위치 정보 입력
            if value in car_numbers:
                temp_route = car_numbers[value]["route"]
            else:
                print("차량 정보가 없습니다.")
                temp_route = []
            # 경로가 없는 경우 또는 경로에서 벗어난 경우
            if value in car_numbers and car_numbers[value]["status"] == "entry" and (not temp_route or key not in temp_route):
                decrease_congestion(temp_route)
                car_numbers[value]["route"] = []
                vehicles_to_route[key] = value

            # 주차 후 출구로 이동하는 경우
            elif value in car_numbers and car_numbers[value]["status"] == "exit" and (not temp_route or key not in temp_route):
                decrease_congestion(temp_route)
                car_numbers[value]["route"] = []    # 경로 비우기
                # -1이 아닌 경우만 주차 공간 비우고 경로 계산
                if car_numbers[value]["parking"] != -1:
                    parking_space[car_numbers[value]["parking"]]["status"] = "empty"    # 주차 공간 비우기
                    car_numbers[value]["parking"] = -1  # 출구로 설정
                    vehicles_to_route[key] = value

            # 차량이 경로를 따라 가고 있는 경우
            elif value in car_numbers and key in temp_route:
                temp_index = temp_route.index(key)  # 경로 상에서 현재 위치의 인덱스
                # 경로의 첫번째 위치면 스킵
                if temp_index == 0:
                    continue
                decrease_congestion_target_in_route(temp_route, key)
                car_numbers[value]["route"] = temp_route[temp_index:]    # 경로 수정


        print("경로 계산할 차량 ", vehicles_to_route)

        # 경로를 계산할 차량이 있는 경우 - 이동 중인 차량의 경로 계산
        for key, value in vehicles_to_route.items():
            parking_goal = get_walking_space_for_parking_space(car_numbers[value]["parking"])
            print("경로 계산", key, parking_goal)
            route = a_star(graph, congestion, key, parking_goal)

            # 경로 상에 비어있는 주차 공간이 있는지 확인
            if car_numbers[value]["status"] == "entry":
                amend_goal, amend_parking_space = check_route(route[:-1])
            else:
                amend_goal, amend_parking_space = None, None

            # 경로 상에 비어있는 주차 공간이 있는 경우 경로 및 주차 공간 변경
            if amend_goal is not None:
                route = route[:route.index(amend_goal) + 1]
                parking_space[car_numbers[value]["parking"]]["status"] = "empty"    # 이전 주차 공간 비우기
                car_numbers[walking_positions[key]]["parking"] = amend_parking_space
                car_numbers[value]["parking"] = amend_parking_space # 주차 공간 변경

            print(route)
            increase_congestion(route)
            car_numbers[value]["route"] = route


        print("주차한 차량: ", parking_positions)
        print("이동 중인 차량: ", walking_positions)
        print("car_numbers", car_numbers)

        print("parking_space", parking_space)
        print(congestion)

        # 차량 데이터 전송
        route_data_queue.put({"cars": car_numbers, "parking": parking_space, "walking": walking_positions})

        yolo_data_queue.task_done()  # 처리 완료 신호

def exit(arg_walking_positions, arg_serial):
    """차량이 출차하는 함수"""
    if car_numbers[arg_walking_positions[1]]["target"] != -1:
        parking_space[car_numbers[arg_walking_positions[1]]["target"]]["status"] = "empty"
    del car_numbers[arg_walking_positions[1]]
    del arg_walking_positions[1]
    arg_serial.write("exit".encode())
    print("차량이 출차했습니다.")


# 경로 내의 특정 구역까지의 혼잡도를 감소시키는 함수
def decrease_congestion_target_in_route(arg_route, arg_target):
    """경로 내의 특정 구역까지의 혼잡도를 감소시키는 함수"""
    for node in arg_route:
        if node == arg_target:
            break
        for next_node in congestion[node]:
            congestion[node][next_node] -= 2

# 차량이 주차 구역에 들어온 시간을 기록하는 함수
def vehicle_parking_time(arg_space, arg_vehicle_id):
    """차량이 주차 구역에 들어온 시간을 기록하는 함수"""

    # 주차 구역에 처음 들어온 경우 (이전 시간이 없는 경우)
    if arg_vehicle_id not in stop_times:
        stop_times[arg_vehicle_id] = time.time()
    else:
        # 주차 구역에 처음 들어온 시간이 있고, 5초 이상 경과한 경우
        if time.time() - stop_times[arg_vehicle_id] >= 5:
            car_numbers[arg_vehicle_id]["status"] = "parking"
            if car_numbers[arg_vehicle_id]["parking"] != -1:
                parking_space[car_numbers[arg_vehicle_id]["parking"]]["status"] = "empty"   # 데이터의 무결성을 위해 우선 비움
            car_numbers[arg_vehicle_id]["parking"] = arg_space
            car_numbers[arg_vehicle_id]["route"] = []   # 주차 시 경로 초기화
            parking_space[arg_space]["status"] = "occupied"
            parking_space[arg_space]["car_number"] = car_numbers[arg_vehicle_id]["car_number"]
            parking_space[arg_space]["parking_time"] = stop_times[arg_vehicle_id]

# 사전에 주차 되어 있던 차량에 번호 부여
def isFirst_func(arg_vehicles):
    """사전에 주차 되어 있던 차량에 번호 부여"""
    print("isFirst arg_vehicles", arg_vehicles)
    print("isFirst set_car_numbers", set_car_numbers)
    global isFirst
    for key, value in set_car_numbers.items():
        for car_id, car_value in arg_vehicles.items():
            # 오차 범위 +- 10 이내 이면 같은 차량으로 판단
            if value[0] - 10 <= car_value["position"][0] <= value[0] + 10 and \
                    value[1] - 10 <= car_value["position"][1] <= value[1] + 10:
                car_numbers[car_id] = {"car_number": key, "status": "entry", "parking": set_goal(key), "route": [], "entry_time": time.time()}
                print("isFirst car_numbers", car_numbers)
                break

    isFirst = False

# 차량이 이동 중인 경우
def vehicle_moving(arg_vehicle_id, arg_vehicles):
    if arg_vehicle_id in stop_times:
        del stop_times[arg_vehicle_id]

    print("차량 이동 중 vehicle_moving")
    print(arg_vehicle_id)
    print(arg_vehicles)

    # 차량의 위치 정보 업데이트
    if str(arg_vehicle_id) in car_numbers:
        car_numbers[str(arg_vehicle_id)]["position"] = arg_vehicles[str(arg_vehicle_id)]["position"]

# 경로 내의 구역의 혼잡도를 감소시키는 함수
def decrease_congestion(arg_route):
    """경로 내의 구역의 혼잡도를 감소시키는 함수"""
    for node in arg_route:
        for next_node in congestion[node]:
            congestion[node][next_node] -= 2

# 경로 내의 구역의 혼잡도를 증가시키는 함수
def increase_congestion(arg_route):
    """경로 내의 구역의 혼잡도를 증가시키는 함수"""
    for node in arg_route:
        for next_node in congestion[node]:
            congestion[node][next_node] += 2

# 경로상에 추차할 구역이 있는지 확인하는 함수
def check_route(arg_route):
    print("check_route")
    print(arg_route)
    for walking_space_id in arg_route:
        for parking_space_id in walking_space[walking_space_id]["parking_space"]:
            if parking_space_id != -1 and parking_space[parking_space_id]["status"] == "empty":
                parking_space[parking_space_id]["status"] = "target"
                parking_space[parking_space_id]["car_number"] = walking_space[walking_space_id]["car_number"]
                return walking_space_id, parking_space_id

    return None, None

# 주차 구역에 대한 이동 구역을 반환하는 함수
def get_walking_space_for_parking_space(arg_parking_space):
    """주차 구역에 대한 이동 구역을 반환하는 함수"""
    for key, value in walking_space.items():
        if arg_parking_space in tuple(value["parking_space"]):
            return key

# 점이 다각형 내부에 있는지 확인하는 함수
def is_point_in_polygon(px, py, polygon_points):
    """주어진 점(px, py)이 다각형 polygon_points 내부에 있는지 확인"""
    # 다각형 좌표를 numpy 배열로 변환
    contour = np.array(polygon_points, dtype=np.int32)
    # OpenCV의 pointPolygonTest 사용
    result = cv2.pointPolygonTest(contour, (px, py), False)
    # 결과가 양수이면 내부에 있음
    return result >= 0

# 차량의 위치를 확인하는 함수
def check_position(vehicle_id, vehicle_value, car_numbers, arg_parking_positions, arg_walking_positions):
    """차량의 위치를 확인하는 함수"""
    # 차량 위치 확인
    px, py = vehicle_value["position"]

    # 주차 공간 체크
    for key, value in parking_space.items():
        if str(vehicle_id) in car_numbers and is_point_in_polygon(px, py, value["position"]):
            arg_parking_positions[key] = vehicle_id
            print(f"차량 {vehicle_id}은 주차 공간 {key}에 위치합니다.")
            return

    # 이동 공간 체크
    for key, value in walking_space.items():
        if str(vehicle_id) in car_numbers and is_point_in_polygon(px, py, value["position"]):
            arg_walking_positions[key] = vehicle_id
            print(f"차량 {vehicle_id}은 이동 공간 {key}에 위치합니다.")
            return

    # 입차 체크
    if is_point_in_polygon(px, py, walking_space[15]["position"]):
        arg_walking_positions[15] = vehicle_id
        print(f"차량 {vehicle_id}은 입차 중입니다.")
        return

    print(f"차량 {vehicle_id}의 위치를 확인할 수 없습니다.")

# 주차 공간을 설정하는 함수
def set_parking_space(arg_parking_positions):
    """주차 공간을 설정하는 함수"""
    for key, value in parking_space.items():
        if value["name"] in arg_parking_positions:
            pass
        elif value["status"] == "target":
            pass
        else:
            parking_space[key]["status"] = "empty"
            parking_space[key]["car_number"] = None
            parking_space[key]["parking_time"] = None

# 이동 공간을 설정하는 함수
def set_walking_space(arg_walking_positions):
    """이동 공간을 설정하는 함수"""
    for key, value in walking_space.items():
        if value["name"] in arg_walking_positions:
            walking_space[key]["status"] = "occupied"
            walking_space[key]["car_number"] = arg_walking_positions[value["name"]]
        else:
            walking_space[key]["status"] = "empty"
            walking_space[key]["car_number"] = None

    # 이동 공간에 있는 차량 중 주차를 했던 차량은 상태를 exit로 변경
    for key, value in arg_walking_positions.items():
        if str(value) in car_numbers and car_numbers[value]["status"] == "parking":
            car_numbers[value]["status"] = "exit"

# 주차할 공간을 지정하는 함수 (할당할 주차 공간의 순서 지정)
def set_goal(arg_car_number):
    """주차할 공간을 지정하는 함수"""
    print("set_goal")
    for i in (11, 10, 21, 13, 20, 12, 19, 18, 17, 7, 6, 9, 8, 16, 15, 0, 14, 1, 2, 3, 4, 5):    # 할당할 주차 구역 순서
        if parking_space[i]["status"] == "empty":
            parking_space[i]["status"] = "target"
            parking_space[i]["car_number"] = arg_car_number
            return i

# A* 알고리즘
def heuristic(a, b):
    # 휴리스틱 함수: 여기서는 간단하게 두 노드 간 차이만 계산 (유클리드 거리는 필요하지 않음)
    # 예측용 함수로 모든 계산을 하기 전에 대략적인 예측을 하여 가능성 높은곳만 계산하도록 도와줌
    return 0

# A* 알고리즘
def a_star(graph, congestion, start, goal):
    """경로를 계산하여 반환하는 함수"""
    pq = []
    heapq.heappush(pq, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while pq:
        current = heapq.heappop(pq)[1]
        
        if current == goal:
            break
        
        for next_node in graph[current]:
            new_cost = cost_so_far[current] + graph[current][next_node] + congestion[current][next_node]
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                priority = new_cost + heuristic(goal, next_node)
                heapq.heappush(pq, (priority, next_node))
                came_from[next_node] = current
    
    # 경로를 역추적하여 반환
    current = goal
    path = []
    while current:
        path.append(current)
        current = came_from[current]
    path.reverse()
    
    return path

# # 주차 구역의 좌표값
parking_space = {}

# # 이동 구역의 좌표값
walking_space = {}

# 그래프
graph = {
    1: {2: 1},
    2: {1: 1, 3: 1, 5: 1},
    3: {2: 2, 4: 1},
    4: {3: 1, 6: 1},
    5: {2: 2, 7: 1},
    6: {4: 1, 9: 1},
    7: {5: 1, 8: 1, 10: 1},
    8: {7: 1, 9: 1},
    9: {6: 1, 8: 1, 11: 1},
    10: {7: 1, 12: 1},
    11: {9: 1, 14: 1},
    12: {10: 1, 13: 1, 15: 1},
    13: {12: 1, 14: 1},
    14: {11: 1, 13: 1},
    15: {12: 1}
}

# 혼잡도
congestion = {
    1: {2: 1},
    2: {1: 1, 3: 1, 5: 1},
    3: {2: 2, 4: 1},
    4: {3: 1, 6: 1},
    5: {2: 2, 7: 1},
    6: {4: 1, 9: 1},
    7: {5: 1, 8: 1, 10: 1},
    8: {7: 1, 9: 1},
    9: {6: 1, 8: 1, 11: 1},
    10: {7: 1, 12: 1},
    11: {9: 1, 14: 1},
    12: {10: 1, 13: 1, 15: 1},
    13: {12: 1, 14: 1},
    14: {11: 1, 13: 1},
    15: {12: 1}
}

# 차량의 번호와 ID를 매핑
car_numbers = {
    # status = entry, parking, exit
    # parking = 상태가 entry일 경우에는 주차할 구역, parking일 경우에는 주차한 구역
    # id: {"car_number": "1234", "status": "entry", "parking": 0}
    # 0: {"car_number": "12가1234", "status": "entry", "parking": 21, "route": [], "parking_time": None, "entry_time": None},
}

# 경로
routes = {}

# 각 차량의 정지 시간을 기록
stop_times = {}

# 이미 주차되어 있던 차량
set_car_numbers = {}

isFirst = True

number_of_parking_space = len(parking_space)

if __name__ == "__main__":

    start = 0
    goal = 14

    path = a_star(graph, congestion, start, goal)
    print(path)