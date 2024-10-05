import threading
import time
import queue
import yolo_tracking as yolo
import test_file.yolo_tracking_mock as yolo_mock
import shortest_route as sr
import send_to_server as server
import uart

URI = "ws://127.0.0.1:5002"

# 프로그램 종료 플래그
stop_event = threading.Event()
init_event = threading.Event()

# 공유할 데이터 큐
yolo_data_queue = queue.Queue()
car_number_data_queue = queue.Queue()
route_data_queue = queue.Queue()

# 4. 경로를 서버와 Arduino로 전송 (무한 반복)
def send_path_to_server_and_arduino():
    while not stop_event.is_set():
        # print("경로를 서버와 Arduino로 전송 중...")
        time.sleep(5)

# 쓰레드 생성
thread1 = threading.Thread(target=yolo.main, kwargs={"yolo_data_queue": yolo_data_queue, "event": init_event})
# thread1 = threading.Thread(target=yolo_mock.track_vehicles, kwargs={"yolo_data_queue": yolo_data_queue})
thread2 = threading.Thread(target=sr.main, kwargs={"yolo_data_queue": yolo_data_queue, "car_number_data_queue": car_number_data_queue, "route_data_queue": route_data_queue, "event": init_event})
thread3 = threading.Thread(target=uart.get_car_number, kwargs={"car_number_data_queue": car_number_data_queue})
thread4 = threading.Thread(target=server.send_to_server, kwargs={"uri": URI, "route_data_queue": route_data_queue})

# 쓰레드 시작
thread1.start()
thread2.start()
thread3.start()
thread4.start()

try:
    # 메인 프로그램을 무한 대기 상태로 유지
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # 키보드 인터럽트 발생 시 쓰레드 종료
    print("프로그램 종료 중...")
    stop_event.set()

# 모든 쓰레드가 종료될 때까지 대기
thread1.join()
thread2.join()
thread3.join()
thread4.join()

print("프로그램이 정상적으로 종료되었습니다.")
