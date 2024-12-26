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
class Userid_mnt_Window(QMainWindow):
    def __init__(self,pf_os,comp_code,user_id):
        super().__init__()
        self.move(10, 50)
        self.setFixedSize(1026, 493)
        if pf_os == 'Windows':
            option_ui = 'UiDir/userid_mnt.ui'
        else:
            option_ui = 'UiDir/userid_mnt.ui'
        self.comp_code = comp_code
        self.user_id = user_id
        # option_ui = 'UiDir/StockCompInfo.ui'
        uic.loadUi(option_ui, self)

        regExp = QRegExp("[0-9]*") #edit에 숫자만 입력 처리하기 위해
        self.pb_save.clicked.connect(self.userid_mnt_dbsave)  # 사용자 id 발급 저장
        self.pb_clear.clicked.connect(self.userid_mnt_clear)  # 화면 clear
        self.pb_pwreset.clicked.connect(self.userid_mnt_reset)  # 화면 clear

        self.tw_userid_mnt.clicked.connect(self.mouse_click_rtn) # 클릭시 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
        self.tw_userid_mnt.keyPressEvent = self.keyPressEvent #UP, DOWN 키를 누를 때 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
        self.first_sch()  # super 권한자 자신을 제외하고 전 id를 다 보여주려면....


    #비밀번호 초기화 해주려면...
    def userid_mnt_reset(self):
        if self.ed_user_id.text() is None or self.ed_user_id.text() =='':
                QMessageBox.about(self, "정보", "비밀번호 초기화할 ID를 아래에서 선택하세요")
                self.userid_mnt_clear()
        else:
            reply = QMessageBox.question(self, 'Message', '비밀번호를 초기화 하시겠습니까?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes: #비밀번호를 초기화 저장하려면
                pwd = '1234567'  # 비밀번호 초기화
                hashed_pwd = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")  # 암호화
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

                #비밀번호 초기화를 저장하려면.....
                mra = mariadb_conn().conn
                csr = mra.cursor()

                query_in01 = "update user_info_tbl set pw_ilja=%s,user_pw=%s,mnt_id=%s " \
                             " WHERE comp_code=%s and user_id=%s "
                t = (now_date,hashed_pwd,self.user_id,self.comp_code,self.ed_user_id.text())
                try:
                    csr.execute(query_in01, t)
                    mra.commit()
                except mariadb.Error as e:
                    print(f"Error: {e}")
                csr.close()
                mra.close()

                QMessageBox.about(self, "정보", "비밀번호 '1234567'로 초기화되었습니다.....")
                self.first_sch()
            else:
                self.first_sch()

    #db 저장
    def userid_mnt_dbsave(self):
        if ((self.sch_stop =='' and self.cb_stop.isChecked()) or
           (self.sch_stop =='Y' and (not self.cb_stop.isChecked())) or
           (self.sch_bigo != self.ed_bigo.text())):
            reply = QMessageBox.question(self, 'Message', '변경 사항을 저장하시겠습니까?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:  # 변경 사항을 저장하려면....
                if self.sch_stop == '' and self.cb_stop.isChecked():#id를 중지 하려한다면...
                    if self.ed_bigo.text() is None or self.ed_bigo.text() =='':
                        QMessageBox.about(self, "정보", "ID 일시 중지시 참고사항을 꼭 입력하세요..")
                        self.ed_bigo.setFocus()
                    else: #저장으로..
                        self.dbsave_rtn()#바로 자료를 저장한다.
                        self.first_sch()
                elif self.sch_stop == 'Y' and (not self.cb_stop.isChecked()):#중지를 풀어 주려면.....
                    if self.ed_bigo.text() in None or self.ed_bigo.text() =='':
                        QMessageBox.about(self, "정보", "ID 일시 중지에서 해제할 경우  참고사항을 꼭 입력하세요..")
                        self.ed_bigo.setFocus()
                    else: #저장으로..
                        self.dbsave_rtn()#바로 자료를 저장한다.
                        self.first_sch()
                else:
                    self.dbsave_rtn()  # 바로 자료를 저장한다.
                    self.first_sch()
            else:
                self.userid_mnt_clear.setFocus()
        else:
            QMessageBox.about(self, "정보", "변경사항이 없습니다.")
            self.pb_clear.setFocus()


    def dbsave_rtn(self):
        if self.cb_stop.isChecked():#id가 중지로  처리하려면....
            id_stop = 'Y'#중지
        else:
            id_stop = ''  #해제
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

        #비밀번호 초기화를 저장하려면.....
        mra = mariadb_conn().conn
        csr = mra.cursor()

        query_in01 = "update user_info_tbl set pw_ilja=%s,user_stop=%s,,user_bigo=%s,mnt_id=%s " \
                     " WHERE comp_code=%s and user_id=%s "
        t = (now_date,id_stop,self.ed_bigo.text(),self.user_id,self.comp_code,self.ed_user_id.text())
        try:
            csr.execute(query_in01, t)
            mra.commit()
        except mariadb.Error as e:
            print(f"Error: {e}")
        csr.close()
        mra.close()

        QMessageBox.about(self, "정보", "자료가 처리되었습니다....")

    #화면 Clear
    def userid_mnt_clear(self):
        self.ed_user_name.setText('')
        self.ed_user_id.setText('')
        self.ed_user_tel.setText('')
        self.cb_stop.setChecked(False)#중지 처리  NO CHECK
        self.ed_bigo.setText('')
        self.sch_name = ''
        self.sch_id   = ''
        self.sch_tel  = ''
        self.sch_stop = ''
        self.sch_bigo = ''

    def display_rtn(self):#화면에 뿌려준다....
        self.ed_user_name.setText(self.sch_name)
        self.ed_user_id.setText(self.sch_id)
        self.ed_user_tel.setText(self.sch_tel)
        self.ed_bigo.setText(self.sch_bigo)
        if self.sch_stop == 'Y':#ID 일시 중단
            self.cb_stop.setChecked(True)  # 체크 시에...
        else:
            self.cb_stop.setChecked(False)  # 체크 시에...

    #KEY_UP, KEY_DOWN을 눌렀다면 .....
    def keyPressEvent (self, eventQKeyEvent):
        key = eventQKeyEvent.key()
        if key == Qt.Key_Up: #up 키를 누를 때마다 ID 정보를 보여주려면.....
            row = self.tw_userid_mnt.currentRow() #현재 ROW 값을 가져오려면..
            if row == 0: # 처음 일때 값을 1로 하기 위해
                row += 1
            self.tw_userid_mnt.setCurrentCell(row-1,0)  #한 ROW 위로 이동
            self.sch_name = self.tw_userid_mnt.item(self.tw_userid_mnt.currentRow(), 0).text()  #성명을 읽는다.
            self.sch_id   = self.tw_userid_mnt.item(self.tw_userid_mnt.currentRow(), 1).text()  #id을 읽는다.
            self.sch_tel  = self.tw_userid_mnt.item(self.tw_userid_mnt.currentRow(), 2).text()  #전화번호을 읽는다.
            self.sch_stop = self.tw_userid_mnt.item(self.tw_userid_mnt.currentRow(), 3).text()  #중지여부 읽는다.
            self.sch_bigo = self.tw_userid_mnt.item(self.tw_userid_mnt.currentRow(), 4).text()  #참고사항을 읽는다.

            self.display_rtn()#화면에 뿌려주려면...


        elif key == Qt.Key_Down:  # down 키를 누를 때마다 ID 정보를 보여주려면.....
            row = self.tw_userid_mnt.currentRow() #현재 ROW 값을 가져오려면..
            if row >= (self.tw_userid_mnt.rowCount() -1): #마지막 ROW일때 계속 마지막 자료 보여주려면.....
               row -= 1
            self.tw_userid_mnt.setCurrentCell(row + 1, 0) #한 ROW 밑으로 이동
            self.sch_name = self.tw_userid_mnt.item(self.tw_userid_mnt.currentRow(), 0).text()  #성명을 읽는다.
            self.sch_id   = self.tw_userid_mnt.item(self.tw_userid_mnt.currentRow(), 1).text()  #id을 읽는다.
            self.sch_tel  = self.tw_userid_mnt.item(self.tw_userid_mnt.currentRow(), 2).text()  #전화번호을 읽는다.
            self.sch_stop = self.tw_userid_mnt.item(self.tw_userid_mnt.currentRow(), 3).text()  #중지여부 읽는다.
            self.sch_bigo = self.tw_userid_mnt.item(self.tw_userid_mnt.currentRow(), 4).text()  #참고사항을 읽는다.

            self.display_rtn()#화면에 뿌려주려면...

    # 클릭시 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
    def mouse_click_rtn(self):
        row = self.tw_userid_mnt.currentRow() #현재 ROW 값을 가져오려면..
        self.tw_userid_mnt.setCurrentCell(row, 0)  # ROW 이동
        self.sch_name = self.tw_userid_mnt.item(self.tw_userid_mnt.currentRow(), 0).text()  #성명을 읽는다.
        self.sch_id   = self.tw_userid_mnt.item(self.tw_userid_mnt.currentRow(), 1).text()  #id을 읽는다.
        self.sch_tel  = self.tw_userid_mnt.item(self.tw_userid_mnt.currentRow(), 2).text()  #전화번호을 읽는다.
        self.sch_stop = self.tw_userid_mnt.item(self.tw_userid_mnt.currentRow(), 3).text()  #중지여부 읽는다.
        self.sch_bigo = self.tw_userid_mnt.item(self.tw_userid_mnt.currentRow(), 4).text()  #참고사항을 읽는다.

        self.display_rtn()#화면에 뿌려주려면...

    def first_sch(self):
        self.userid_mnt_clear()
        mra = mariadb_conn().conn
        mra = mariadb_conn().conn
        csr = mra.cursor(dictionary=True) #딕셔너리 형태로 표현하기 위해....
        query_sel = ("SELECT USER_NAME,USER_ID,USER_TEL,USER_STOP,USER_BIGO FROM user_info_tbl"
                     " WHERE comp_code = '" + self.comp_code + "' AND user_id != '"+self.user_id+"' ")
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        item_cnt = len(rows)
        self.tw_userid_mnt.setRowCount(item_cnt)
        style = "::section {""background-color: lightblue; }"
        self.tw_userid_mnt.horizontalHeader().setStyleSheet(style)
        # self.tw_reserve.setShowGrid(False)

        #호실 정보 보여주기
        for idx, col in enumerate(rows):
            # self.tw_reserve.item(0, 0).setBackground(QBrush(Qt.red))

            self.tw_userid_mnt.setItem(idx, 0, QTableWidgetItem(col["USER_NAME"]))#일자
            self.tw_userid_mnt.item(idx, 0).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tw_userid_mnt.setItem(idx, 1, QTableWidgetItem(col["USER_ID"]))#호실
            self.tw_userid_mnt.setItem(idx, 2, QTableWidgetItem(col["USER_TEL"]))#격실타입
            self.tw_userid_mnt.item(idx, 2).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tw_userid_mnt.setItem(idx, 3, QTableWidgetItem(col["USER_STOP"]))#예약자
            self.tw_userid_mnt.item(idx, 3).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tw_userid_mnt.setItem(idx, 4, QTableWidgetItem(col["USER_BIGO"]))#예약사이트

        self.tw_userid_mnt.resizeRowsToContents()
        self.tw_userid_mnt.resizeColumnsToContents()#col 자릿수에 맡게 보여주려면...
        self.tw_userid_mnt.verticalHeader().setVisible(False)  # row header 숨기기
        self.tw_userid_mnt.setEditTriggers(QAbstractItemView.NoEditTriggers)#수정 불가하게
        self.tw_userid_mnt.setSelectionBehavior(QAbstractItemView.SelectRows)#한줄씩 선택
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
