import cv2
import numpy as np

# 전역 변수 초기화
parking_zones = []
current_polygon = []
max_zones = 22

# 마우스 콜백 함수
def draw_polygon(event, x, y, flags, param):
    global current_polygon, image_copy

    # 마우스 왼쪽 클릭 시 점 추가
    if event == cv2.EVENT_LBUTTONDOWN:
        current_polygon.append((x, y))

    # 실시간으로 선을 그리기 위해 마우스 이동 중 그리기
    if event == cv2.EVENT_MOUSEMOVE and current_polygon:
        image_copy = image.copy()  # 원본 이미지 복사
        for zone in parking_zones:
            # 기존 다각형 그리기
            cv2.polylines(image_copy, [np.array(zone)], isClosed=True, color=(0, 255, 0), thickness=2)
        # 현재 그리는 다각형 그리기
        pts = np.array(current_polygon + [(x, y)], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(image_copy, [pts], isClosed=False, color=(255, 0, 0), thickness=2)

# 이미지 불러오기
image = cv2.imread('/Users/kyumin/Parking-control-system-Python-Hardware/ShortestPath/test_file/test_2.png')
image_copy = image.copy()

# 윈도우 설정 및 마우스 콜백 함수 등록
cv2.namedWindow('Parking Zones')
cv2.setMouseCallback('Parking Zones', draw_polygon)

while True:
    cv2.imshow('Parking Zones', image_copy)
    key = cv2.waitKey(1) & 0xFF

    # Enter 키를 누르면 현재 다각형을 확정하고 저장
    if key == 13:  # Enter 키
        if len(current_polygon) > 2:
            parking_zones.append(current_polygon)
            current_polygon = []
            print(f"Zone {len(parking_zones)} added.")

            # 만약 22개 구역이 다 그려지면 종료
            if len(parking_zones) >= max_zones:
                print("All parking zones have been defined.")
                break

    # ESC 키를 누르면 종료
    elif key == 27:  # ESC 키
        break

cv2.destroyAllWindows()

# 결과 출력
print("Parking zones coordinates:")
for idx, zone in enumerate(parking_zones):
    print(f"Zone {idx+1}: {zone}")
