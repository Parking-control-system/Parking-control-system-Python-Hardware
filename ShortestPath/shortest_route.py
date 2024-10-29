import heapq
import time
import json
import serial

### 변수 선언 ###

# 주차 구역의 좌표값
parking_space = {}

# 이동 구역의 좌표값
walking_space = {}

# 경로를 계산할 차량
vehicles_to_route = {}  # {이동 구역 아이디: 차량 아이디}

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

# 차량의 번호와 ID를 매핑 (지속적으로 추적하며 상태를 관리할 차량 목록)
car_numbers = {
    # status = entry, parking, exit
    # parking = 상태가 entry일 경우에는 주차할 구역, parking일 경우에는 주차한 구역
    # id: {"car_number": "1234", "status": "entry", "parking": 0}
    # 0: {"car_number": "12가1234", "status": "entry", "parking": 21, "route": [], "parking_time": None, "entry_time": None},
}

# 최초 실행 시 주차되어 있던 차량
set_car_numbers = {}

# 최초 실행 여부
isFirst = True


### 함수 선언 ###

# 쓰레드에서 실행 되는 메인 함수
def main(yolo_data_queue, car_number_data_queue, route_data_queue, event, parking_space_path, walking_space_path, serial_port):
    """쓰레드에서 실행 되는 메인 함수"""

    # 처음 두 번의 경우는 트래커가 추적을 못하는 데이터이므로 버림
    yolo_data_queue.get()
    yolo_data_queue.get()

    # parking_space, walking_space 설정
    initialize_data(parking_space_path, walking_space_path)

    # 최초 실행 시 주차된 차량 아이디 부여
    init(yolo_data_queue)

    # tracking 쓰레드 루프 시작
    event.set()

    # 루프 실행
    roop(yolo_data_queue, car_number_data_queue, route_data_queue, serial_port)


# 최초 주차된 차량 아이디 부여
def init(yolo_data_queue):
    tracking_data = yolo_data_queue.get()["vehicles"]

    print("최초 실행 데이터", tracking_data)

    for key, value in tracking_data.items():
        for parking_id, parking_value in parking_space.items():
            if is_point_in_rectangle(value["position"], parking_value["position"]):
                print(parking_value["name"])

        for walking_id, walking_value in walking_space.items():
            if is_point_in_rectangle(value["position"], walking_value["position"]):
                print(walking_value["name"])

        car_number = input(f"id {key}번 차량 번호: ")
        set_car_numbers[car_number] = value["position"]


def roop(yolo_data_queue, car_number_data_queue, route_data_queue, serial_port):
    """차량 추적 데이터와 차량 번호 데이터를 받아오는 메인 함수"""

    global vehicles_to_route

    ser = serial.Serial(serial_port, 9600, timeout=1)

    print("최초 실행 시 설정된 차량 번호", set_car_numbers)
    while True:
        # yolo로 추적한 데이터 큐에서 가져오기
        vehicles = yolo_data_queue.get()["vehicles"]

        print("최단 경로 수신 데이터", vehicles)

        parking_positions = {}  # 주차한 차량의 위치 정보 {구역 아이디: 차량 아이디}
        walking_positions = {}  # 이동 중인 차량의 위치 정보 {구역 아이디: 차량 아이디}

        # 최초 실행의 경우 실행 전 주차된 차량 아이디 부여
        if isFirst:
            first_func(vehicles)

        # 감지된 차량들의 위치 확인
        for vehicle_id, value in vehicles.items():
            # 차량 번호가 있는 차량 확인
            if vehicle_id in car_numbers:
                check_position(vehicle_id, value, parking_positions, walking_positions)
                car_numbers[vehicle_id]["position"] = value["position"]

            # 차량 번호가 없는 차 중 입차 구역에 있는 차량
            elif is_point_in_rectangle(value["position"], walking_space[15]["position"]):
                entry(vehicle_id, car_number_data_queue, value["position"])
                walking_positions[15] = vehicle_id

        print("주차 구역 차량", parking_positions)
        print("이동 구역 차량", walking_positions)

        # 차량 출차 확인
        if 1 in walking_positions:
            car_exit(walking_positions, ser)

        vehicles_to_route = {}  # 경로를 계산할 차량 초기화

        # 차량 위치에 따라 주차 공간, 이동 공간, 차량 설정
        set_parking_space(parking_positions)
        set_walking_space(walking_positions, vehicles)

        print("경로를 계산할 차량", vehicles_to_route)

        # 경로 계산
        for space_id, car_id in vehicles_to_route.items():
            cal_route(space_id, car_id)

        print("car_numbers", car_numbers)
        print("parking_space", parking_space)
        print(congestion)

        # 차량 데이터 전송 (cars: 차량 정보, parking: 주차 구역 정보, walking: 이동 중인 차량 id)
        route_data_queue.put({"cars": car_numbers, "parking": parking_space, "walking": walking_positions})

        yolo_data_queue.task_done()  # 처리 완료 신호


