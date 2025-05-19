#include <LedControl.h>
#include <ArduinoJson.h>

// 1,2,3 번 매트릭스 제어 
// 핀 구성 설정
// 1번째 모듈
#define DATA_PIN1 13   // 데이터 핀
#define CLK_PIN1  12   // 클록 핀
#define CS_PIN1 11  // 첫 번째 모듈의 칩 선택 핀
#define CS_PIN2 10    // 두 번째 모듈의 칩 선택 핀
#define CS_PIN3 9    // 세 번째 모듈의 칩 선택 핀
#define CS_PIN4 8   // 네 번째 모듈의 칩 선택 핀
// 2번째 모듈
#define DATA_PIN2 7  // 데이터 핀
#define CLK_PIN2  6   // 클록 핀
#define CS_PIN5 5   // 다섯 번째 모듈의 칩 선택 핀
#define CS_PIN6 4    // 여섯 번째 모듈의 칩 선택 핀
#define CS_PIN7 3    // 일곱 번째 모듈의 칩 선택 핀
#define CS_PIN8 2    // 여덟 번째 모듈의 칩 선택 핀
// 3번째 모듈
#define DATA_PIN3 22   // 데이터 핀
#define CLK_PIN3  23  // 클록 핀
#define CS_PIN9 24  // 아홉 번째 모듈의 칩 선택 핀
#define CS_PIN10 25   // 열 번째 모듈의 칩 선택 핀
#define CS_PIN11 26   // 열한 번째 모듈의 칩 선택 핀
#define CS_PIN12 27   // 열두 번째 모듈의 칩 선택 핀

// 각 8x32 모듈에 대한 LedControl 객체 생성
LedControl lc1 = LedControl(DATA_PIN1, CLK_PIN1, CS_PIN1, 4);
LedControl lc2 = LedControl(DATA_PIN1, CLK_PIN1, CS_PIN2, 4);
LedControl lc3 = LedControl(DATA_PIN1, CLK_PIN1, CS_PIN3, 4);
LedControl lc4 = LedControl(DATA_PIN1, CLK_PIN1, CS_PIN4, 4);
LedControl lc5 = LedControl(DATA_PIN2, CLK_PIN2, CS_PIN5, 4);
LedControl lc6 = LedControl(DATA_PIN2, CLK_PIN2, CS_PIN6, 4);
LedControl lc7 = LedControl(DATA_PIN2, CLK_PIN2, CS_PIN7, 4);
LedControl lc8 = LedControl(DATA_PIN2, CLK_PIN2, CS_PIN8, 4);
LedControl lc9 = LedControl(DATA_PIN3, CLK_PIN3, CS_PIN9, 4);
LedControl lc10 = LedControl(DATA_PIN3, CLK_PIN3, CS_PIN10, 4);
LedControl lc11 = LedControl(DATA_PIN3, CLK_PIN3, CS_PIN11, 4);
LedControl lc12 = LedControl(DATA_PIN3, CLK_PIN3, CS_PIN12, 4);


// 화살표 패턴 정의 (32x32 크기)
byte arrowRight[32][4] = {
  { 0b00000000, 0b00000001, 0b10000000, 0b00000000 },
  { 0b00000000, 0b00000011, 0b11000000, 0b00000000 },
  { 0b00000000, 0b00000111, 0b11100000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00011111, 0b11111000, 0b00000000 },
  { 0b00000000, 0b00111111, 0b11111100, 0b00000000 },
  { 0b00000000, 0b01111111, 0b11111110, 0b00000000 },
  { 0b00000000, 0b11111111, 0b11111111, 0b00000000 },
  { 0b00000001, 0b11111111, 0b11111111, 0b10000000 },
  { 0b00000011, 0b11111111, 0b11111111, 0b11000000 },
  { 0b00000111, 0b11111111, 0b11111111, 0b11100000 },
  { 0b00001111, 0b11111111, 0b11111111, 0b11110000 },
  { 0b00011111, 0b11111111, 0b11111111, 0b11111000 },
  { 0b00111111, 0b11111111, 0b11111111, 0b11111100 },
  { 0b01111111, 0b11111111, 0b11111111, 0b11111110 },
  { 0b11111111, 0b11111111, 0b11111111, 0b11111111 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 }
};


