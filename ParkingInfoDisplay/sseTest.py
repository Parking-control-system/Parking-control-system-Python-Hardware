import requests
import json

def sse_client(url):
    response = requests.get(url, stream=True)

    count = 0
    datas = []
    
    for line in response.iter_lines(decode_unicode=True):
        if line:
            count += 1
            # 최초 연결
            if count <= 2:
            # 받은 응답에서 data 부분을 추출
                if line.startswith("data:"):
                    # "data:"를 제거하고 나머지 JSON 문자열을 파싱합니다.
                    json_data = line[len('data:'):]
                    datas = json.loads(json_data)
            else:
                if line.startswith("data:"):
                    json_data = line[len('data:'):]
                    parse_data = json.loads(json_data)
                    
                    for data in datas:
                        if data["areaId"] == parse_data["areaId"]:
                            data["occupiedSpace"] = parse_data["occupiedSpace"]
                            data["reservationSpace"] = parse_data["reservationSpace"]
                
                    print(datas)

                    
                        

if __name__ == "__main__":
    sse_url = "http://localhost:8080/api/display/status"
    sse_client(sse_url)
