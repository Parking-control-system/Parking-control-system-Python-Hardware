import time
import queue
import random

def track_vehicles(yolo_data_queue):
    i = 0
    while True:
        # 차량과 주차 공간 정보 생성 (예시 데이터)
        tracking_data = {
            "vehicles": [
                # {"id": i, "position": (random.randint(0, 400), random.randint(0, 400)), "speed": 20 + i, "direction": "north", \
                #  "status": "moving"} for i in range(3)
                {"id": 0, "position": (250, 250), "speed": 20, "direction": "north", "status": "moving"},
            ]
        }
        # print(f"1번 쓰레드: 차량 및 주차 정보 생성: {tracking_data}")
        yolo_data_queue.put(tracking_data)  # 데이터 큐에 넣기
        i += 1  # 인덱스 증가
        time.sleep(3)  # 1초 간격으로 데이터 생성


if __name__ == "__main__":
    yolo_data_queue = queue.Queue()
    track_vehicles(yolo_data_queue)