byte arrowLeft[32][4] = {
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b11111111, 0b11111111, 0b11111111, 0b11111111 },
  { 0b01111111, 0b11111111, 0b11111111, 0b11111110 },
  { 0b00111111, 0b11111111, 0b11111111, 0b11111100 },
  { 0b00011111, 0b11111111, 0b11111111, 0b11111000 },
  { 0b00001111, 0b11111111, 0b11111111, 0b11110000 },
  { 0b00000111, 0b11111111, 0b11111111, 0b11100000 },
  { 0b00000011, 0b11111111, 0b11111111, 0b11000000 },
  { 0b00000001, 0b11111111, 0b11111111, 0b10000000 },
  { 0b00000000, 0b11111111, 0b11111111, 0b00000000 },
  { 0b00000000, 0b01111111, 0b11111110, 0b00000000 },
  { 0b00000000, 0b00111111, 0b11111100, 0b00000000 },
  { 0b00000000, 0b00011111, 0b11111000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00000111, 0b11100000, 0b00000000 },
  { 0b00000000, 0b00000011, 0b11000000, 0b00000000 },
  { 0b00000000, 0b00000001, 0b10000000, 0b00000000 }
};


byte arrowDown[32][4] = {
  { 0b00000000, 0b00000001, 0b00000000, 0b00000000 },
  { 0b00000000, 0b00000011, 0b00000000, 0b00000000 },
  { 0b00000000, 0b00000111, 0b00000000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b00000000, 0b00000000 },
  { 0b00000000, 0b00011111, 0b00000000, 0b00000000 },
  { 0b00000000, 0b00111111, 0b00000000, 0b00000000 },
  { 0b00000000, 0b01111111, 0b00000000, 0b00000000 },
  { 0b00000000, 0b11111111, 0b00000000, 0b00000000 },
  { 0b00000001, 0b11111111, 0b00000000, 0b00000000 },
  { 0b00000011, 0b11111111, 0b00000000, 0b00000000 },
  { 0b00000111, 0b11111111, 0b00000000, 0b00000000 },
  { 0b00001111, 0b11111111, 0b00000000, 0b00000000 },
  { 0b00011111, 0b11111111, 0b11111111, 0b11111111 },
  { 0b00111111, 0b11111111, 0b11111111, 0b11111111 },
  { 0b01111111, 0b11111111, 0b11111111, 0b11111111 },
  { 0b11111111, 0b11111111, 0b11111111, 0b11111111 },
  { 0b11111111, 0b11111111, 0b11111111, 0b11111111 },
  { 0b01111111, 0b11111111, 0b11111111, 0b11111111 },
  { 0b00111111, 0b11111111, 0b11111111, 0b11111111 },
  { 0b00011111, 0b11111111, 0b11111111, 0b11111111 },
  { 0b00001111, 0b11111111, 0b00000000, 0b00000000 },
  { 0b00000111, 0b11111111, 0b00000000, 0b00000000 },
  { 0b00000011, 0b11111111, 0b00000000, 0b00000000 },
  { 0b00000001, 0b11111111, 0b00000000, 0b00000000 },
  { 0b00000000, 0b11111111, 0b00000000, 0b00000000 },
  { 0b00000000, 0b01111111, 0b00000000, 0b00000000 },
  { 0b00000000, 0b00111111, 0b00000000, 0b00000000 },
  { 0b00000000, 0b00011111, 0b00000000, 0b00000000 },
  { 0b00000000, 0b00001111, 0b00000000, 0b00000000 },
  { 0b00000000, 0b00000111, 0b00000000, 0b00000000 },
  { 0b00000000, 0b00000011, 0b00000000, 0b00000000 },
  { 0b00000000, 0b00000001, 0b00000000, 0b00000000 }
};




