from typing import List

import cv2
import mediapipe as mp
import time
import math
import numpy as np

import threading
import time
import serial
import serial.tools.list_ports
from sympy import *

# 自定义变量

ser = serial.Serial('/dev/ttyS0', baudrate=9600, timeout=1)


class handDetctor():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True, ):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 转换为rgb
        self.results = self.hands.process(imgRGB)

        # print(results.multi_hand_landmarks)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)

        return img

    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                # 获取手指关节点
                h, w, c = img.shape
                cx, cy, cz = int(lm.x * w), int(lm.y * h), int(lm.z * 200)
                lmList.append([id, cx, cy, cz])
                cv2.putText(img, str(int(id)), (cx + 10, cy + 10), cv2.FONT_HERSHEY_PLAIN,  # 显示关节坐标
                            1, (0, 0, 255), 2)

        return lmList

        # 返回列表 包含每个手指的开合状态

    def fingerStatus(self, lmList):
        fingerList = []
        id, originx, originy, originz = lmList[0]
        keypoint_list = [[2, 4], [6, 8], [10, 12], [14, 16], [18, 20]]
        for point in keypoint_list:
            id, x1, y1, z1 = lmList[point[0]]
            id, x2, y2, z2 = lmList[point[1]]
            if math.hypot(x2 - originx, y2 - originy) > math.hypot(x1 - originx, y1 - originy):
                fingerList.append(True)
            else:
                fingerList.append(False)

        if (fingerList[0] == True and fingerList[1] == True and fingerList[2] == False and fingerList[3] == False and
                fingerList[4 == False]):
            return True
        else:
            return False

    def findFlowState(self, lmList):
        fingerList = []
        id, originx, originy, originz = lmList[0]
        keypoint_list = [[2, 4], [6, 8], [10, 12], [14, 16], [18, 20]]
        for point in keypoint_list:
            id, x1, y1, z1 = lmList[point[0]]
            id, x2, y2, z2 = lmList[point[1]]
            if math.hypot(x2 - originx, y2 - originy) > math.hypot(x1 - originx, y1 - originy):
                fingerList.append(True)
            else:
                fingerList.append(False)

        if fingerList[0] == True and fingerList[1] == True and fingerList[2] == True and fingerList[3] == True and \
                fingerList[4] == True:
            return 1
        else:
            return 2


class myLimit():
    def __init__(self, xLimit, yLimit, key):
        self.xLimit = xLimit
        self.yLimit = yLimit
        self.key = key

    def getValue(self):
        print(self.xLimit)
        print(self.yLimit)
        print(self.key)


def change(list, limit):
    # print("=================")
    # for i in range(26):
    #     limit[i].getValue()
    for i in range(26):
        if limit[i].xLimit[0] < list[1] < limit[i].xLimit[1] and limit[i].yLimit[0] < list[2] < limit[i].yLimit[1]:
            print(limit[i].key)


