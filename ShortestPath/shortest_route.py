def calculate_optimal_path(yolo_data_queue, car_number_data_queue):
    while True:
        # 큐에서 데이터 가져오기
        tracking_data = yolo_data_queue.get()
        if tracking_data is None:  # 종료 신호 (None) 받으면 종료
            break

        # 데이터 처리 (예: 차량의 속도 계산)
        vehicles = tracking_data["vehicles"]
        parking_spaces = tracking_data["parking_spaces"]

        for vehicle in vehicles:
            print(f"2번 쓰레드: 차량 {vehicle['id']}의 속도: {vehicle['speed']} km/h")
        
        for space in parking_spaces:
            status = "빈 공간" if space["is_empty"] else f"차량 {space['vehicle_id']} 주차 중"
            print(f"2번 쓰레드: 주차 공간 {space['id']} 상태: {status}")

        if car_number_data_queue.qsize() > 0:
            car_number = car_number_data_queue.get()
            print(f"2번 쓰레드: 라즈베리 파이로부터 수신한 차량 번호: {car_number}")

        yolo_data_queue.task_done()  # 처리 완료 신호