import cv2
import mediapipe as mp
import math
import HandTrackingModule as htm
import time
import serial

# ser = serial.Serial('/dev/ttyS0', baudrate=9600, timeout=1)  # 串口初始化

wCam, hCam = 640, 480
cTime = 0
pTime = 0
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(detectionCon=0.7)

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        # print(lmList[4], lmList[8])
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)  # 计算两点之间的距离
        print(int(length) + 100)
        txbuf = str(int(length) + 100)  # 发送角度
        # ser.write(txbuf.encode())
        time.sleep(0.1)
        if length > 150:
            length = 150
        cv2.putText(img, f'Water flow size: {int(length)}', (40, 50), cv2.FONT_HERSHEY_PLAIN,
                    2, (255, 0, 0), 2)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.imshow("IMG", img)
    key = cv2.waitKey(1) & 0xFF  # 按键处理
    if key == ord('q'):  # 当按下 'q' 键时退出循环
        break

cap.release()
cv2.destroyAllWindows()