def main():
    cap = cv2.VideoCapture(0)
    # 帧率统计
    pTime = 0
    cTime = 0
    lastState = 0
    lastTime = 0
    lastAngle = 0;
    AngleError = 0
    AngleSum = 0
    AngleFlag = 1
    lastangle = AngleSum  #
    HEX = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '0A', '0b', '0c', '0d', '0e', '0f', \
           '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1A', '1b', '1c', '1d', '1e', '1f', \
           '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '2A', '2b', '2c', '2d', '2e', '2f', \
           '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '3A', '3b', '3c', '3d', '3e', '3f', \
           '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '4A', '4b', '4c', '4d', '4e', '4f', \
           '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '5A', '5b', '5c', '5d', '5e', '5f', \
           '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '6A', '6b', '6c', '6d', '6e', '6f', \
           '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '7A', '7b', '7c', '7d', '7e', '7f', \
           '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '8A', '8b', '8c', '8d', '8e', '8f', \
           '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '9A', '9b', '9c', '9d', '9e', '9f', \
           'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'aA', 'ab', 'ac', 'ad', 'ae', 'af', \
           'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'bA', 'bb', 'bc', 'bd', 'be', 'bf', \
           'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'cA', 'cb', 'cc', 'cd', 'ce', 'cf', \
           'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'dA', 'db', 'dc', 'dd', 'de', 'df', \
           'e0', 'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9', 'eA', 'eb', 'ec', 'ed', 'ee', 'ef', \
           'f0', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'fA', 'fb', 'fc', 'fd', 'fe', 'ff', \
           ]

    array = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    detector = handDetctor()
    allList = []
    allList.append(myLimit([5, 20], [230, 250], 'A'))
    allList.append(myLimit([280, 290], [290, 310], 'B'))
    allList.append(myLimit([150, 160], [290, 310], 'C'))
    allList.append(myLimit([130, 140], [230, 250], 'D'))
    allList.append(myLimit([100, 120], [160, 180], 'E'))
    allList.append(myLimit([190, 200], [230, 250], 'F'))
    allList.append(myLimit([250, 270], [230, 250], 'G'))
    allList.append(myLimit([320, 340], [230, 250], 'H'))
    allList.append(myLimit([430, 450], [160, 180], 'I'))
    allList.append(myLimit([390, 410], [230, 250], 'J'))
    allList.append(myLimit([460, 470], [230, 250], 'K'))
    allList.append(myLimit([510, 520], [230, 250], 'L'))
    allList.append(myLimit([410, 430], [290, 310], 'M'))
    allList.append(myLimit([360, 370], [290, 310], 'N'))
    allList.append(myLimit([490, 500], [160, 180], 'O'))
    allList.append(myLimit([560, 580], [160, 180], 'P'))
    allList.append(myLimit([-10, 20], [160, 180], 'Q'))
    allList.append(myLimit([160, 170], [160, 180], 'R'))
    allList.append(myLimit([60, 80], [230, 250], 'S'))
    allList.append(myLimit([230, 240], [160, 180], 'T'))
    allList.append(myLimit([360, 380], [160, 180], 'U'))
    allList.append(myLimit([220, 230], [290, 310], 'V'))
    allList.append(myLimit([40, 60], [160, 180], 'W'))
    allList.append(myLimit([100, 110], [290, 310], 'X'))
    allList.append(myLimit([300, 310], [160, 180], 'Y'))
    allList.append(myLimit([30, 50], [290, 310], 'Z'))

    while True:
        success, img = cap.read()
        # img = cv2.flip(img,1)
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)
        array = np.roll(array, -1)

        if len(lmList) != 0:
            if detector.findFlowState(lmList) == 1:
                id1, x1, y1, z1 = lmList[1]
                id2, x2, y2, z2 = lmList[8]
                if x2 - x1 != 0:
                    angle = (atan((y2 - y1) / (x2 - x1))) * 57.3
                    if x2 - x1 > 0 and y2 - y1 > 0:
                        # print("第四象限")
                        angle = 360 - angle
                    elif x2 - x1 > 0 and y2 - y1 < 0:
                        # print("第一象限")
                        angle = -angle
                    if x2 - x1 < 0 and y2 - y1 > 0:
                        # print("第三象限")
                        angle = 180 - angle
                    elif x2 - x1 < 0 and y2 - y1 < 0:
                        # print("第二象限")
                        angle = 90 + (90 - angle)
                    # print("当前角度", angle)
                    if AngleFlag == 1:
                        lastAngle = angle
                        AngleFlag = 0

                    AngleError = (angle - lastAngle)
                    #print("AngleErroe = ",AngleError)

                    if AngleError >1 and AngleError <30 :
                        AngleSum = AngleSum +1
                    if AngleError <-1 and AngleError >-30 :
                        AngleSum = AngleSum -1
                    lastAngle = angle
                    #AngleSum = AngleSum + AngleError
                    if (AngleSum > 255):
                        AngleSum = 255
                    elif AngleSum < 0:
                        AngleSum = 0

                    #print("AngleSum = ",AngleSum)

            elif detector.findFlowState(lmList) == 2:
                AngleFlag = 1
        AngleSum = round(AngleSum)
        if lastangle != AngleSum:
            lastangle = AngleSum
            txbuf = str(lastangle)
            ser.write(txbuf.encode())
            print(str(txbuf))

        # 统计屏幕帧率
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        cv2.putText(img, str(int(AngleSum)), (500, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        cv2.imshow("image", img)
        if cv2.waitKey(2) & 0xFF == 27:
            # 关闭串口
            ser.close()
            break

    cap.release()


if __name__ == '__main__':
    main()
