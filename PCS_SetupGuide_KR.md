# PCS_SetupGuide

Parking Control System 셋업 가이드

## 젯슨 오린 나노 (JetPack v5.1.4)

### 서버

1. [PCS-Hardware](https://github.com/Parking-control-system/Parking-control-system-Python-Hardware)에서 서버 코드(FlaskServer)를 다운로드

2. 라이브러리 설치 (가상 환경 이용해도 무관)

```
pip install Flask
```

3. 서버 실행

```
python3 app.py
```

### 메인 프로그램

1. [PCS-Hardware](https://github.com/Parking-control-system/Parking-control-system-Python-Hardware)에서 메인 코드(ShortestPath)를 다운로드

2. 아래의 명령어를 통해 도커 이미지를 실행

```
xhost +
sudo docker run -it --ipc=host --runtime nvidia \
    --privileged \
    --device /dev/video0 \
    --device /dev/video1 \
    --device /dev/ttpTHS0 \
    --device /dev/ttpACM0 \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix/:/tmp/.X11-unix \
    -v /tmp/argus_socket:/tmp/argus_socket \
    -v /etc/nvidia-container-runtime/host-files-for-container.d:/etc/nvidia-container-runtime/host-files-for-container.d \
    -v /home/{폴더의 경로}:/workspace \
    --network host \
    ultralytics/ultralytics:latest-jetson-jetpack5
```

3. position_file/draw_poligon.py를 통해 좌표 파일 생성

4. 라이브러리 설치

```
pip3 install pyserial
pip3 install "python-socketio[client]"
pip3 install deep_sort_realtime --no-deps
```

5. 프로그램 실행

```
python3 main.py
```

## 젯슨 나노

###
