# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
import requests, json
from PyQt5.QtCore import QThread, pyqtSignal


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(640, 480)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.aText = QtWidgets.QTextBrowser(self.centralwidget)
        self.aText.setGeometry(QtCore.QRect(110, 60, 141, 111))
        font = QtGui.QFont()
        font.setPointSize(72)
        font.setBold(True)
        font.setWeight(75)
        self.aText.setFont(font)
        self.aText.setPlaceholderText("")
        self.aText.setObjectName("aText")
        self.bText = QtWidgets.QTextBrowser(self.centralwidget)
        self.bText.setGeometry(QtCore.QRect(110, 200, 141, 111))
        font = QtGui.QFont()
        font.setPointSize(72)
        font.setBold(True)
        font.setWeight(75)
        self.bText.setFont(font)
        self.bText.setObjectName("bText")
        self.aNumber = QtWidgets.QTextBrowser(self.centralwidget)
        self.aNumber.setGeometry(QtCore.QRect(310, 60, 141, 111))
        font = QtGui.QFont()
        font.setPointSize(72)
        font.setBold(True)
        font.setWeight(75)
        self.aNumber.setFont(font)
        self.aNumber.setPlaceholderText("")
        self.aNumber.setObjectName("aNumber")
        self.bNumber = QtWidgets.QTextBrowser(self.centralwidget)
        self.bNumber.setGeometry(QtCore.QRect(310, 200, 141, 111))
        font = QtGui.QFont()
        font.setPointSize(72)
        font.setBold(True)
        font.setWeight(75)
        self.bNumber.setFont(font)
        self.bNumber.setObjectName("bNumber")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 37))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.aText.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'.AppleSystemUIFont\'; font-size:72pt; font-weight:600; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">A</p></body></html>"))
        self.bText.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'.AppleSystemUIFont\'; font-size:72pt; font-weight:600; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">B</p></body></html>"))
        self.aNumber.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'.AppleSystemUIFont\'; font-size:72pt; font-weight:600; font-style:normal;\">\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.bNumber.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'.AppleSystemUIFont\'; font-size:72pt; font-weight:600; font-style:normal;\">\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))

class SseThread(QThread):
    data_received = pyqtSignal(list)  # 시그널을 통해 데이터를 전송

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        response = requests.get(self.url, stream=True)
        count = 0
        datas = []
        
        for line in response.iter_lines(decode_unicode=True):
            if line:
                count += 1
                if count <= 2:
                    if line.startswith("data:"):
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
                
                self.data_received.emit(datas)  # 데이터를 전송

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # SSE 스레드 생성 및 연결
        self.sse_thread = SseThread("http://localhost:8080/api/display/status")
        self.sse_thread.data_received.connect(self.update_display)
        self.sse_thread.start()

    def update_display(self, datas):
        for data in datas:
            if data["areaId"] == "A":
                self.aNumber.setText(str(data["allSpace"] - data["occupiedSpace"] - data["reservationSpace"]))
            elif data["areaId"] == "B":
                self.bNumber.setText(str(data["allSpace"] - data["occupiedSpace"] - data["reservationSpace"]))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
