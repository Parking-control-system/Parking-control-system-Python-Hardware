import time

def track_vehicles(yolo_data_queue):
    i = 0
    while True:
        # 차량과 주차 공간 정보 생성 (예시 데이터)
        tracking_data = {
            "vehicles": [
                {"id": i, "position": (i * 10, i * 20), "speed": 20 + i, "direction": "north", "status": "moving"},
            ] for i in range(10)
            # "parking_spaces": [
            #     {"id": 100 + i, "position": (i * 15, i * 25), "is_empty": (i % 2 == 0), "vehicle_id": None if i % 2 == 0 else i},
            # ]
        }
        print(f"1번 쓰레드: 차량 및 주차 정보 생성: {tracking_data}")
        # yolo_data_queue.put(tracking_data)  # 데이터 큐에 넣기
        i += 1  # 인덱스 증가
        time.sleep(1)  # 1초 간격으로 데이터 생성