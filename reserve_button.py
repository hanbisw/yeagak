from PyQt5 import QtWidgets, uic
import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QGraphicsDropShadowEffect, QFrame, QLabel

from PyQt5.QtCore import QFile, QTextStream
from PyQt5 import QtWidgets, uic
import sys

from PyQt5.QtWidgets import QPushButton, QGraphicsDropShadowEffect, QFrame

from PyQt5.QtCore import QFile, QTextStream
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

form_window = uic.loadUiType("UiDir/reserve_button.ui")[0]


class UiMainWindow(QtWidgets.QMainWindow, form_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # aa = """QMainWindow{background-color: gray;} """
        # self.setStyleSheet(aa)
        # self.setStyleSheet('background: yellow;')
        self.button = QToolButton(self.fr01)

        # self.button = QPushButton('',self.fr01)
        self.button.setStyleSheet("""QToolButton {  
                        border-radius: 10px;
                        background-position: center;
                        background-repeat: no-repeat;
                        color: black;
                        text-align: left;
                        font: 18px;
                        padding-bottom: 15px;
}"""
            """QToolButton { background-color:#86e57f; }"""
            
            """QToolButton::hover { background-color: #3333ff;
    color: #fff;}"""
            """QToolButton::pressed { 
    background-color:#ff2d55; }"""
        )
        # creating a QGraphicsDropShadowEffect object
        shadow = QGraphicsDropShadowEffect()
        # setting blur radius
        shadow.setBlurRadius(15)
        # creating a QGraphicsDropShadowEffect object
        shadow1 = QGraphicsDropShadowEffect()
        # setting blur radius
        shadow1.setBlurRadius(15)
        self.button.setGraphicsEffect(shadow)
        # self.button.move(75, 175)


        a_txt = '누울리나'

        # bt_text ="<h2><i>" + a_txt + "</i> <br> <br> <br> <p style=text-align:center> <font size=20px color=blue>Qt!</font></h2> </p>"
        bt_text = "<h2><font size=7 face=verdana color=white align=center>302호실</font><br><font size=5 face=verdana color=white align=center>(프리미엄 투윈)</font></h2>"
        # aa = myicon(bt_text)
        self.button.setIcon(self.myicon(bt_text))
        # self.button.setIconSize(mypixmap.size())
        self.button.setIconSize(QSize(130, 180))
        self.button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # 아이콘 아래 텍스트



        self.button.setGeometry(10, 10, 300, 200)
        self.button.setText('\n우동균\n\n 일자 : 2024-09-20 ~ 2024-11-20 \n(1박)')
        self.button.setFont(QFont('Arial', 15))
        self.button.setCursor(QCursor(Qt.PointingHandCursor))
        self.button.setToolTip('301호실   우동균')
        # self.button.setAlignment(Qt.AlignLeft)
        self.button.clicked.connect(self.myclick)

        self.button1 = QToolButton(self.fr01)

        # self.button = QPushButton('',self.fr01)
        self.button1.setStyleSheet("""QToolButton {  
                                border-radius: 10px;
                                background-position: center;
                                background-repeat: no-repeat;
                                color: black;
                                text-align: left;
                                font: 18px;
                                padding-bottom: 15px;
        }"""
                                  """QToolButton { background-color: #00a4de; }"""

                                  """QToolButton::hover { background-color: #3333ff;
                          color: #fff;}"""
                                  """QToolButton::pressed { 
                          background-color:#ff2d55; }"""
                                  )
        # creating a QGraphicsDropShadowEffect object
        shadow1 = QGraphicsDropShadowEffect()
        # setting blur radius
        shadow1.setBlurRadius(15)
        self.button1.setGraphicsEffect(shadow1)
        # self.button.move(75, 175)

        a_txt = '누울리나'

        # bt_text ="<h2><i>" + a_txt + "</i> <br> <br> <br> <p style=text-align:center> <font size=20px color=blue>Qt!</font></h2> </p>"
        bt_text = "<h2><font size=7 face=verdana color=white align=center>303호실</font><br><font size=5 face=verdana color=white align=center>(프리미엄 투윈)</font></h2>"
        # aa = myicon(bt_text)
        self.button1.setIcon(self.myicon(bt_text))
        self.button1.setCursor(QCursor(Qt.PointingHandCursor))
        # self.button.setIconSize(mypixmap.size())
        self.button1.setIconSize(QSize(130, 180))
        self.button1.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # 아이콘 아래 텍스트

        self.button1.setGeometry(350, 10, 300, 200)
        self.button1.setText('\nKristina Goryacheva\n\n 일자 : 2024-09-20 ~ 2024-11-20 \n(5박)')
        self.button1.setFont(QFont('Arial', 15))
        # self.button.setAlignment(Qt.AlignLeft)
        self.button1.clicked.connect(self.myclick)

        self.button2 = QToolButton(self.fr01)

        # self.button = QPushButton('',self.fr01)
        self.button2.setStyleSheet("""QToolButton {  
                                border-radius: 10px;
                                background-position: center;
                                background-repeat: no-repeat;
                                color: black;
                                text-align: left;
                                font: 18px;
                                padding-bottom: 15px;
        }"""
                                  """QToolButton { background-color:#2e77bc; }"""

                                  """QToolButton::hover { 
                                  background-color: #217346;
                          color: #fff;}"""
                                  """QToolButton::pressed { 
                          background-color:#3333ff; }"""
                                  )
        # creating a QGraphicsDropShadowEffect object
        shadow2 = QGraphicsDropShadowEffect()
        # setting blur radius
        shadow2.setBlurRadius(15)
        self.button2.setGraphicsEffect(shadow2)
        self.button2.setCursor(QCursor(Qt.PointingHandCursor))
        # self.button.move(75, 175)

        a_txt = '누울리나'

        # bt_text ="<h2><i>" + a_txt + "</i> <br> <br> <br> <p style=text-align:center> <font size=20px color=blue>Qt!</font></h2> </p>"
        bt_text = "<h2><font size=7 face=verdana color=white align=center>305호실</font><br><font size=5 face=verdana color=white align=center>(프리미엄 투윈)</font></h2>"
        # aa = myicon(bt_text)
        self.button2.setIcon(self.myicon(bt_text))
        # self.button.setIconSize(mypixmap.size())
        self.button2.setIconSize(QSize(130, 180))
        self.button2.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # 아이콘 아래 텍스트

        self.button2.setGeometry(690, 10, 300, 200)
        # self.button2.setText('\n\n 일자 : 2024-09-20 ~ 2024-09-21\n 나는 누구일까 \n\n\n')
        self.button2.setFont(QFont('Arial', 15))
        # self.button.setAlignment(Qt.AlignLeft)
        self.button2.clicked.connect(self.myclick)

        self.button3 = QToolButton(self.fr01)

        # self.button = QPushButton('',self.fr01)
        self.button3.setStyleSheet("""QToolButton {  
                                border-radius: 10px;
                                background-position: center;
                                background-repeat: no-repeat;
                                color: black;
                                text-align: left;
                                font: 18px;
                                padding-bottom: 15px;
        }"""
                                  """QToolButton { background-color:#86e57f; }"""

                                  """QToolButton::hover { background-color: #3333ff;
                          color: #fff;}"""
                                  """QToolButton::pressed { 
                          background-color:#ff2d55; }"""
                                  )
        # creating a QGraphicsDropShadowEffect object
        shadow3 = QGraphicsDropShadowEffect()
        # setting blur radius
        shadow3.setBlurRadius(15)
        self.button3.setGraphicsEffect(shadow3)
        # self.button.move(75, 175)

        a_txt = '누울리나'

        # bt_text ="<h2><i>" + a_txt + "</i> <br> <br> <br> <p style=text-align:center> <font size=20px color=blue>Qt!</font></h2> </p>"
        bt_text = "<h2><font size=7 face=verdana color=white align=center>302호실</font><br><font size=5 face=verdana color=white align=center>(프리미엄 투윈)</font></h2>"
        # aa = myicon(bt_text)
        self.button3.setIcon(self.myicon(bt_text))
        # self.button.setIconSize(mypixmap.size())
        self.button3.setIconSize(QSize(130, 180))
        self.button3.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # 아이콘 아래 텍스트

        self.button3.setGeometry(1030, 10, 300, 200)
        self.button3.setText('\n우동균\n\n 일자 : 2024-09-20 ~ 2024-11-20 \n(1박)')
        self.button3.setFont(QFont('Arial', 15))
        self.button3.setCursor(QCursor(Qt.PointingHandCursor))
        # self.button.setAlignment(Qt.AlignLeft)
        self.button3.clicked.connect(self.myclick)

        self.button4 = QToolButton(self.fr01)

        # self.button = QPushButton('',self.fr01)
        self.button4.setStyleSheet("""QToolButton {  
                                        border-radius: 10px;
                                        background-position: center;
                                        background-repeat: no-repeat;
                                        color: black;
                                        text-align: left;
                                        font: 18px;
                                        padding-bottom: 15px;
                }"""
                                   """QToolButton { background-color: #00a4de; }"""

                                   """QToolButton::hover { background-color: #3333ff;
                           color: #fff;}"""
                                   """QToolButton::pressed { 
                           background-color:#ff2d55; }"""
                                   )
        # creating a QGraphicsDropShadowEffect object
        shadow4 = QGraphicsDropShadowEffect()
        # setting blur radius
        shadow4.setBlurRadius(15)
        self.button4.setGraphicsEffect(shadow4)
        # self.button.move(75, 175)

        a_txt = '누울리나'

        # bt_text ="<h2><i>" + a_txt + "</i> <br> <br> <br> <p style=text-align:center> <font size=20px color=blue>Qt!</font></h2> </p>"
        bt_text = "<h2><font size=7 face=verdana color=white align=center>303호실</font><br><font size=5 face=verdana color=white align=center>(프리미엄 투윈)</font></h2>"
        # aa = myicon(bt_text)
        self.button4.setIcon(self.myicon(bt_text))
        self.button4.setCursor(QCursor(Qt.PointingHandCursor))
        # self.button.setIconSize(mypixmap.size())
        self.button4.setIconSize(QSize(130, 180))
        self.button4.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # 아이콘 아래 텍스트

        self.button4.setGeometry(1370, 10, 300, 200)
        self.button4.setText('\nKristina Goryacheva\n\n 일자 : 2024-09-20 ~ 2024-11-20 \n(5박)')
        self.button4.setFont(QFont('Arial', 15))
        # self.button.setAlignment(Qt.AlignLeft)
        self.button4.clicked.connect(self.myclick)

        self.button1_0 = QToolButton(self.fr01)

        # self.button = QPushButton('',self.fr01)
        self.button1_0.setStyleSheet("""QToolButton {  
                                border-radius: 10px;
                                background-position: center;
                                background-repeat: no-repeat;
                                color: black;
                                text-align: left;
                                font: 18px;
                                padding-bottom: 15px;
        }"""
                                     """QToolButton { background-color:#86e57f; }"""

                                     """QToolButton::hover { background-color: #3333ff;
                             color: #fff;}"""
                                     """QToolButton::pressed { 
                             background-color:#ff2d55; }"""
                                     )
        # creating a QGraphicsDropShadowEffect object
        shadow1_0 = QGraphicsDropShadowEffect()
        # setting blur radius
        shadow1_0.setBlurRadius(15)
        self.button1_0.setGraphicsEffect(shadow1_0)
        # self.button.move(75, 175)

        a_txt = '누울리나'

        # bt_text ="<h2><i>" + a_txt + "</i> <br> <br> <br> <p style=text-align:center> <font size=20px color=blue>Qt!</font></h2> </p>"
        bt_text = "<h2><font size=7 face=verdana color=white align=center>302호실</font><br><font size=5 face=verdana color=white align=center>(프리미엄 투윈)</font></h2>"
        # aa = myicon(bt_text)
        self.button1_0.setIcon(self.myicon(bt_text))
        # self.button.setIconSize(mypixmap.size())
        self.button1_0.setIconSize(QSize(130, 180))
        self.button1_0.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # 아이콘 아래 텍스트

        self.button1_0.setGeometry(10, 240, 300, 200)
        self.button1_0.setText('\n우동균\n\n 일자 : 2024-09-20 ~ 2024-11-20 \n(1박)')
        self.button1_0.setFont(QFont('Arial', 15))
        self.button1_0.setCursor(QCursor(Qt.PointingHandCursor))
        # self.button.setAlignment(Qt.AlignLeft)
        self.button1_0.clicked.connect(self.myclick)

        self.button1_1 = QToolButton(self.fr01)

        # self.button = QPushButton('',self.fr01)
        self.button1_1.setStyleSheet("""QToolButton {  
                        border-radius: 10px;
                        background-position: center;
                        background-repeat: no-repeat;
                        color: black;
                        text-align: left;
                        font: 18px;
                        padding-bottom: 15px;
}"""
            """QToolButton { background-color:#86e57f; }"""
            
            """QToolButton::hover { background-color: #3333ff;
    color: #fff;}"""
            """QToolButton::pressed { 
    background-color:#ff2d55; }"""
        )
        # creating a QGraphicsDropShadowEffect object
        shadow1_1 = QGraphicsDropShadowEffect()
        # setting blur radius
        shadow1_1.setBlurRadius(15)
        self.button1_1.setGraphicsEffect(shadow1_1)
        # self.button.move(75, 175)

        a_txt = '누울리나'

        # bt_text ="<h2><i>" + a_txt + "</i> <br> <br> <br> <p style=text-align:center> <font size=20px color=blue>Qt!</font></h2> </p>"
        bt_text = "<h2><font size=7 face=verdana color=white align=center>303호실</font><br><font size=5 face=verdana color=white align=center>(프리미엄 투윈)</font></h2>"
        # aa = myicon(bt_text)
        self.button1_1.setIcon(self.myicon(bt_text))
        self.button1_1.setCursor(QCursor(Qt.PointingHandCursor))
        # self.button.setIconSize(mypixmap.size())
        self.button1_1.setIconSize(QSize(130, 180))
        self.button1_1.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # 아이콘 아래 텍스트

        self.button1_1.setGeometry(350, 240, 300, 200)
        self.button1_1.setText('\nKristina Goryacheva\n\n 일자 : 2024-09-20 ~ 2024-11-20 \n(5박)')
        self.button1_1.setFont(QFont('Arial', 15))
        # self.button.setAlignment(Qt.AlignLeft)
        self.button1_1.clicked.connect(self.myclick)

        self.button1_2 = QToolButton(self.fr01)

        # self.button = QPushButton('',self.fr01)
        self.button1_2.setStyleSheet("""QToolButton {  
                                        border-radius: 10px;
                                        background-position: center;
                                        background-repeat: no-repeat;
                                        color: black;
                                        text-align: left;
                                        font: 18px;
                                        padding-bottom: 15px;
                }"""
                                     """QToolButton { background-color:#2e77bc; }"""

                                     """QToolButton::hover { 
                                     background-color: #217346;
                             color: #fff;}"""
                                     """QToolButton::pressed { 
                             background-color:#3333ff; }"""
                                     )
        # creating a QGraphicsDropShadowEffect object
        shadow1_2 = QGraphicsDropShadowEffect()
        # setting blur radius
        shadow1_2.setBlurRadius(15)
        self.button1_2.setGraphicsEffect(shadow1_2)
        self.button1_2.setCursor(QCursor(Qt.PointingHandCursor))
        # self.button.move(75, 175)

        a_txt = '누울리나'

        # bt_text ="<h2><i>" + a_txt + "</i> <br> <br> <br> <p style=text-align:center> <font size=20px color=blue>Qt!</font></h2> </p>"
        bt_text = "<h2><font size=7 face=verdana color=white align=center>305호실</font><br><font size=5 face=verdana color=white align=center>(프리미엄 투윈)</font></h2>"
        # aa = myicon(bt_text)
        self.button1_2.setIcon(self.myicon(bt_text))
        # self.button.setIconSize(mypixmap.size())
        self.button1_2.setIconSize(QSize(130, 180))
        self.button1_2.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # 아이콘 아래 텍스트

        self.button1_2.setGeometry(690, 240, 300, 200)
        # self.button2.setText('\n\n 일자 : 2024-09-20 ~ 2024-09-21\n 나는 누구일까 \n\n\n')
        self.button1_2.setFont(QFont('Arial', 15))
        # self.button.setAlignment(Qt.AlignLeft)
        self.button1_2.clicked.connect(self.myclick)

        self.button1_3 = QToolButton(self.fr01)

        # self.button = QPushButton('',self.fr01)
        self.button1_3.setStyleSheet("""QToolButton {  
                                        border-radius: 10px;
                                        background-position: center;
                                        background-repeat: no-repeat;
                                        color: black;
                                        text-align: left;
                                        font: 18px;
                                        padding-bottom: 15px;
                }"""
                                     """QToolButton { background-color:#86e57f; }"""

                                     """QToolButton::hover { background-color: #3333ff;
                             color: #fff;}"""
                                     """QToolButton::pressed { 
                             background-color:#ff2d55; }"""
                                     )
        # creating a QGraphicsDropShadowEffect object
        shadow1_3 = QGraphicsDropShadowEffect()
        # setting blur radius
        shadow1_3.setBlurRadius(15)
        self.button1_3.setGraphicsEffect(shadow1_3)
        # self.button.move(75, 175)

        a_txt = '누울리나'

        # bt_text ="<h2><i>" + a_txt + "</i> <br> <br> <br> <p style=text-align:center> <font size=20px color=blue>Qt!</font></h2> </p>"
        bt_text = "<h2><font size=7 face=verdana color=white align=center>302호실</font><br><font size=5 face=verdana color=white align=center>(프리미엄 투윈)</font></h2>"
        # aa = myicon(bt_text)
        self.button1_3.setIcon(self.myicon(bt_text))
        # self.button.setIconSize(mypixmap.size())
        self.button1_3.setIconSize(QSize(130, 180))
        self.button1_3.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # 아이콘 아래 텍스트

        self.button1_3.setGeometry(1030, 240, 300, 200)
        self.button1_3.setText('\n우동균\n\n 일자 : 2024-09-20 ~ 2024-11-20 \n(1박)')
        self.button1_3.setFont(QFont('Arial', 15))
        self.button1_3.setCursor(QCursor(Qt.PointingHandCursor))
        # self.button.setAlignment(Qt.AlignLeft)
        self.button1_3.clicked.connect(self.myclick)

        self.button1_4 = QToolButton(self.fr01)

        # self.button = QPushButton('',self.fr01)
        self.button1_4.setStyleSheet("""QToolButton {  
                                                border-radius: 10px;
                                                background-position: center;
                                                background-repeat: no-repeat;
                                                color: black;
                                                text-align: left;
                                                font: 18px;
                                                padding-bottom: 15px;
                        }"""
                                     """QToolButton { background-color: #00a4de; }"""

                                     """QToolButton::hover { background-color: #3333ff;
                             color: #fff;}"""
                                     """QToolButton::pressed { 
                             background-color:#ff2d55; }"""
                                     )
        # creating a QGraphicsDropShadowEffect object
        shadow1_4 = QGraphicsDropShadowEffect()
        # setting blur radius
        shadow1_4.setBlurRadius(15)
        self.button1_4.setGraphicsEffect(shadow1_4)
        # self.button.move(75, 175)

        a_txt = '누울리나'

        # bt_text ="<h2><i>" + a_txt + "</i> <br> <br> <br> <p style=text-align:center> <font size=20px color=blue>Qt!</font></h2> </p>"
        bt_text = "<h2><font size=7 face=verdana color=white align=center>303호실</font><br><font size=5 face=verdana color=white align=center>(프리미엄 투윈)</font></h2>"
        # aa = myicon(bt_text)
        self.button1_4.setIcon(self.myicon(bt_text))
        self.button1_4.setCursor(QCursor(Qt.PointingHandCursor))
        # self.button.setIconSize(mypixmap.size())
        self.button1_4.setIconSize(QSize(130, 180))
        self.button1_4.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # 아이콘 아래 텍스트

        self.button1_4.setGeometry(1370, 240, 300, 200)
        self.button1_4.setText('\nKristina Goryacheva\n\n 일자 : 2024-09-20 ~ 2024-11-20 \n(5박)')
        self.button1_4.setFont(QFont('Arial', 15))
        # self.button.setAlignment(Qt.AlignLeft)
        self.button1_4.clicked.connect(self.myclick)



        self.button2_0 = QToolButton(self.fr01)

        # self.button = QPushButton('',self.fr01)
        self.button2_0.setStyleSheet("""QToolButton {  
                                border-radius: 10px;
                                background-position: center;
                                background-repeat: no-repeat;
                                color: black;
                                text-align: left;
                                font: 18px;
                                padding-bottom: 15px;
        }"""
                                   """QToolButton { background-color:#2e77bc; }"""

                                   """QToolButton::hover { 
                                   background-color: #217346;
                           color: #fff;}"""
                                   """QToolButton::pressed { 
                           background-color:#3333ff; }"""
                                   )
        # creating a QGraphicsDropShadowEffect object
        shadow2_0 = QGraphicsDropShadowEffect()
        # setting blur radius
        shadow2_0.setBlurRadius(15)
        self.button2_0.setGraphicsEffect(shadow2_0)
        self.button2_0.setCursor(QCursor(Qt.PointingHandCursor))
        # self.button.move(75, 175)

        a_txt = '누울리나'

        # bt_text ="<h2><i>" + a_txt + "</i> <br> <br> <br> <p style=text-align:center> <font size=20px color=blue>Qt!</font></h2> </p>"
        bt_text = "<h2><font size=7 face=verdana color=white align=center>305호실</font><br><font size=5 face=verdana color=white align=center>(프리미엄 투윈)</font></h2>"
        # aa = myicon(bt_text)
        self.button2_0.setIcon(self.myicon(bt_text))
        # self.button.setIconSize(mypixmap.size())
        self.button2_0.setIconSize(QSize(130, 180))
        self.button2_0.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # 아이콘 아래 텍스트

        self.button2_0.setGeometry(10, 470, 300, 200)
        # self.button2.setText('\n\n 일자 : 2024-09-20 ~ 2024-09-21\n 나는 누구일까 \n\n\n')
        self.button2_0.setFont(QFont('Arial', 15))
        # self.button.setAlignment(Qt.AlignLeft)
        self.button2_0.clicked.connect(self.myclick)

        self.button2_1 = QToolButton(self.fr01)

        # self.button = QPushButton('',self.fr01)
        self.button2_1.setStyleSheet("""QToolButton {  
                                border-radius: 10px;
                                background-position: center;
                                background-repeat: no-repeat;
                                color: black;
                                text-align: left;
                                font: 18px;
                                padding-bottom: 15px;
        }"""
                                   """QToolButton { background-color: #00a4de; }"""

                                   """QToolButton::hover { background-color: #3333ff;
                           color: #fff;}"""
                                   """QToolButton::pressed { 
                           background-color:#ff2d55; }"""
                                   )
        # creating a QGraphicsDropShadowEffect object
        shadow2_1 = QGraphicsDropShadowEffect()
        # setting blur radius
        shadow2_1.setBlurRadius(15)
        self.button2_1.setGraphicsEffect(shadow2_1)
        # self.button.move(75, 175)

        a_txt = '누울리나'

        # bt_text ="<h2><i>" + a_txt + "</i> <br> <br> <br> <p style=text-align:center> <font size=20px color=blue>Qt!</font></h2> </p>"
        bt_text = "<h2><font size=7 face=verdana color=white align=center>303호실</font><br><font size=5 face=verdana color=white align=center>(프리미엄 투윈)</font></h2>"
        # aa = myicon(bt_text)
        self.button2_1.setIcon(self.myicon(bt_text))
        self.button2_1.setCursor(QCursor(Qt.PointingHandCursor))
        # self.button.setIconSize(mypixmap.size())
        self.button2_1.setIconSize(QSize(130, 180))
        self.button2_1.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # 아이콘 아래 텍스트

        self.button2_1.setGeometry(350, 470, 300, 200)
        self.button2_1.setText('\nKristina Goryacheva\n\n 일자 : 2024-09-20 ~ 2024-11-20 \n(5박)')
        self.button2_1.setFont(QFont('Arial', 15))
        # self.button.setAlignment(Qt.AlignLeft)
        self.button2_1.clicked.connect(self.myclick)

        self.button2_2 = QToolButton(self.fr01)

        # self.button = QPushButton('',self.fr01)
        self.button2_2.setStyleSheet("""QToolButton {  
                                border-radius: 10px;
                                background-position: center;
                                background-repeat: no-repeat;
                                color: black;
                                text-align: left;
                                font: 18px;
                                padding-bottom: 15px;
        }"""
                                   """QToolButton { background-color:#2e77bc; }"""

                                   """QToolButton::hover { 
                                   background-color: #217346;
                           color: #fff;}"""
                                   """QToolButton::pressed { 
                           background-color:#3333ff; }"""
                                   )
        # creating a QGraphicsDropShadowEffect object
        shadow2_2 = QGraphicsDropShadowEffect()
        # setting blur radius
        shadow2_2.setBlurRadius(15)
        self.button2_2.setGraphicsEffect(shadow2_2)
        self.button2_2.setCursor(QCursor(Qt.PointingHandCursor))
        # self.button.move(75, 175)

        a_txt = '누울리나'

        # bt_text ="<h2><i>" + a_txt + "</i> <br> <br> <br> <p style=text-align:center> <font size=20px color=blue>Qt!</font></h2> </p>"
        bt_text = "<h2><font size=7 face=verdana color=white align=center>305호실</font><br><font size=5 face=verdana color=white align=center>(프리미엄 투윈)</font></h2>"
        # aa = myicon(bt_text)
        self.button2_2.setIcon(self.myicon(bt_text))
        # self.button.setIconSize(mypixmap.size())
        self.button2_2.setIconSize(QSize(130, 180))
        self.button2_2.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # 아이콘 아래 텍스트

        self.button2_2.setGeometry(690, 470, 300, 200)
        # self.button2.setText('\n\n 일자 : 2024-09-20 ~ 2024-09-21\n 나는 누구일까 \n\n\n')
        self.button2_2.setFont(QFont('Arial', 15))
        # self.button.setAlignment(Qt.AlignLeft)
        self.button2_2.clicked.connect(self.myclick)

        ########################
        self.button1_a = QToolButton(self.fr02)

        # self.button = QPushButton('',self.fr01)
        self.button1_a.setStyleSheet("""QToolButton {
                        background-position: center;
                        background-repeat: no-repeat;
                        color: black;
                        text-align: left;
                        font: 75 15pt "Arial";
                        padding-bottom: 15px;
}"""
            """QToolButton { background-color:#f5f5dc; }"""
            
            """QToolButton::hover { background-color: #3333ff;
    color: #fff;}"""
            """QToolButton::pressed { 
    background-color:#ff2d55; }"""
        )
        # creating a QGraphicsDropShadowEffect object
        shadow1_a = QGraphicsDropShadowEffect()
        # setting blur radius
        shadow1_a.setBlurRadius(15)
        self.button1_a.setGraphicsEffect(shadow1_a)
        # self.button.move(75, 175)

        self.button1_a.setGeometry(10, 0, 120, 30)
        self.button1_a.setText('우동균')
        # self.button1_a.setFont(QFont('Arial', 15))
        self.button1_a.setCursor(QCursor(Qt.PointingHandCursor))
        self.button1_a.setToolTip('우동균 2024-11-15~2024-11-20')

        self.button1_b = QToolButton(self.fr02)

        # self.button = QPushButton('',self.fr01)
        self.button1_b.setStyleSheet("""QToolButton {
                                background-position: center;
                                background-repeat: no-repeat;
                                color: black;
                                text-align: left;
                                font: 75 15pt "Arial";
                                padding-bottom: 15px;
        }"""
                                     """QToolButton { background-color:#f5f5dc; }"""

                                     """QToolButton::hover { background-color: #3333ff;
                             color: #fff;}"""
                                     """QToolButton::pressed { 
                             background-color:#ff2d55; }"""
                                     )
        # creating a QGraphicsDropShadowEffect object
        shadow1_b = QGraphicsDropShadowEffect()
        # setting blur radius
        shadow1_b.setBlurRadius(15)
        self.button1_b.setGraphicsEffect(shadow1_b)
        # self.button.move(75, 175)

        self.button1_b.setGeometry(150, 0, 200, 30)
        self.button1_b.setText('Kristina Goryacheva')
        # self.button1_b.setFont(QFont('Arial', 15))
        self.button1_b.setCursor(QCursor(Qt.PointingHandCursor))
        self.button1_b.setToolTip('Kristina Goryacheva 2024-11-15~2024-11-20')









    def myicon(self, bt_text):
        mydocument = QTextDocument()
        mydocument.setDocumentMargin(0)
        mydocument.setHtml(bt_text)

        mypixmap = QPixmap(mydocument.size().toSize())
        mypixmap.fill(Qt.transparent)
        mypainter = QPainter(mypixmap)
        mydocument.drawContents(mypainter)
        mypainter.end()

        return QIcon(mypixmap)

    def load_stylesheet(self):
        # stylesheet.qss 파일 로드
        # qss_file = QFile('stylesheet1.qss')
        # qss_file.open(QFile.ReadOnly | QFile.Text)
        # qss_stream = QTextStream(qss_file)
        # self.setStyleSheet(qss_stream.readAll())
        aa1 ="""QMainWindow{background-color: white;} """
        aa = """
QPushButton#button {
    background-color: #f44336;
}
#button:hover {
    background-color: #e57373; 
    color: #fff;
}
#button:pressed { 
    background-color: #ffcdd2; 
}
#button1 {
    background-color: #4caf50;
    border-radius: 5px;       
}
#button1:hover {
    background-color: #81c784;
    color: #fff;              
}
#button1:pressed {
    background-color: #c8e6c9;
}
"""
        aa2 = aa1 + aa
        self.setStyleSheet(aa2)
        # qss_file.close()

    def myclick(self):
        self.button.setText('\n김성식\n\n 일자 : 2024-09-20 ~ 2024-11-20 \n(2박)')
        # btn_1.setText('\n399호실\n\n\n\n')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = UiMainWindow()
    main_window.show()
    sys.exit(app.exec_())