byte arrowUp[32][4] = {
  { 0b00000000, 0b00000000, 0b10000000, 0b00000000 },
  { 0b00000000, 0b00000000, 0b11000000, 0b00000000 },
  { 0b00000000, 0b00000000, 0b11100000, 0b00000000 },
  { 0b00000000, 0b00000000, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00000000, 0b11111000, 0b00000000 },
  { 0b00000000, 0b00000000, 0b11111100, 0b00000000 },
  { 0b00000000, 0b00000000, 0b11111110, 0b00000000 },
  { 0b00000000, 0b00000000, 0b11111111, 0b00000000 },
  { 0b00000000, 0b00000000, 0b11111111, 0b10000000 },
  { 0b00000000, 0b00000000, 0b11111111, 0b11000000 },
  { 0b00000000, 0b00000000, 0b11111111, 0b11100000 },
  { 0b00000000, 0b00000000, 0b11111111, 0b11110000 },
  { 0b11111111, 0b11111111, 0b11111111, 0b11111000 },
  { 0b11111111, 0b11111111, 0b11111111, 0b11111100 },
  { 0b11111111, 0b11111111, 0b11111111, 0b11111110 },
  { 0b11111111, 0b11111111, 0b11111111, 0b11111111 },
  { 0b11111111, 0b11111111, 0b11111111, 0b11111111 },
  { 0b11111111, 0b11111111, 0b11111111, 0b11111110 },
  { 0b11111111, 0b11111111, 0b11111111, 0b11111100 },
  { 0b11111111, 0b11111111, 0b11111111, 0b11111000 },
  { 0b00000000, 0b00000000, 0b11111111, 0b11110000 },
  { 0b00000000, 0b00000000, 0b11111111, 0b11100000 },
  { 0b00000000, 0b00000000, 0b11111111, 0b11000000 },
  { 0b00000000, 0b00000000, 0b11111111, 0b10000000 },
  { 0b00000000, 0b00000000, 0b11111111, 0b00000000 },
  { 0b00000000, 0b00000000, 0b11111110, 0b00000000 },
  { 0b00000000, 0b00000000, 0b11111100, 0b00000000 },
  { 0b00000000, 0b00000000, 0b11111000, 0b00000000 },
  { 0b00000000, 0b00000000, 0b11110000, 0b00000000 },
  { 0b00000000, 0b00000000, 0b11100000, 0b00000000 },
  { 0b00000000, 0b00000000, 0b11000000, 0b00000000 },
  { 0b00000000, 0b00000000, 0b10000000, 0b00000000 }
};


// 비트 반전 함수
byte reverseBits(byte b) {
  byte reversed = 0;
  for (int i = 0; i < 8; i++) {
    if (b & (1 << i)) {
      reversed |= (1 << (7 - i));
    }
  }
  return reversed;
}

// 특정 모듈에 화살표 패턴을 표시하는 함수
void displayArrow(byte pattern[32][4], LedControl* lcGroup[], int groupSize) {
  for (uint8_t row = 0; row < 8; row++) {
    for (int i = 0; i < groupSize; i++) {
      lcGroup[i]->setRow(0, row, reverseBits(pattern[row + (i * 8)][0]));
      lcGroup[i]->setRow(1, row, reverseBits(pattern[row + (i * 8)][1]));
      lcGroup[i]->setRow(2, row, reverseBits(pattern[row + (i * 8)][2]));
      lcGroup[i]->setRow(3, row, reverseBits(pattern[row + (i * 8)][3]));
    }
  }
}

// 모든 매트릭스를 끄는 함수
void turnOffAllMatrices() {
  LedControl* lcModules[] = {&lc1, &lc2, &lc3, &lc4, &lc5, &lc6, &lc7, &lc8, &lc9, &lc10, &lc11, &lc12};
  for (int i = 0; i < 12; i++) {
    for (int j = 0; j < 4; j++) {
      lcModules[i]->clearDisplay(j);  // 디스플레이를 끄기
    }
  }
}