def initialize_data(parking_space_path, walking_space_path):
    """최초 실행 시 데이터 설정"""
    global parking_space
    global walking_space

    # json으로 부터 parking_space 데이터를 읽어옴
    with open(parking_space_path, "r") as f:
        parking_space = json.load(f)
        parking_space = {int(key): value for key, value in parking_space.items()}  # 문자열 키를 숫자로 변환

    # json으로 부터 walking_space 데이터를 읽어옴
    with open(walking_space_path, "r") as f:
        walking_space = json.load(f)
        walking_space = {int(key): value for key, value in walking_space.items()}  # 문자열 키를 숫자로 변환


def car_exit(arg_walking_positions, arg_serial):
    """차량이 출차하는 함수"""
    print("출차하는 차량이 있습니다.")
    if car_numbers[arg_walking_positions[1]]["parking"] != -1:
        parking_space[car_numbers[arg_walking_positions[1]]["parking"]]["status"] = "empty"
    del car_numbers[arg_walking_positions[1]]
    del arg_walking_positions[1]
    arg_serial.write("exit".encode())
    print("차량이 출차했습니다.")


def entry(vehicle_id, data_queue, arg_position):
    """차량이 입차하는 함수"""
    print("입차하는 차량이 있습니다.")
    if data_queue.qsize() > 0:
        car_number = data_queue.get()
        print(f"2번 쓰레드: 입출차기에서 수신한 차량 번호: {car_number}")
        if car_number == "[]":
            return
        car_numbers[vehicle_id] = {"car_number": car_number, "status": "entry",
                                              "parking": set_goal(car_number), "route": [], "entry_time": time.time(),
                                              "position": arg_position, "last_visited_space": None}
        print("car_numbers", car_numbers)


# 경로 내의 특정 구역까지의 혼잡도를 감소시키는 함수
def decrease_congestion_target_in_route(arg_route, arg_target):
    """경로 내의 특정 구역까지의 혼잡도를 감소시키는 함수"""
    for node in arg_route:
        if node == arg_target:
            break
        for next_node in congestion[node]:
            congestion[node][next_node] -= 2


# 사전에 주차 되어 있던 차량에 번호 부여
def first_func(arg_vehicles):
    """사전에 주차 되어 있던 차량에 번호 부여"""
    print("isFirst arg_vehicles", arg_vehicles)
    print("isFirst set_car_numbers", set_car_numbers)
    global isFirst
    global car_numbers

    for key, value in set_car_numbers.items():
        for car_id, car_value in arg_vehicles.items():
            # 오차 범위 +- 10 이내 이면 같은 차량으로 판단
            if value[0] - 10 <= car_value["position"][0] <= value[0] + 10 and \
                    value[1] - 10 <= car_value["position"][1] <= value[1] + 10:
                car_numbers[car_id] = {"car_number": key, "status": "entry", "parking": set_goal(key), "route": [], "entry_time": time.time(), "last_visited_space": None}
                print("isFirst car_numbers", car_numbers)
                break

    isFirst = False


# 경로 내의 구역의 혼잡도를 감소시키는 함수
def decrease_congestion(arg_route, arg_congestion = 2):
    """경로 내의 구역의 혼잡도를 감소시키는 함수"""
    for node in arg_route:
        for next_node in congestion[node]:
            congestion[node][next_node] -= arg_congestion


# 경로 내의 구역의 혼잡도를 증가시키는 함수
def increase_congestion(arg_route, arg_congestion = 2):
    """경로 내의 구역의 혼잡도를 증가시키는 함수"""
    for node in arg_route:
        for next_node in congestion[node]:
            congestion[node][next_node] += arg_congestion


# 주차 구역에 대한 이동 구역을 반환하는 함수
def get_walking_space_for_parking_space(arg_parking_space):
    """주차 구역에 대한 이동 구역을 반환하는 함수"""
    for key, value in walking_space.items():
        if arg_parking_space in tuple(value["parking_space"]):
            return key


