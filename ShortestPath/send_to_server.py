import socketio
import time
import queue

from shortest_route import walking_space

# Standard Python
sio = socketio.Client()

@sio.event
def connect():
    print("Connection established")

@sio.event
def disconnect():
    print("Disconnected from server")

def send_to_server(uri, route_data_queue):
    sio.connect(uri)
    while True:
        try:
            # Queue에서 데이터가 있을 때까지 대기
            route_data = route_data_queue.get(timeout=1)
            # Sending path: {'total_cars': 24, 'cars': {1: {'car_number': '1234', 'status': 'parking', 'parking': 22, 'route': [], 'parking_time': 1728125835.2989068},
            #                                   2: {'car_number': '5678', 'status': 'parking', 'parking': 23, 'route': [], 'parking_time': 1728125835.298909}}}
            print(f"Sending path: {route_data}")

            # 서버로 데이터 전송
            sio.emit('message', route_data)

            arduino_data = []

            for car, value in route_data["cars"].items():
                # 3개 이상의 경로가 있고 경로의 두 번째 값이 2, 4, 7, 9, 12, 14인 경우
                route = value["route"]
                if route and route[1] in (2, 4, 7, 9, 12, 14) and len(route) > 2:
                    display_area = walking_space[route[1]]
                    next_area = walking_space[route[2]]
                    display_area_id = route[1]

                    # TODO 실환경에서 테스트 할 경우에는 좌표가 완전히 동일하지 않기 때문에 +- 얼마 정도로 조건을 수정해야 함
                    # x 좌표가 같은 경우
                    if display_area["position"][0][0] == next_area["position"][0][0]:
                        if display_area["position"][0][1] < next_area["position"][0][1]:
                            arduino_data.append((car, display_area_id, "down"))
                        elif display_area["position"][0][1] > next_area["position"][0][1]:
                            arduino_data.append((car, display_area_id, "up"))

                    # y 좌표가 같은 경우
                    elif display_area["position"][0][1] == next_area["position"][0][1]:
                        if display_area["position"][0][0] < next_area["position"][0][0]:
                            arduino_data.append((car, display_area_id, "right"))
                        elif display_area["position"][0][0] > next_area["position"][0][0]:
                            arduino_data.append((car, display_area_id, "left"))

        except queue.Empty:
            # Queue가 비었을 때는 잠시 대기
            time.sleep(1)
            continue

if __name__ == "__main__":
    uri = "http://localhost:5002"  # Socket.IO는 ws:// 대신 http:// 사용
    route_data_queue = queue.Queue()
    send_to_server(uri, route_data_queue)
