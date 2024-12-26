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
class Userid_issue_Window(QMainWindow):
    def __init__(self,pf_os,comp_code,user_id):
        super().__init__()
        self.move(10, 50)
        self.setFixedSize(664, 306)
        if pf_os == 'Windows':
            option_ui = 'UiDir/userid_issue.ui'
        else:
            option_ui = 'UiDir/userid_issue.ui'
        self.comp_code = comp_code
        self.user_id = user_id
        # option_ui = 'UiDir/StockCompInfo.ui'
        uic.loadUi(option_ui, self)

        # regExp = QRegExp("[0-9]*") #edit에 숫자만 입력 처리하기 위해
        regExp = QRegExp("[0-9--]*")  # edit에 숫자와 '-'를 입력 처리하기 위해
        self.ed_tel.setValidator(QRegExpValidator(regExp, self))
        # self.show()
        # self.setWindowTitle("기업 정보 자료 등록(StockCompInfo.py)")
        self.overlap_chk = ''#중복 확인을 체크 후 사용 가능으로 쓰기 위해.....
        self.pb_save.clicked.connect(self.userid_dbsave)  # 사용자 id 발급 저장
        self.pb_clear.clicked.connect(self.userid_clear)  # 화면 clear
        self.pb_overlap_chk.clicked.connect(self.overlap_rtn)  # id 중복 확인
        self.ed_userid.textChanged.connect(self.userid_change_rtn)#중복확인 후에도 변경되면 다시 중복 확인을 체크하기 위해
        self.init_rtn()

    #db 저장
    def userid_dbsave(self):
        if self.overlap_chk == 'r':
            if self.ed_name is None or self.ed_name.text().replace(" ", "") =='':
                QMessageBox.about(self, "정보", "성명을 입력하세요....")
                self.ed_name.setFocus()
            else:
                if self.ed_tel.text() is None or self.ed_tel.text() =='' or len(self.ed_tel.text().replace(" ", "")) <= 9:
                    QMessageBox.about(self, "정보", "전화(폰)번호를 정확히 입력하세요....")
                    self.ed_tel.setFocus()
                else:
                    if self.cb_power.currentIndex() == 0:
                        QMessageBox.about(self, "정보", "권한 부여 해주세요....")
                        self.cb_power.setFocus()
                    else:#체크가 끝나고 저장 처리한다.  성명, 전화번호, 권한은 중복이 처리가 가능하도록 즉 한사람이 2개이상의 ID를 부여하기 위해# 암호화
                        pwd='1234567' #최초비밀번호
                        hashed_pwd = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")#암호화
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
                        query_in01 = "insert into user_info_tbl (comp_code,user_id,pw_ilja,user_name," \
                                     "user_tel,user_power,user_pw,user_stop,user_bigo,mnt_id) " \
                                     " values (%s,%s,%s,%s,%s,FN_CODE_CODE('PWR',%s),%s,'','',%s) "
                        t = (
                        self.comp_code,self.ed_userid.text(), now_date,self.ed_name.text(),
                        self.ed_tel.text().replace(" ", ""), self.cb_power.currentText(), hashed_pwd,self.user_id)
                        try:
                            csr.execute(query_in01, t)
                            mra.commit()
                        except mariadb.Error as e:
                            print(f"Error: {e}")
                        csr.close()
                        mra.close()

                        QMessageBox.about(self, "정보", " 사용자 ID : "+self.ed_userid.text()+" 발급되었습니다.....")
                        self.userid_clear()

        else:
            QMessageBox.about(self, "Message", "중복확인 버튼 클릭을 클릭하세요..")
            self.pb_overlap_chk.setFocus()


    #화면 Clear
    def userid_clear(self):
        self.ed_userid.setText('')
        self.ed_name.setText('')
        self.ed_tel.setText('')
        self.cb_power.setCurrentIndex(0)

    #권한 설정 combobox에 뿌려주려면....
    def init_rtn(self):
        # 권한 설정 코드를 검색해 오려면...
        mra = mariadb_conn().conn
        csr = mra.cursor(dictionary=True) #딕셔너리 형태로 표현하기 위해....
        query_sel = "SELECT CODE_NAME FROM yeogak_code_tbl WHERE code_id = 'PWR' "
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        self.cb_power.insertItem(0,'')
        #권한설정 콤보박스에 넣어 준다.....
        for idx, col in enumerate(rows):
            # print(col["CODE_NAME"])
            self.cb_power.addItem(col["CODE_NAME"])


    #self.overlap_chk 리셋하려고
    def userid_change_rtn(self):
        self.overlap_chk = '' #중복 체크를 초기화
        self.ed_userid.lower()  # 소문자로 변경

    #알파벳 자리수 7자리 이상 체크 후 ID 중복을 체크하려면..
    def overlap_rtn(self):
        str_chk = self.ed_userid.text()
        if str_chk is None or str_chk == '':
            QMessageBox.about(self, "Message", "ID 를 영문자,숫자 7자리 이상으로 정확히 입력하세요....")
            self.ed_userid.setFocus()
        else:
            if str_chk[0].isalpha():#첫 글자는 영문자로 하기위해....
                if len(str_chk) <= 6:
                    QMessageBox.about(self, "Message", "ID 를 영문자,숫자 7자리 이상으로 정확히 입력하세요....")
                    self.ed_userid.setFocus()
                else:
                    # alp = str_chk.isalpha()
                    # alnu = str_chk.isalnum()
                    if str_chk.isalnum():#영문자,숫자로 이루어졌다면... 다음은 중복체크
                        # id 중복 확인확인 하기....
                        mra = mariadb_conn().conn
                        csr = mra.cursor()
                        query_sel = "SELECT COUNT(*) FROM user_info_tbl "\
                                " WHERE comp_code = '" + self.comp_code + "' AND user_id = '"+str_chk+"' "
                        # print(query_sel)
                        csr.execute(query_sel)
                        rows = csr.fetchall()
                        csr.close()
                        mra.close()
                        cnt = rows[0][0]
                        if cnt > 0 :
                            QMessageBox.about(self, "Message", "사용 중인 ID 입니다.")
                            self.ed_userid.setText('')
                            self.overlap_chk = ''
                            self.ed_userid.setFocus()
                        else:
                            QMessageBox.about(self, "Message", "사용가능한 ID 입니다.")
                            self.overlap_chk = 'r'
                            self.ed_userid.setFocus()
                    else:
                        QMessageBox.about(self, "Message", "영문자,숫자 7자리 이상으로 구성해서 다시 입력하세요..")
                        self.ed_userid.setText('')
                        self.overlap_chk = ''
                        self.ed_userid.setFocus()
            else:#첫 글자가 영문자가 아니면 다시 입력 유도....
                QMessageBox.about(self, "Message", "첫 글자는 영문자로 구성해서 다시 입력하세요..")
                self.ed_userid.setText('')
                self.overlap_chk = ''
                self.ed_userid.setFocus()

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
