from deep_sort_realtime.deepsort_tracker import DeepSort
from ultralytics import YOLO
import cv2

GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

# model_path: YOLO 모델 경로 수정 필요
def detect_objects(video_source=0,
                   model_path='/Users/kyumin/python-application/carDetection/PCS-model/yolov8_v3/weights/best.pt'):

    model = YOLO(model_path)
    cap = cv2.VideoCapture(video_source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 560)

    # DeepSORT 초기화
    tracker = DeepSort(max_age=100, n_init=1, max_iou_distance=1)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Cam Error")
            break

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
                if conf < 0.7:
                    continue

                xmin, ymin, xmax, ymax = int(data[0]), int(data[1]), int(data[2]), int(data[3])
                label = int(data[5])

                dets.append([[xmin, ymin, xmax - xmin, ymax - ymin], conf, label])

        tracks = tracker.update_tracks(dets, frame=frame)

        for track in tracks:
            print("track", track)

            if not track.is_confirmed():
                continue

            track_id = track.track_id
            ltrb = track.to_ltrb()

            xmin, ymin, xmax, ymax = int(ltrb[0]), int(ltrb[1]), int(ltrb[2]), int(ltrb[3])
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), GREEN, 2)
            cv2.rectangle(frame, (xmin, ymin - 20), (xmin + 20, ymin), GREEN, -1)
            cv2.putText(frame, str(track_id), (xmin + 5, ymin - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 2)

        cv2.imshow('Tracking', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    detect_objects()