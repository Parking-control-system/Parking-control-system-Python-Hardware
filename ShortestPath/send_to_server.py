import socketio
import time
import queue

from shortest_route import walking_space, parking_space

# Standard Python
sio = socketio.Client(reconnection=True, reconnection_attempts=5, reconnection_delay=2)

@sio.event
def connect():
    print("Connection established")

@sio.event
def disconnect():
    print("Disconnected from server")

def send_to_server(uri, route_data_queue):
    sio.connect(uri)
    # test
    moving_x = 0
    moving_y = 0

    while True:
        try:
            # Queue에서 데이터가 있을 때까지 대기
            data = route_data_queue.get(timeout=1)
            # Sending path: {'cars': {1: {'car_number': '1234', 'status': 'parking', 'parking': 22, 'route': [], 'parking_time': 1728125835.2989068},
            #                                   2: {'car_number': '5678', 'status': 'parking', 'parking': 23, 'route': [], 'parking_time': 1728125835.298909}}}

            cars = data["cars"]

            parking_data = parking_space.copy()

            print("parkingData = ", parking_data)

            moving_data = {
                0: {"position": (0 + moving_x, 0 + moving_y), "entry_time": 0},
                1: {"position": (100 - moving_x, 200 - moving_y), "entry_time": 0},
            }

            moving_x += 2
            moving_y += 1

            if moving_x > 100:
                moving_x = 0
                moving_y = 0

            send_data = {"time": time.time()}

            for id, value in data["moving"]:
                moving_data[value]["position"] = cars[value]["position"]
                moving_data[value]["entry_time"] = cars[value]["entry_time"]
                moving_data[value]["car_number"] = cars[value]["car_number"]

            send_data["moving"] = moving_data

            for id, value in data["cars"].items():
                if value["status"] == "entry":
                    parking_data[value["parking"]]["status"] = "target"
                    parking_data[value["parking"]]["car_number"] = value["car_number"]
                    parking_data[value["parking"]]["entry_time"] = value["entry_time"]

            for id, value in data["parking"]:
                parking_data[id]["status"] = "parking"
                parking_data[id]["car_number"] = cars[value]["car_number"]
                parking_data[id["parking_time"]] = cars[value]["parking_time"]

            send_data["parking"] = parking_data

            timed = 1728718966.121786

            # 웹 테스트 데이터
            for i in (0, 1, 2, 3, 13, 14, 17, 21):
                parking_data[i]["status"] = "parking"
                parking_data[i]["car_number"] = "123가5674"
                parking_data[i]["entry_time"] = time.time()
                parking_data[i]["parking_time"] = timed + i

            for i in (3, 21):
                send_data["parking"][i]["status"] = "target"
                send_data["parking"][i]["car_number"] = "123가5674"
                send_data["parking"][i]["entry_time"] = timed + i

            print(f"Sending path: {send_data}")

            # 서버로 데이터 전송
            sio.emit('message', send_data)

            arduino_data = []

            for car, value in data["cars"].items():
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
