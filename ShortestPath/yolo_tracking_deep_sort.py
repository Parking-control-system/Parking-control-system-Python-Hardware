import queue
from deep_sort_realtime.deepsort_tracker import DeepSort
import cv2
from ultralytics import YOLO
import platform

def main(yolo_data_queue, event, model_path, video_source=0):

    model = YOLO(model_path)
    if platform.system() == "Darwin":
        cap = cv2.VideoCapture(video_source)
    elif platform.system() == "Linux":
        cap = cv2.VideoCapture(video_source, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 560)

    # DeepSORT 초기화
    tracker = DeepSort(max_age=100, n_init=1, max_iou_distance=1)

    for _ in range(3):
        one_frame(cap, model, tracker, yolo_data_queue)

    event.wait()

    while True:
        one_frame(cap, model, tracker, yolo_data_queue)

    cap.release()
    cv2.destroyAllWindows()

def one_frame(cap, model, tracker, yolo_data_queue):
    ret, frame = cap.read()
    if not ret:
        print("Cam Error")
        return

    # YOLOv8로 객체 탐지 수행
    results = model(frame)

    # 탐지 결과 추출
    detections = results[0]  # 단일 이미지이므로 첫 번째 결과 사용
    dets = []

    if detections.boxes is not None:
        for data in detections.boxes.data.tolist():  # Boxes 객체
            # 바운딩 박스 좌표 및 신뢰도 추출
            print(data)
            conf = float(data[4])  # 신뢰도 추출
            if conf < 0.8:
                continue

            xmin, ymin, xmax, ymax = int(data[0]), int(data[1]), int(data[2]), int(data[3])
            label = int(data[5])

            dets.append([[xmin, ymin, xmax - xmin, ymax - ymin], conf, label])

    tracks = tracker.update_tracks(dets, frame=frame)

    # 객체 정보 저장을 위한 딕셔너리
    tracked_objects = {}

    for track in tracks:

        if not track.is_confirmed():
            continue

        track_id = track.track_id
        ltrb = track.to_ltrb()

        xmin, ymin, xmax, ymax = int(ltrb[0]), int(ltrb[1]), int(ltrb[2]), int(ltrb[3])
        x_center = (xmin + xmax) // 2
        y_center = (ymin + ymax) // 2

        # 딕셔너리에 저장
        tracked_objects[track_id] = {'position': (x_center, y_center)}

    # 객체 정보를 큐에 저장
    print("yolo_tracking: ", tracked_objects)
    yolo_data_queue.put({"vehicles": tracked_objects})


if __name__ == '__main__':
    que = queue.Queue()