# 차량의 위치를 확인하여 주차 공간 또는 이동 공간에 할당하는 함수
def check_position(vehicle_id, vehicle_value, arg_parking_positions, arg_walking_positions):
    """차량의 위치를 확인하여 주차 공간 또는 이동 공간에 할당하는 함수"""

    px, py = vehicle_value["position"]

    # 주차 공간 체크
    for key, value in parking_space.items():
        if str(vehicle_id) in car_numbers and is_point_in_rectangle((px, py), value["position"]):
            arg_parking_positions[key] = vehicle_id
            return

    # 이동 공간 체크
    for key, value in walking_space.items():
        if str(vehicle_id) in car_numbers and is_point_in_rectangle((px, py), value["position"]):
            arg_walking_positions[key] = vehicle_id
            return

    print(f"차량 {vehicle_id}의 위치를 확인할 수 없습니다.")


# 주차 공간 및 주차 차량 설정
def set_parking_space(arg_parking_positions):
    """주차 공간 및 주차 차량 설정"""

    for space_id, car_id in arg_parking_positions.items():
        # 주차 중
        if parking_space[space_id]["status"] == "occupied":
            continue

        # 해당 구역에 주차 예정이 아니었던 차량이 들어온 경우
        elif parking_space[space_id]["status"] == "target" and parking_space[space_id]["car_number"] != car_id:
            # 원래 주차 예정이었던 차량 설정
            car_numbers[parking_space[space_id]["car_number"]]["parking"] = set_goal(parking_space[space_id]["car_number"]) # 주차 공간 변경
            decrease_congestion(car_numbers[parking_space[space_id]["car_number"]]["route"])    # 이전 경로 혼잡도 감소
            car_numbers[parking_space[space_id]["car_number"]]["route"] = []    # 경로 초기화

        # 주차 구역 설정
        parking_space[space_id]["status"] = "occupied"
        parking_space[space_id]["car_number"] = car_id
        parking_space[space_id]["parking_time"] = time.time()

        # 차량 설정
        car_numbers[car_id]["status"] = "parking"
        car_numbers[car_id]["parking"] = space_id
        decrease_congestion(car_numbers[car_id]["route"])    # 이전 경로 혼잡도 감소
        car_numbers[car_id]["route"] = []
        car_numbers[car_id]["last_visited_space"] = None


# 이동 공간 및 이동하는 차량 설정
def set_walking_space(arg_walking_positions, arg_vehicles):
    """이동 공간 및 이동하는 차량 설정"""

    global vehicles_to_route

    for space_id, car_id in arg_walking_positions.items():
        # 주차 한 후 최초 이동 시
        if car_numbers[car_id]["status"] == "parking":
            # 주차 구역 비우기
            parking_space[car_numbers[car_id]["parking"]]["status"] = "empty"
            parking_space[car_numbers[car_id]["parking"]]["car_number"] = None
            parking_space[car_numbers[car_id]["parking"]]["parking_time"] = None

            # 차량 설정
            car_numbers[car_id]["status"] = "exit"
            car_numbers[car_id]["route"] = []
            car_numbers[car_id]["parking"] = -1 # 출구로 설정

        # 경로에서 벗어난 경우
        if space_id not in car_numbers[car_id]["route"]:
            decrease_congestion(car_numbers[car_id]["route"])    # 이전 경로 혼잡도 감소
            if car_numbers[car_id]["route"]:
                car_numbers[car_id]["last_visited_space"] = car_numbers[car_id]["route"][0]    # 직전 방문 구역 설정
            car_numbers[car_id]["route"] = []    # 경로 초기화

        elif space_id in car_numbers[car_id]["route"]:
            temp_index = car_numbers[car_id]["route"].index(space_id)

            # 경로의 첫번째 위치면 스킵
            if temp_index == 0:
                continue

            decrease_congestion_target_in_route(car_numbers[car_id]["route"], space_id)
            car_numbers[car_id]["last_visited_space"] = car_numbers[car_id]["route"][temp_index - 1]    # 이전 방문 구역 설정
            car_numbers[car_id]["route"] = car_numbers[car_id]["route"][temp_index:]    # 경로 수정

        # 경로가 없는 경우 경로를 계산할 딕셔너리에 추가
        if not car_numbers[car_id]["route"]:
            vehicles_to_route[space_id] = car_id

        # 이동 중인 차량 위치 기록
        car_numbers[car_id]["position"] = arg_vehicles[car_id]["position"]


# 주차할 공간을 지정하는 함수 (할당할 주차 공간의 순서 지정)
def set_goal(arg_car_number):
    """주차할 공간을 지정하는 함수"""
    print("set_goal")
    for i in (11, 10, 21, 13, 20, 12, 19, 18, 17, 7, 6, 9, 8, 16, 15, 0, 14, 1, 2, 3, 4, 5):    # 할당할 주차 구역 순서
        if parking_space[i]["status"] == "empty":
            parking_space[i]["status"] = "target"
            parking_space[i]["car_number"] = arg_car_number
            return i

    print("주차 공간이 없습니다.")
    return -1


