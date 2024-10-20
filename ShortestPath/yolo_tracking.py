import queue

import cv2
import torch
import numpy as np
from ultralytics import YOLO

def main(yolo_data_queue, event):
    yolo_data_queue.put({
        "vehicles": {# 1: {"position": (1430, 771), "speed": 20, "direction": "north", "status": "moving"},
                     #2: {"position": (1173, 769), "speed": 20, "direction": "north", "status": "moving"},
            }})

    event.wait()

    track_vehicles(yolo_data_queue)

# 이전 프레임의 객체 위치를 저장하기 위한 전역 변수
previous_positions = {}


def calculate_speed_and_direction(previous_position, current_position):
    dx = current_position[0] - previous_position[0]
    dy = current_position[1] - previous_position[1]

    # 속도 계산 (유클리드 거리 계산)
    speed = np.sqrt(dx ** 2 + dy ** 2)

    # 방향 계산
    if abs(dx) > abs(dy):
        direction = "east" if dx > 0 else "west"
    else:
        direction = "north" if dy < 0 else "south"

    return speed, direction

# TODO 1: 차량을 추적하는 모델로 변경
# TODO 2: 좌표 확인을 위해 __main__ 함수에 테스트 코드 작성

def track_vehicles(yolo_data_queue, video_source=0,
                   # model_path='/Users/kyumin/python-application/carDetection/YOLOv8_car_model/yolov8-car3/weights/best.pt',
                   model_path='yolov8s.pt',
                   img_size=680):
    # YOLOv8 모델 로드
    model = YOLO(model_path)

    # 웹캠 비디오 캡처 설정
    cap = cv2.VideoCapture(video_source)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 객체 탐지 및 추적
        results = model.track(frame, tracker="bytetrack.yaml", imgsz=img_size)

        # 객체 정보 저장을 위한 리스트
        tracked_objects = {}

        # 탐지 결과 처리
        if len(results):
            for track in results[0].boxes:
                box = track.xyxy[0].cpu().numpy()  # 박스 좌표
                conf = float(track.conf.cpu().numpy())  # 신뢰도를 부동소수점 값으로 변환
                cls = int(track.cls.cpu().numpy())  # 클래스도 정수로 변환

                # 신뢰도 필터: 0.7 이상만 처리
                if conf >= 0.7:
                    # 객체 ID가 None인지 확인
                    if track.id is not None:
                        id = int(track.id.cpu().numpy())  # 객체 ID를 정수로 변환
                    else:
                        id = 'N/A'  # None이면 ID가 없다는 표시로 'N/A' 할당

                    x1, y1, x2, y2 = map(int, box)
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    current_position = (center_x, center_y)

                    # 이전 위치가 있는 경우 속도와 방향 계산
                    if id in previous_positions:
                        previous_position = previous_positions[id]
                        speed, direction = calculate_speed_and_direction(previous_position, current_position)
                        status = "moving" if speed > 1 else "stopped"  # 속도가 1 이상이면 moving, 그렇지 않으면 stopped
                    else:
                        speed = 0
                        direction = "N/A"
                        status = "stopped"

                    # 현재 위치를 저장
                    previous_positions[id] = current_position

                    # 객체 정보 저장
                    tracked_objects[id] = {
                        "position": current_position,
                        "speed": speed,
                        "direction": direction,
                        "status": status
                    }

                    # 라벨 표시
                    label = f'ID:{id} {model.names[cls]} {conf:.2f} {status}'
                    color = (255, 0, 0) if cls == 1 else (0, 0, 255) if cls == 0 else (0, 255, 0)
                    plot_one_box([x1, y1, x2, y2], frame, label=label, color=color, line_thickness=2)

        # 객체 정보 출력 (콘솔)
        # if tracked_objects:
        #     print(tracked_objects)
        print("yolo_tracking: ", tracked_objects)
        yolo_data_queue.put({"vehicles": tracked_objects})

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def plot_one_box(xyxy, img, label=None, color=(255, 0, 0), line_thickness=3):
    c1, c2 = (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3]))
    cv2.rectangle(img, c1, c2, color, thickness=line_thickness, lineType=cv2.LINE_AA)
    if label:
        font_scale = 0.5
        font_thickness = max(line_thickness - 1, 1)
        t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
        c2 = (c1[0] + t_size[0], c1[1] - t_size[1] - 3)
        cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)
        cv2.putText(img, label, (c1[0], c1[1] - 2), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255),
                    font_thickness, cv2.LINE_AA)


if __name__ == '__main__':
    que = queue.Queue()
    track_vehicles(que)
