from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QBrush, QRegExpValidator
from PyQt5.QtWidgets import *
import os

from config.mariadb_connection import mariadb_conn
import mariadb
from datetime import timedelta,datetime
import bcrypt
# from function.inputtypehandler import InputTypeHandler


# class StockIndexWindow(QMainWindow, form_class):
class Userpwd_change_Window(QMainWindow):
    def __init__(self,pf_os,comp_code,user_id):
        super().__init__()
        self.move(10, 50)
        self.setFixedSize(439, 393)
        if pf_os == 'Windows':
            option_ui = 'UiDir/userpwd_change.ui'
        else:
            option_ui = 'UiDir/userpwd_change.ui'
        self.comp_code = comp_code
        self.user_id = user_id
        # option_ui = 'UiDir/StockCompInfo.ui'
        uic.loadUi(option_ui, self)

        # regExp = QRegExp("[0-9]*") #edit에 숫자만 입력 처리하기 위해
        regExp = QRegExp("[0-9--]*")  # edit에 숫자와 '-'를 입력 처리하기 위해
        self.ed_user_tel.setValidator(QRegExpValidator(regExp, self))
        # self.show()
        # self.setWindowTitle("기업 정보 자료 등록(StockCompInfo.py)")
        self.pb_save.clicked.connect(self.userpwd_dbsave)  # 사용자 id 발급 저장
        self.pb_clear.clicked.connect(self.userpwd_clear)  # 화면 clear
        self.init_rtn()

    #db 저장
    def userpwd_dbsave(self):
        if self.ed_now_pwd.text() is None or self.ed_now_pwd.text() =='' or len(self.ed_now_pwd.text()) <= 6 :
            QMessageBox.about(self, "정보", "현재 비밀번호를 입력하세요....")
            self.ed_now_pwd.setFocus()
        else:
            if  self.ed_new_pwd_01.text() is None or self.ed_new_pwd_01.text() =='' or len(self.ed_new_pwd_01.text()) <= 6 :
                QMessageBox.about(self, "정보", "새 비밀번호를 7자리 이상 입력하세요....")
                self.ed_new_pwd_01.setFocus()
            else:
                if self.ed_new_pwd_02.text() is None or self.ed_new_pwd_02.text() =='' or len(self.ed_new_pwd_02.text()) <= 6 :
                    QMessageBox.about(self, "정보", "새 비밀번호 확인란의 새 비밀빈호와 맞게 입력하세요....")
                    self.ed_new_pwd_02.setFocus()
                else:
                    if self.ed_new_pwd_01.text() != self.ed_new_pwd_02.text():
                        QMessageBox.about(self, "정보", "새 비밀번호와 새 비밀번호 확인이 맞지 않음!\n 정확히 입력하세요....")
                        self.ed_new_pwd_01.setText('')
                        self.ed_new_pwd_02.setText('')
                        self.ed_new_pwd_01.setFocus()
                    else:
                        # 현재 비밀번호가 맞는지 검사
                        now_pwd = self.ed_now_pwd.text()
                        password = now_pwd.encode('utf-8')  # unicode -> bytes
                        db_chk = self.user_old_pwd.encode('utf-8')  # unicode -> bytes
                        if not bcrypt.checkpw(password, db_chk):
                            QMessageBox.about(self, "정보", "현재 비밀번호가 맞지 않음! 정확히 입력하세요....")
                            self.ed_now_pwd.setText('')
                            self.ed_now_pwd.setFocus()
                        else:
                            pwd= self.ed_new_pwd_01.text()
                            if pwd[0].isalpha():#첫 글자는 영문자로 하기위해....
                                search_string = " "#비밀번호에 공백이 있는지 체크하기 위해
                                if pwd.find(search_string) != -1:
                                    QMessageBox.about(self, "정보", "공백이 포함되어 있음 다시 입력하세요....")
                                    self.ed_new_pwd_01.setText('')
                                    self.ed_new_pwd_02.setText('')
                                    self.ed_new_pwd_01.setFocus()
                                else:
                                    if not pwd.isalnum(): #특수문자를 포함 한경우
                                        #현재의 비밀번호가 맞으면  다음은 새 비밀번호의 조합을 본다...
                                        hashed_pwd = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")#암호화
                                        #저장 모드
                                        # 현재 일자를 검색
                                        mra = mariadb_conn().conn
                                        csr = mra.cursor()
                                        query_sel = "SELECT date_format(CURDATE(),'%Y-%m-%d') from dual "
                                        # print(query_sel)
                                        csr.execute(query_sel)
                                        rows = csr.fetchall()
                                        csr.close()
                                        mra.close()
                                        now_date = rows[0][0]

                                        # user_info_tbL 자료를 저장하려면.....
                                        mra = mariadb_conn().conn
                                        csr = mra.cursor()

                                        query_in01 = "update user_info_tbl set pw_ilja=%s,user_pw=%s " \
                                                     " WHERE comp_code=%s and user_id=%s "
                                        t = (now_date,hashed_pwd, self.comp_code,self.user_id)
                                        try:
                                            csr.execute(query_in01, t)
                                            mra.commit()
                                        except mariadb.Error as e:
                                            print(f"Error: {e}")
                                        csr.close()
                                        mra.close()

                                        QMessageBox.about(self, "정보", "새로운 비밀번호로 변경되었습니다.....")
                                        self.userpwd_clear()
                                        self.pb_clear.setFocus()
                                    else:
                                        QMessageBox.about(self, "정보", "특수문자를 조합하여 꼭 입력하세요....")
                                        self.ed_new_pwd_01.setText('')
                                        self.ed_new_pwd_02.setText('')
                                        self.ed_new_pwd_01.setFocus()
                            else:#첫 글자가 영문자가 아니면 메시지 보내기.....
                                QMessageBox.about(self, "정보", "비밀번호 첫 글자는 영문자를 입력하세요....")
                                self.ed_new_pwd_01.setText('')
                                self.ed_new_pwd_02.setText('')
                                self.ed_new_pwd_01.setFocus()
    #화면 Clear
    def userpwd_clear(self):
        self.ed_now_pwd.setText('')
        self.ed_new_pwd_01.setText('')
        self.ed_new_pwd_02.setText('')

    #권한 설정 combobox에 뿌려주려면....
    def init_rtn(self):
        # 권한 설정 코드를 검색해 오려면...
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_sel = ("SELECT USER_NAME,USER_TEL,USER_PW FROM user_info_tbl"
                     " WHERE comp_code = '" + self.comp_code + "' AND user_id = '"+self.user_id+"' ")
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()

        self.ed_user_id.setText(self.user_id)
        self.ed_user_name.setText(rows[0][0])
        self.ed_user_tel.setText(rows[0][1])
        self.user_old_pwd = rows[0][2]

##########################암호화 복호화
# 사용자 비밀번호
# pwd = "1"
#
# # # 비밀번호 해시 생성
# # hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
# #
# # decoded_hashed_password = hashed_password.decode('utf-8')
# aahashed_password = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
# # # 해시된 비밀번호 출력
# # print(str(hashed_password))
# # print(decoded_hashed_password)
# print(aahashed_password)
#
# password_en        = pwd.encode('utf-8') # unicode -> bytes
# hashed_password = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
# print(pwd)
# print(password_en)
# print(hashed_password)
#
# db_pwd='$2b$12$tb8QV6hTRsTi4AKSTa0EBudYEfSWj5zQcHGDcwoD5uBVX45lrRFae'
# password        = pwd.encode('utf-8') # unicode -> bytes
# hashed_password = db_pwd.encode('utf-8') # unicode -> bytes
#
# if not bcrypt.checkpw(password, hashed_password):
#     print(password)
#     print(hashed_password)
#     print("비번이 맞지 않습니다.....")
# else:
#     print(password)
#     print(hashed_password)
#     print("로그인 되었습니다.....")