def cal_route(space_id, car_id):
    parking_goal = get_walking_space_for_parking_space(car_numbers[car_id]["parking"])
    if car_numbers[car_id]["last_visited_space"]:
        increase_congestion((car_numbers[car_id]["last_visited_space"], ), 100)  # 직전 방문 구역 혼잡도 증가
    route = a_star(congestion, space_id, parking_goal)
    if car_numbers[car_id]["last_visited_space"]:
        decrease_congestion((car_numbers[car_id]["last_visited_space"], ), 100)  # 직전 방문 구역 혼잡도 감소

    # 주차를 하는 차량의 경우 경로 상에 비어 있는 주차 구역 확인
    if car_numbers[car_id]["status"] == "entry":
        amend_goal, amend_parking_space = check_route(route[:-1])
    else:
        amend_goal, amend_parking_space = None, None

    # 경로 상에 비어있는 주차 공간이 있는 경우 경로 수정 및 주차 공간 변경
    if amend_goal is not None:
        route = route[:route.index(amend_goal) + 1]
        parking_space[car_numbers[car_id]["parking"]]["status"] = "empty"  # 이전 주차 공간 비우기
        car_numbers[car_id]["parking"] = amend_parking_space  # 주차 공간 변경
        parking_space[amend_parking_space]["status"] = "target"  # 새로운 주차 공간 설정
        parking_space[amend_parking_space]["car_number"] = car_id  # 새로운 주차 공간 설정

    increase_congestion(route)
    car_numbers[car_id]["route"] = route

    print(f"차량 {car_id}의 경로: {route}")


def is_point_in_rectangle(point, rectangle):
    """
    특정 좌표가 사각형 내부에 있는지 확인하는 함수.
    :param point: (x, y) 확인할 좌표
    :param rectangle: [(x1, y1), (x2, y2), (x3, y3), (x4, y4)] 사각형의 꼭짓점 (좌상단, 우상단, 우하단, 좌하단 순서)
    :return: bool 해당 점이 사각형 안에 있는지 여부
    """

    def vector_cross_product(v1, v2):
        """두 벡터의 외적을 계산하는 함수."""
        return v1[0] * v2[1] - v1[1] * v2[0]

    def is_same_direction(v1, v2):
        """두 벡터의 외적의 부호가 같은지 확인."""
        return vector_cross_product(v1, v2) >= 0

    # 사각형의 네 꼭짓점과 점을 연결하는 벡터를 계산
    for i in range(4):
        v1 = (rectangle[(i + 1) % 4][0] - rectangle[i][0], rectangle[(i + 1) % 4][1] - rectangle[i][1])
        v2 = (point[0] - rectangle[i][0], point[1] - rectangle[i][1])

        # 외적이 모두 같은 부호라면 점이 사각형 내부에 있음
        if not is_same_direction(v1, v2):
            return False

    return True


# A* 알고리즘 예측 함수
def heuristic(a, b):
    # 휴리스틱 함수: 여기서는 간단하게 두 노드 간 차이만 계산 (유클리드 거리는 필요하지 않음)
    # 예측용 함수로 모든 계산을 하기 전에 대략적인 예측을 하여 가능성 높은곳만 계산하도록 도와줌
    return 0


# A* 알고리즘
def a_star(arg_congestion, arg_start, arg_goal):
    """경로를 계산하여 반환하는 함수"""
    pq = []
    heapq.heappush(pq, (0, arg_start))
    came_from = {arg_start: None}
    cost_so_far = {arg_start: 0}
    
    while pq:
        current = heapq.heappop(pq)[1]
        
        if current == arg_goal:
            break
        
        for next_node in arg_congestion[current]:
            new_cost = cost_so_far[current] + arg_congestion[current][next_node]
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                priority = new_cost + heuristic(arg_goal, next_node)
                heapq.heappush(pq, (priority, next_node))
                came_from[next_node] = current
    
    # 경로를 역추적하여 반환
    current = arg_goal
    result_path = []
    while current:
        result_path.append(current)
        current = came_from[current]
    result_path.reverse()
    
    return result_path


# 경로상에 추차할 구역이 있는지 확인하는 함수
def check_route(arg_route):
    print("check_route")
    print(arg_route)
    for walking_space_id in arg_route:
        for parking_space_id in walking_space[walking_space_id]["parking_space"]:
            if parking_space_id != -1 and parking_space[parking_space_id]["status"] == "empty":
                return walking_space_id, parking_space_id

    return None, None

if __name__ == "__main__":

    start = 0
    goal = 14

    path = a_star(congestion, start, goal)
    print(path)