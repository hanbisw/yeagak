from PyQt5.QtWidgets import *
from PyQt5 import uic,QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import QBrush, QRegExpValidator, QColor, QPalette, QFont
from PyQt5.QtWidgets import *

import pandas as pd
import subprocess
import webbrowser
import os
import bcrypt

from config.mariadb_connection import mariadb_conn
import mariadb
from datetime import timedelta,datetime

# from function.inputtypehandler import InputTypeHandler


# class StockIndexWindow(QMainWindow, form_class):
class Login_Window(QDialog):
    def __init__(self,pf_os):
        super().__init__()
        # self.move(30,30)
        self.setFixedSize(560,510)
        if pf_os == 'Windows':
            option_ui = 'UiDir/login_yeogak.ui'
            # option_ui.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            # option_ui.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        else:
            option_ui = 'UiDir/login_yeogak.ui'

        self.center()

        self.comp_code = ''#처음 로그인시 회사 번호를 어떻게 가져오나......
        self.user_id = ''
        # option_ui = 'UiDir/StockCompInfo.ui'
        uic.loadUi(option_ui, self)
        # self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.label.setStyleSheet("background-image : url(UiDir/stay.png); border-top-left-radius: 50px; ")

        self.pb_close.clicked.connect(self.close_rtn)# 종료 버튼 클릭시
        self.pb_login.clicked.connect(self.login_rtn)  # id와 password를 확인한다....
        # self.show()

     #종료시
    def close_rtn(self):# x 버튼을 눌러을때
        self.comp_code = ''
        self.user_name = ''
        self.user_power = ''
        self.user_pwd = ''
        self.user_id = ''
        self.close()

    #로그인 화면을 중앙에 두려면......
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    def login_rtn(self):  # id와 password를 검정한다....
        self.user_id = self.ed_id.text()
        pwd = self.ed_pwd.text()

        if self.ed_id.text() is None or self.ed_id.text() == '':  # 가져온 정보가 없다면.....
            QMessageBox.about(self, "정보", "아이디를 입력하세요....")
            self.ed_id.setText('')
            self.ed_id.setFocus()

        elif self.ed_pwd.text() is None or self.ed_pwd.text() == '':  # 가져온 정보가 없다면.....
            QMessageBox.about(self, "정보", "비밀번호를 입력하세요....")
            self.ed_pwd.setText('')
            self.ed_pwd.setFocus()
        else:
            # 사용자를 검색한
            mra = mariadb_conn().conn
            csr = mra.cursor()
            query_sel = "SELECT user_pw,user_stop from user_info_tbl " \
                        " where user_id = '" + self.user_id + "' "
            # query_sel = "SELECT user_pw,user_stop from user_info_tbl " \
            #             " where comp_code = '"+self.comp_code+"' AND user_id = '" + self.user_id + "' "
            #print(query_sel)
            csr.execute(query_sel)
            rows = csr.fetchall()
            csr.close()
            mra.close()
            cnt = len(rows)
            if cnt > 0:
                user_pw = rows[0][0] #pwd를 가져온다.
                user_stop = rows[0][1]#사용중지 ID인지를 체크한다면....
            else:
                user_pw = '' #pwd를 없을 경우 공백처리.
                user_stop = 'n'#사용중지 ID로....
            if user_stop != 'y':#사용중지 ID가 아니라면...
                if user_pw is None or user_pw  == '':
                    QMessageBox.about(self, "정보", "아이디를 맞지 않음 다시 입력하세요....")
                    self.ed_id.setFocus()
                else:
                    password = pwd.encode('utf-8')  # unicode -> bytes
                    db_chk = user_pw.encode('utf-8')  # unicode -> bytes
                    if not bcrypt.checkpw(password, db_chk):
                        QMessageBox.about(self, "정보", "아이디와 비밀번호가 맞지 않음! 확인바랍니다....")
                        self.ed_id.setText('')
                        self.ed_pwd.setText('')
                        self.ed_id.setFocus()
                    else:
                        mra = mariadb_conn().conn
                        csr = mra.cursor()
                        query_sel = "SELECT comp_code,user_name,user_power from user_info_tbl "\
                                    " where user_id = '"+self.user_id+"' "
                        # query_sel = "SELECT comp_code,user_name,user_power from user_info_tbl "\
                        #             " where comp_code = '"+self.comp_code+"' AND user_id = '"+self.user_id+"' "
                        #print(query_sel)
                        csr.execute(query_sel)
                        rows = csr.fetchall()
                        csr.close()
                        mra.close()
                        self.comp_code = rows[0][0]
                        self.user_name = rows[0][1]
                        self.user_power = rows[0][2]
                        if pwd =='1234567':
                            self.user_pwd ='c'#비밀빌번호를 변경을 요구하는 화면으로 전환하려면
                        else:
                            self.user_pwd = ''#비밀번호 변경없이 통과

                        self.close() #로그인 성공시.....

            else:#중지 ID라면 메시지 보내고 프로그램 중지 시키려면......
                QMessageBox.about(self, "정보", "사용이 중지된 ID입니다. 프로그램을 종료합니다.")
                #중지 ID가 접속 시도시 어떻게 해야 할 까   SNS
                self.comp_code = ''
                self.user_name = ''
                self.user_power = ''
                self.user_pwd = ''
                self.user_id = ''#
                self.close()  # 프로그램 종료.....