// LedControl 객체를 초기화하는 함수
void initializeModules() {
  LedControl* lcModules[] = {&lc1, &lc2, &lc3, &lc4, &lc5, &lc6, &lc7, &lc8, &lc9, &lc10, &lc11, &lc12};
  for (int i = 0; i < 12; i++) {
    for (int j = 0; j < 4; j++) {
      lcModules[i]->shutdown(j, false);  // 매트릭스를 깨우기
      lcModules[i]->setIntensity(j, 8);  // 밝기 설정 (0-15)
      lcModules[i]->clearDisplay(j);     // 디스플레이 초기화
    }
  }
}

const int BUFFER_SIZE = 256; // JSON 데이터의 충분한 버퍼 크기
char jsonBuffer[BUFFER_SIZE];

void setup() {
  Serial.begin(9600); // UART 통신 초기화
  while (!Serial) {
    ; // 시리얼 포트가 연결될 때까지 대기
  }
  Serial.println("Arduino is ready to receive JSON data."); // 아두이노가 준비되었음을 알림

  // LedControl 모듈 초기화
  initializeModules();

  // 처음에는 모든 매트릭스를 끔
  turnOffAllMatrices();
}

void loop() {
  static String lastJson = "";
  // 시리얼 데이터가 있는지 확인
  if (Serial.available() > 0) {
    // 시리얼 데이터를 버퍼에 읽기
    size_t len = Serial.readBytesUntil('\n', jsonBuffer, BUFFER_SIZE);
    jsonBuffer[len] = '\0'; // JSON 문자열의 끝을 null로 설정

    Serial.print("Received JSON: ");
    Serial.println(jsonBuffer);  // 수신된 JSON 데이터를 에코 출력

    // JSON 파싱
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, jsonBuffer);

    if (error) {
      Serial.print("Failed to parse JSON: ");
      Serial.println(error.c_str());  // 오류 메시지 출력
      // 파싱 실패 시 모든 매트릭스를 끔
      turnOffAllMatrices();
    } else {
      String currentJson = String(jsonBuffer);
      if (currentJson != lastJson) {
        lastJson = currentJson;
        // JSON 파싱 성공 시
        for (int i = 1; i <= 3; i++) {
          if (doc.containsKey(String(i))) {
            const char* direction = doc[String(i)]["direction"];
            Serial.print("Car ");
            Serial.print(i);
            Serial.print(" direction: ");
            Serial.println(direction);

            // 올바른 LedControl 객체 그룹 선택
            LedControl* lcGroup[4];
            int groupSize = 4;

            switch (i) {
              case 1:
                lcGroup[0] = &lc1; lcGroup[1] = &lc2; lcGroup[2] = &lc3; lcGroup[3] = &lc4;
                break;
              case 2:
                lcGroup[0] = &lc5; lcGroup[1] = &lc6; lcGroup[2] = &lc7; lcGroup[3] = &lc8;
                break;
              case 3:
                lcGroup[0] = &lc9; lcGroup[1] = &lc10; lcGroup[2] = &lc11; lcGroup[3] = &lc12;
                // 방향을 반대로 변경 (단, 원래 방향으로 돌아오지 않음)
                if (strcmp(direction, "up") == 0) {
                strcpy(direction, "down");  // 상향 -> 하향
              } else if (strcmp(direction, "down") == 0) {
                strcpy(direction, "up");    // 하향 -> 상향
              } else if (strcmp(direction, "left") == 0) {
                strcpy(direction, "right"); // 좌향 -> 우향
              } else if (strcmp(direction, "right") == 0) {
                strcpy(direction, "left");  // 우향 -> 좌향
              }
              break;
            }

            // 방향에 따라 적절한 화살표 표시
            if (strcmp(direction, "up") == 0) {
              displayArrow(arrowUp, lcGroup, groupSize);
            } else if (strcmp(direction, "down") == 0) {
              displayArrow(arrowDown, lcGroup, groupSize);
            } else if (strcmp(direction, "left") == 0) {
              displayArrow(arrowLeft, lcGroup, groupSize);
            } else if (strcmp(direction, "right") == 0) {
              displayArrow(arrowRight, lcGroup, groupSize);
            }
          }
        }
      }
    }
  } else {
    // 데이터가 수신되지 않으면 모든 매트릭스를 끔
    turnOffAllMatrices();
  }
}