#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtGui import QPixmap, QBrush, QColor
from PyQt5.QtWidgets import QMainWindow, QApplication, QMdiSubWindow, QMdiArea, QLabel, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import Qt


from BASIC.basic_yeogak_info import Basic_yeogak_info_Window
from BASIC.appcomp_info import Appcomp_info_Window
from BASIC.appcomp_use_info import Appcomp_use_info_Window
from RESERVE_CANCEL_MNT.reserve_cancel2025_day_mnt import Reserve_cancel2025_day_mnt_Window
from RESERVE_CANCEL_MNT.reserve_cancel2025_day_pst import Reserve_cancel2025_day_pst_Window
from RESERVE_CANCEL_MNT.reserve_cancel2025_month_pst import Reserve_cancel2025_month_pst_Window
from RESERVE_CANCEL_MNT.reserve_cancel2025_period_pst import Reserve_cancel2025_period_pst_Window
from RESERVE_MNT.reserve_day2025_pst import Reserve_day2025_pst_Window
from RESERVE_MNT.reserve_month2025_mnt import Reserve_month2025_mnt_Window
from RESERVE_MNT.reserve_month2025_pst import Reserve_month2025_pst_Window
from RESERVE_MNT.reserve_period2025_mnt import Reserve_period2025_mnt_Window
from RESERVE_MNT.reserve_period2025_pst import Reserve_period2025_pst_Window
from revenue_pst.revenue_table_month2025_pst import Revenue_table_month2025_pst_Window
from revenue_pst.revenue_table_period2025_pst import Revenue_table_period2025_pst_Window
from revenue_pst.revenue_table_year2025_pst import Revenue_table_year2025_pst_Window

from EXPENSES_MNT.expenses_day_mnt import Expenses_day_mnt_Window
from EXPENSES_MNT.expenses_period_pst import Expenses_period_pst_Window
from EXPENSES_MNT.expenses_month_pst import Expenses_month_pst_Window
from EXPENSES_MNT.expenses_day_pst import Expenses_day_pst_Window
from USERID.userid_issue import Userid_issue_Window
from USERID.userpwd_change import Userpwd_change_Window
from USERID.userid_mnt import Userid_mnt_Window
from Login.login import Login_Window
import platform

#"pyinstaller  -n=NolgoJago --icon=.\stay.png .\yeogak.py" 실행파일 만들기 cmd로 실행

class QMdiSubWindowMod(QMdiSubWindow):
    def __init__(self):
        super().__init__()
        self.forceClose = False
    def closeEvent(self, event):
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.close()


