import socketio
import time
import queue

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
            print(f"Sending path: {route_data}")

            # 서버로 데이터 전송
            sio.emit('message', route_data)

        except queue.Empty:
            # Queue가 비었을 때는 잠시 대기
            time.sleep(1)
            continue

if __name__ == "__main__":
    uri = "http://localhost:5002"  # Socket.IO는 ws:// 대신 http:// 사용
    route_data_queue = queue.Queue()
    send_to_server(uri, route_data_queue)
