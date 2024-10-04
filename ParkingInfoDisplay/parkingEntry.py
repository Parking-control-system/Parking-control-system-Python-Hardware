import requests, json
from datetime import datetime

while True:

    num = input()
    url = "http://localhost:8080/api"
    # 현재 시간 가져오기
    now = datetime.now()

    # 원하는 형식으로 포맷팅
    formatted_time = now.strftime("%Y-%m-%dT%H:%M")
    carId = input()
    
    if num == "1":
        print("입차")

        data = {
            "carId": carId,
            "entryTime": formatted_time,
            "carType": "중형"
        }

        print(formatted_time)

        response = requests.post(url + "/entry", json=data)

        print(response.status_code)
        print(response.json())
        print(response.json()["code"])

    if num == "2":
        print("출차")
        
        data = {
            "carId": carId,
            "exitTime": formatted_time
        }

        response = requests.post(url + "/exit", json=data)

        print(response.status_code)
        print(response.json())
        print(response.json()["code"])
