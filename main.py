# pip install opencv-python
# pip install googletrans==4.0.0-rc1
# pip install pytesseract
# pip install pyqt5
# pip install pyinstaller

# pyinstaller -w --add-data ./icon.ico;. -F -i ./icon.ico main.py

# 투명하게 (below 3 lines)
# self.setStyleSheet("background:transparent")
# self.setAttribute(Qt.WA_TranslucentBackground)
# self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
# image = cv2.imread(resource_path('1.png')) # 이미지 읽기
# cv2.imwrite('filter_rgb.png', mark) #필터 사진 저장

#파란색 글씨 살리기 구현 못함
#포켓몬 이름 자동 번역

import os
import sys
import threading
import cv2
import googletrans
import pytesseract
import numpy as np
from PIL import ImageGrab
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

def resource_path(relative_path): # pyinstaller 실행 시 참고자료 경로 지정 함수
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
global_txt = ""
global_flag = threading.Event()

def thread_translate():
    global global_txt
    while not global_flag.is_set():
        img = imgage_extraction()
        global_txt = img2txt(img)
def imgage_extraction(): # 특정 화면 캡쳐 후 글자만 남기는 필터 적용
    imgGrab = ImageGrab.grab(bbox=(420, 890, 1510, 1050))
    image = cv2.cvtColor(np.array(imgGrab), cv2.COLOR_RGB2BGR)
    mark = np.copy(image) # image 복사
    #  BGR 제한 값 설정
    blue_threshold = 200
    green_threshold = 200
    red_threshold = 200
    bgr_threshold = [blue_threshold, green_threshold, red_threshold]
    # BGR 흰색 제한 값보다 작으면 검은색으로
    thresholds = (image[:,:,0] < bgr_threshold[0]) \
                & (image[:,:,0] > 55) \
                | (image[:,:,1] < bgr_threshold[1]) \
                | (image[:,:,2] < bgr_threshold[2]) # 노란색 : B > 55
    mark[thresholds] = [0,0,0]
    return mark
def img2txt(mark): # mark에서 텍스트 추출 후 번역
    translator = googletrans.Translator()  # 구글 번역기 선언
    text = pytesseract.image_to_string(mark) # mark에서 텍스트 추출
    text = text.rstrip() #특수문자 제거
    text = text.replace("\n", " ") # 줄 바꿈 제거
    text = text.replace("|", "I")
    text = text.replace("/", "I")
    try:
        translation = translator.translate(text, dest='ko')
        text = translation.text
        text = translation_pokemon(text)
    except:
        text = ""
    return text
def translation_pokemon(text):
    a = "Gulpin"
    b = "꿀꺽몬"
    if a in text:
        text = text.replace("%s"%a, "%s"%b)
        print(text)
    return text

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        self.button1 = QPushButton("Click to run translation", self)
        self.button1.setCheckable(True)
        self.button1.toggled.connect(self.button1_toggle)
        font = self.button1.font()
        font.setPointSize(20)
        font.setBold(True)
        font.setFamily('맑은 고딕')
        self.button1.setFont(font)

        self.button2 = QPushButton("번역기 배경색", self)
        self.button2.setCheckable(True)
        self.button2.toggled.connect(self.button2_toggle)
        font = self.button2.font()
        font.setPointSize(20)
        font.setBold(True)
        font.setFamily('맑은 고딕')
        self.button2.setFont(font)

        self.label = QLabel("GTRT V1.0", self)
        self.label.setAlignment(Qt.AlignCenter)
        font = self.label.font()
        font.setPointSize(15)
        font.setBold(True)
        font.setFamily('맑은 고딕')
        self.label.setFont(font)

        layout = QGridLayout()
        layout.addWidget(self.button1, 0, 0)
        layout.addWidget(self.button2, 1, 0)
        layout.addWidget(self.label, 2, 0)
        self.setLayout(layout)

        # dialog, timer 선언
        self.dialog = QDialog()
        self.subWindow_initUI()
        self.update = QTimer()
        self.update.setInterval(1000)
        self.update.timeout.connect(self.label_updating)

        self.setWindowTitle('GTRT(Game Translator in Real Time)')
        # self.setGeometry(460, 840, 1000, 50) #초기 위치, 창 사이즈
        self.setGeometry(-420, 530, 400, 500) #초기 위치, 창 사이즈
        self.setWindowIcon(QIcon(resource_path('./References/torchic.ico')))
        self.show()
    #button1 토글 식 이벤트
    def button1_toggle(self, state):
        if state:
            self.button1.setText("GTRT : ON")
            self.dialog.show()
            # 화면 번역 스레드 실행
            global_flag.clear()
            thread = threading.Thread(target=thread_translate)
            thread.daemon = True
            thread.start()
            # gui 갱신 스레드 실행
            self.update.start()
        elif not state:
            self.button1.setText("GTRT : OFF")
            global_flag.set()
            self.update.stop()
            self.dialog.close()
    #button2 토글 식 이벤트
    def button2_toggle(self, state):
        self.label_sub.setStyleSheet("%s" \
                                     %({True: "border-radius: 10px; color:white;background-color:rgb(153,153,153)", \
                                        False: "color:white"}[state]))
        self.button2.setText({True: "번역기 배경색 : ON", False: "번역기 배경색 : OFF"}[state])
    # QDialog를 이용한 subWindow 생성
    def subWindow_initUI(self):
        self.label_sub = QLabel("제작자 : 김종헌", self.dialog)
        self.label_sub.setStyleSheet("border-radius: 10px; color:white;background-color:rgb(153,153,153)")
        self.label_sub.setAlignment(Qt.AlignCenter)
        font_sub = self.label_sub.font()
        font_sub.setPointSize(15)
        font_sub.setBold(True)
        font_sub.setFamily('맑은 고딕')
        self.label_sub.setFont(font_sub)

        layout_sub = QGridLayout()
        layout_sub.addWidget(self.label_sub, 0, 0)
        self.dialog.setLayout(layout_sub)

        # 투명하게
        self.dialog.setStyleSheet("background:transparent")
        self.dialog.setAttribute(Qt.WA_TranslucentBackground)
        self.dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # QDialog 세팅
        self.dialog.setWindowTitle('Translating Window')
        self.dialog.setGeometry(460, 840, 1000, 50) # 초기 위치, 창 사이즈
        self.dialog.setWindowIcon(QIcon(resource_path('./References/pikachu.ico')))
    # QTimer를 이용한 자동 실행
    def label_updating(self):
        self.label_sub.setText(global_txt)
        self.label_sub.repaint()
    # 종료 이벤트
    def closeEvent(self, event):
        self.dialog.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    start = MainWindow()
    sys.exit(app.exec_())