# ------------------------- MainWindow ------------------------- #
form_class = uic.loadUiType("yeogak.ui")[0]
#actionStock_save_failed
class  mainGui(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
    # def __init__(self, parent=None):
    #     super(mainGui, self).__init__(parent)
        self.pf_os = platform.system()
        self.mdi = QMdiArea()
        self.mdi.setBackground(QBrush(QColor(210, 210, 210)))

        self.setupUi(self)
        self.setCentralWidget(self.mdi)
        self.setWindowTitle("놀GO 자Go Ver 1.0(aws)")
        # self.setWindowTitle("놀GO 자Go Ver 0.89 (yeogak2025_ntb\yeogak2025_ntb.py)")
        self.showMaximized()

        # self.label_1 = QLabel(self)
        # self.label_1.setPixmap(QPixmap(".\Img\corp.png"))
        # self.label_1.setGeometry(1820, 900, 100, 100)
        # self.label_1.show()
        # self.label_2 = QLabel(self)
        # self.label_2.setPixmap(QPixmap("C:\HanbiStock\Korea\Kospi\Img\title2.png"))
        # self.label_2.setGeometry(500, 500, 150, 150)
        # self.label_2.show()
        #self.var_clear()
        dlg = Login_Window(self.pf_os)
        dlg.exec_()

        self.comp_code = dlg.comp_code
        self.user_id = dlg.user_id
        self.user_pwd = dlg.user_pwd
        self.user_power = dlg.user_power
        if self.user_pwd =='c':#비밀번호 변경하려면....
            # ucw = Userpwd_change_Window(self.pf_os,self.comp_code,self.user_id)
            self.subWinApp4 = QMdiSubWindowMod()
            self.subWinApp4.setWidget(Userpwd_change_Window(self.pf_os,self.comp_code,self.user_id))
            self.subWinApp4.setWindowTitle("비밀번호 변경")
            # self.subWinApp4.setWindowTitle("비밀번호 변경(userpwd_change.py)")
            self.subWinApp4.setWindowFlags(Qt.WindowMinimizeButtonHint)
            self.mdi.addSubWindow(self.subWinApp4)
            self.subWinApp4.show()
            self.subWinApp4.setFocus()

            # ucw = Expenses_day_Window(self.pf_os,self.comp_code,self.user_id)
            # ucw.exec_()
        #정상 진행한다.
        if self.user_id is None or self.user_id == '':
            self.close()
        else:
            self.setConnections()

    def setConnections(self):
        self.action_exit.triggered.connect(self.close)

        # 숙박 시설 정보 관리
        self.action_basic_yeogak_info.triggered.connect(self.openApp1)

        # 숙박 어풀 홈페이지 정보 관리
        # self.action_app_homepage_info.triggered.connect(self.openApp2)
        #
        # "사용자 ID 발금"
        self.action_userid_issue.triggered.connect(self.openApp3)
        #
        # "사용자 비밀번호 변경"
        self.action_userpwd_change.triggered.connect(self.openApp4)
        #
        # # "사용자 ID 관리"
        self.action_userid_mnt.triggered.connect(self.openApp5)
        #
        # "숙박어플 정보 관리"
        self.action_appcomp_info.triggered.connect(self.openApp6)
        #
        # "숙박 어플 사용여부 관리"
        self.action_appcomp_use_info.triggered.connect(self.openApp7)

        # # "프로그램 종료"
        # self.action_exit.connect(self.openApp4)
        #
        #  "월 예약 관리"
        self.action_mon_reserve_management.triggered.connect(self.openApp10)
        #
        # #  기간별 예약 관리
        self.action_period_reserve_mnt.triggered.connect(self.openApp11)

        #  일별 예약 현황
        self.action_day_reserve_pst.triggered.connect(self.openApp12)

        #  월별 예약 현황
        self.action_month_reserve_pst.triggered.connect(self.openApp13)

        #  기간별 예약 현황
        self.action_period_reserve_pst.triggered.connect(self.openApp14)

        # 일별 지출 관리
        self.action_day_expenses_mnt.triggered.connect(self.openApp20)
        #
        # #  월별 지출 관리
        # self.action_month_expenses.triggered.connect(self.openApp21)
        #
        #  일자별 지출 현황
        self.action_day_expenses_pst.triggered.connect(self.openApp22)
        #
        # 월별 지출 현황
        self.action_month_expenses_pst.triggered.connect(self.openApp23)
        #
        # # 연간 지출 현황
        # self.action_year_expenses_pst.triggered.connect(self.openApp24)
        #
        # 임의 기간별 지출 현황
        self.action_period_expenses_pst.triggered.connect(self.openApp25)

        # 예약 취소 관리
        self.action_reserve_cancel_day_mnt.triggered.connect(self.openApp40)
        #
        # # 기간별 예약 취소 현황
        # self.action_period_cancel_perscondi.triggered.connect(self.openApp41)
        #
        # 일자별 예약 취소 현황
        self.action_day_cancel_pst.triggered.connect(self.openApp42)

        # 월별 예약 취소 현황
        self.action_month_cancel_pst.triggered.connect(self.openApp43)

        # 기간별 예약 취소 현황
        self.action_period_cancel_pst.triggered.connect(self.openApp44)
        #
        # # 월별 매출 현황
        self.action_month_sales_pst.triggered.connect(self.openApp61)
        #
        # # 연간 매출 현황
        self.action_year_sales_pst.triggered.connect(self.openApp62)
        #

        # 기간별 매출 현황
        self.action_period_sales_pst.triggered.connect(self.openApp63)



    #def closeEvent(self, event):
    def closeEvent(self, event):
        if self.user_id is None or self.user_id =='':
            event.accept()
            sys.exit()
        else:
            event.accept()

    def openApp1(self):
        self.subWinApp1 = QMdiSubWindowMod()
        self.subWinApp1.setWidget(Basic_yeogak_info_Window(self.pf_os,self.comp_code,self.user_id))
        self.subWinApp1.setWindowTitle("숙박 시설 정보 관리")
        # self.subWinApp1.setWindowTitle("숙박 시설 정보 관리(basic_yeogak_info.py)")
        self.subWinApp1.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp1)
        self.subWinApp1.show()
        self.subWinApp1.setFocus()

    # def openApp2(self):
        # if self.app2_chk == "S":
        #     self.subWinApp2 = QMdiSubWindowMod()
        #     self.subWinApp2.setWidget(Basic_yeogak_info_Window(self.pf_os,self.comp_code,self.user_id))
        #     self.subWinApp2.setWindowTitle("숙박 시설 정보 관리(basic_yeogak_info.py)")
        #     self.mdi.addSubWindow(self.subWinApp2)
        #     self.app2_chk = "P"
        #     # self.subWinApp2.hide()
        # else:
        #     self.subWinApp2.setWidget(Basic_yeogak_info_Window(self.pf_os, self.comp_code,self.user_id))
        # self.subWinApp2.show()
        # self.subWinApp2.setFocus()

    def openApp3(self):
        self.subWinApp3 = QMdiSubWindowMod()
        self.subWinApp3.setWidget(Userid_issue_Window(self.pf_os,self.comp_code,self.user_id))
        self.subWinApp3.setWindowTitle("사용자 ID 발급")
        # self.subWinApp3.setWindowTitle("사용자 ID 발급(userid_issue.py)")
        self.subWinApp3.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp3)
        self.subWinApp3.show()
        self.subWinApp3.setFocus()

    def openApp4(self):
        self.subWinApp4 = QMdiSubWindowMod()
        self.subWinApp4.setWidget(Userpwd_change_Window(self.pf_os,self.comp_code,self.user_id))
        self.subWinApp4.setWindowTitle("비밀번호 변경")
        # self.subWinApp4.setWindowTitle("비밀번호 변경(userpwd_change.py)")
        self.subWinApp4.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp4)
        self.subWinApp4.show()
        self.subWinApp4.setFocus()

    def openApp5(self):
        self.subWinApp5 = QMdiSubWindowMod()
        self.subWinApp5.setWidget(Userid_mnt_Window(self.pf_os,self.comp_code,self.user_id))
        self.subWinApp5.setWindowTitle("사용자 ID 관리")
        # self.subWinApp5.setWindowTitle("사용자 ID 관리(userid_mnt.py)")
        self.subWinApp5.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp5)
        self.subWinApp5.show()
        self.subWinApp5.setFocus()

    def openApp6(self):
        self.subWinApp6 = QMdiSubWindowMod()
        self.subWinApp6.setWidget(Appcomp_info_Window(self.pf_os,self.comp_code,self.user_id))
        self.subWinApp6.setWindowTitle("숙박어플 정보 관리")
        # self.subWinApp6.setWindowTitle("숙박어플 정보 관리(appcomp_info.py)")
        self.subWinApp6.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp6)
        self.subWinApp6.show()
        self.subWinApp6.setFocus()

    def openApp7(self):
        self.subWinApp7 = QMdiSubWindowMod()
        self.subWinApp7.setWidget(Appcomp_use_info_Window(self.pf_os,self.comp_code,self.user_id))
        self.subWinApp7.setWindowTitle("숙박 어플 사용여부 관리")
        # self.subWinApp7.setWindowTitle("숙박 어플 사용여부 관리(appcomp_use_info.py)")
        self.subWinApp7.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp7)
        self.subWinApp7.show()
        self.subWinApp7.setFocus()

    def openApp10(self):
        self.subWinApp10 = QMdiSubWindowMod()
        self.subWinApp10.setWidget(
            Reserve_month2025_mnt_Window(self.pf_os, self.comp_code,self.user_id))
        self.subWinApp10.setWindowTitle("월 예약 관리")
        # self.subWinApp10.setWindowTitle("월별 예약 관리(reserve_month_mnt.py)")
        self.subWinApp10.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp10)
        self.subWinApp10.show()
        self.subWinApp10.setFocus()

    def openApp11(self):
        self.subWinApp11 = QMdiSubWindowMod()
        self.subWinApp11.setWidget(
            Reserve_period2025_mnt_Window(self.pf_os, self.comp_code, self.user_id))
        self.subWinApp11.setWindowTitle("기간별 예약 관리")
        self.subWinApp11.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp11)
        self.subWinApp11.show()
        self.subWinApp11.setFocus()

    def openApp12(self):
        self.subWinApp12 = QMdiSubWindowMod()
        self.subWinApp12.setWidget(
            Reserve_day2025_pst_Window(self.pf_os, self.comp_code, self.user_id))
        self.subWinApp12.setWindowTitle("일일 호실 및 예약자 정보")
        self.subWinApp12.setWindowFlags(Qt.WindowMinimizeButtonHint)

        self.mdi.addSubWindow(self.subWinApp12)
        self.subWinApp12.show()
        self.subWinApp12.setFocus()

    def openApp13(self):
        self.subWinApp13 = QMdiSubWindowMod()
        self.subWinApp13.setWidget(
            Reserve_month2025_pst_Window(self.pf_os, self.comp_code, self.user_id))
        self.subWinApp13.setWindowTitle("월별 예약 현황")
        self.subWinApp13.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp13)
        self.subWinApp13.show()
        self.subWinApp13.setFocus()

    def openApp14(self):
        self.subWinApp14 = QMdiSubWindowMod()
        self.subWinApp14.setWidget(
            Reserve_period2025_pst_Window(self.pf_os, self.comp_code, self.user_id))
        self.subWinApp14.setWindowTitle("기간별 예약 현황")
        self.subWinApp14.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp14)
        self.subWinApp14.show()
        self.subWinApp14.setFocus()

    def openApp20(self):
        self.subWinApp20 = QMdiSubWindowMod()
        self.subWinApp20.setWidget(
            Expenses_day_mnt_Window(self.pf_os, self.comp_code, self.user_id))
        self.subWinApp20.setWindowTitle("일별 지출 관리")
        # self.subWinApp20.setWindowTitle("일별 지출 관리(expenses_day.py)")
        self.subWinApp20.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp20)
        self.subWinApp20.show()
        self.subWinApp20.setFocus()

    def openApp22(self):
        self.subWinApp22 = QMdiSubWindowMod()
        self.subWinApp22.setWidget(
            Expenses_day_pst_Window(self.pf_os, self.comp_code, self.user_id))
        self.subWinApp22.setWindowTitle("일자별 지출 현황")
        # self.subWinApp22.setWindowTitle("일자별 지출 현황(expenses_day_pst.py)")
        self.subWinApp22.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp22)
        self.subWinApp22.show()
        self.subWinApp22.setFocus()

    def openApp23(self):
        self.subWinApp23 = QMdiSubWindowMod()
        self.subWinApp23.setWidget(
            Expenses_month_pst_Window(self.pf_os, self.comp_code, self.user_id))
        self.subWinApp23.setWindowTitle("월별 지출 현황")
        # self.subWinApp23.setWindowTitle("월별 지출 현황(expenses_month_pst.py)")
        self.subWinApp23.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp23)
        self.subWinApp23.show()
        self.subWinApp23.setFocus()

    def openApp25(self):
        self.subWinApp25 = QMdiSubWindowMod()
        self.subWinApp25.setWidget(
            Expenses_period_pst_Window(self.pf_os, self.comp_code, self.user_id))
        self.subWinApp25.setWindowTitle("기간별 지출 현황")
        # self.subWinApp25.setWindowTitle("기간별 지출 현황(expenses_period_pst.py)")
        self.subWinApp25.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp25)
        self.subWinApp25.show()
        self.subWinApp25.setFocus()

    def openApp40(self):
        self.subWinApp40 = QMdiSubWindowMod()
        self.subWinApp40.setWidget(
            Reserve_cancel2025_day_mnt_Window(self.pf_os, self.comp_code, self.user_id))
        self.subWinApp40.setWindowTitle("예약 취소 관리")
        # self.subWinApp40.setWindowTitle("예약 취소 관리(reserve_cancel_day.py)")
        self.subWinApp40.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp40)
        self.subWinApp40.show()
        self.subWinApp40.setFocus()

    def openApp42(self):
        self.subWinApp42 = QMdiSubWindowMod()
        self.subWinApp42.setWidget(
            Reserve_cancel2025_day_pst_Window(self.pf_os, self.comp_code, self.user_id))
        self.subWinApp42.setWindowTitle("일자별 예약 취소 현황")
        self.subWinApp42.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp42)
        self.subWinApp42.show()
        self.subWinApp42.setFocus()

    def openApp43(self):
        self.subWinApp43 = QMdiSubWindowMod()
        self.subWinApp43.setWidget(
            Reserve_cancel2025_month_pst_Window(self.pf_os, self.comp_code, self.user_id))
        self.subWinApp43.setWindowTitle("월별 예약 취소 현황")
        self.subWinApp43.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp43)
        self.subWinApp43.show()
        self.subWinApp43.setFocus()

    def openApp44(self):
        self.subWinApp44 = QMdiSubWindowMod()
        self.subWinApp44.setWidget(
            Reserve_cancel2025_period_pst_Window(self.pf_os, self.comp_code, self.user_id))
        self.subWinApp44.setWindowTitle("기간별 예약 취소 현황")
        self.subWinApp44.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp44)
        self.subWinApp44.show()
        self.subWinApp44.setFocus()

    def openApp61(self):
        self.subWinApp61 = QMdiSubWindowMod()
        self.subWinApp61.setWidget(
            Revenue_table_month2025_pst_Window(self.pf_os, self.comp_code, self.user_id))
        self.subWinApp61.setWindowTitle("월별 매출 현황")
        self.subWinApp61.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp61)
        self.subWinApp61.show()
        self.subWinApp61.setFocus()

    def openApp62(self):
        self.subWinApp62 = QMdiSubWindowMod()
        self.subWinApp62.setWidget(
            Revenue_table_year2025_pst_Window(self.pf_os, self.comp_code, self.user_id))
        self.subWinApp62.setWindowTitle("연간 매출 현황")
        self.subWinApp62.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp62)
        self.subWinApp62.show()
        self.subWinApp62.setFocus()

    def openApp63(self):
        self.subWinApp63 = QMdiSubWindowMod()
        self.subWinApp63.setWidget(
            Revenue_table_period2025_pst_Window(self.pf_os, self.comp_code, self.user_id))
        self.subWinApp63.setWindowTitle("기간별 매출 현황")
        self.subWinApp63.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.mdi.addSubWindow(self.subWinApp63)
        self.subWinApp63.show()
        self.subWinApp63.setFocus()

    def openApp50(self):

        self.subWinApp50 = QMdiSubWindowMod()
        self.subWinApp50.setWidget(Login_Window(self.pf_os, self.comp_code, self.user_id))
        self.subWinApp50.show()
    #
    # def save_day(self):
    #     pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setStyle('Breeze')#폼 스타일 정의 할수 있다.
    #['Breeze', 'Oxygen', 'QtCurve', 'Windows', 'Fusion']
    myWindow = mainGui()
    myWindow.show()
    app.exec_()