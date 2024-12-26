from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QBrush, QRegExpValidator, QColor, QPalette, QFont
from PyQt5.QtWidgets import *

import webbrowser
import os

from config.mariadb_connection import mariadb_conn
import mariadb
from datetime import timedelta,datetime
# from function.inputtypehandler import InputTypeHandler

from function.inlink import inlink_url
# class StockIndexWindow(QMainWindow, form_class):
class Appcomp_use_info_Window(QMainWindow):
    def __init__(self,pf_os,comp_code,user_id):
        super().__init__()
        self.move(10, 50)
        self.setFixedSize(1600, 900)
        if pf_os == 'Windows':
            option_ui = 'UiDir/appcomp_use_info.ui'
        else:
            option_ui = 'UiDir/appcomp_use_info.ui'
        self.comp_code = comp_code
        self.user_id = user_id
        # option_ui = 'UiDir/StockCompInfo.ui'
        uic.loadUi(option_ui, self)

        regExp = QRegExp("[0-9--]*") #edit에 숫자만 입력 처리하기 위해
        self.ed_astel.setValidator(QRegExpValidator(regExp, self))
        self.pb_save.clicked.connect(self.appcomp_use_dbsave)  #  저장/수정
        self.pb_clear.clicked.connect(self.appcomp_use_clear)  #  edit clear

        self.tw_appcomp.clicked.connect(self.mouse_click_rtn) # 클릭시 입력란에 보여주려면.....
        self.tw_appcomp.keyPressEvent = self.keyPressEvent #UP, DOWN 키를 누를 때 입력란에 보여주려면.....
        self.tb_internet.clicked.connect(self.internet_sch)#링크 주소 인터넷으로 연결하기
        self.first_sch()  # 처음 값을 가져와 뿌려준다.

    #인터넷 링크 주소 연결하기
    def internet_sch(self):
        inlink_url(self.ed_homepage.text())#인트넷으로 연결하기

    #자료 저장 또는 수정 하려면....
    def appcomp_use_dbsave(self):
        #수정 사항이 있으면 저장하겠는지 묻는다
        if self.cb_use.isChecked():#마감 처리를 체크하려면...
            use_chk = 'Y'
        else:
            use_chk = ''
        if self.sch_yn == use_chk:
            QMessageBox.about(self, "정보", "수정할 자료가 없습니다...")
            self.pb_clear.setFocus()
        else:

            # 숙박어플 업체를 사용려면.....먼저 코드를 가져온다.
            mra = mariadb_conn().conn
            csr = mra.cursor()
            query_sel = "SELECT appcomp_code FROM appcomp_info_tbl a WHERE appcomp_name  = '"+self.sch_comp+"' "
            # print(query_sel)
            csr.execute(query_sel)
            rows = csr.fetchall()
            csr.close()
            mra.close()
            appcomp_code = rows[0][0]

            if use_chk == 'Y': #사용 한다면  appcomp_use_info_tbl 에 저장하려면......
                # 숙박 어플 업체를 저장하려면.....
                mra = mariadb_conn().conn
                csr = mra.cursor()

                query_in01 = "insert into appcomp_use_info_tbl (comp_code,appcomp_code,mnt_id) " \
                             " values (%s,%s,%s)"
                t = (self.comp_code, appcomp_code, self.user_id)
                try:
                    csr.execute(query_in01, t)
                    mra.commit()
                except mariadb.Error as e:
                    print(f"Error: {e}")
                csr.close()
                mra.close()
                QMessageBox.about(self, "정보", "자료가 처리되었습니다......")
                self.first_sch()

            else:#사용하지 않는 다면 appcomp_use_info_tbl 자료를 빼려면......
                # 클릭된 자료를 삭제한다.
                mra = mariadb_conn().conn
                csr = mra.cursor()
                query_sel = "delete from appcomp_use_info_tbl WHERE comp_code = %s AND appcomp_code = %s "
                t = (self.comp_code, appcomp_code,)
                try:
                    csr.execute(query_sel,t)
                    mra.commit()
                except mariadb.Error as e:
                    print(f"Error: {e}")

                csr.close()
                mra.close()
                QMessageBox.about(self, "정보", "자료가 처리되었습니다......")
                self.first_sch()



    #edit clear 및 초기화
    def appcomp_use_clear(self):
        self.cb_use.setChecked(False)  # 체크 시에...
        self.ed_comp.setText('')  #업체명을 뿌려준다.
        self.ed_astel.setText('') #대표번호를 뿌려준다.
        self.ed_homepage.setText('')# 홈페이지를 뿌려준다.
        self.save_mode = ''

    #KEY_UP, KEY_DOWN을 눌렀다면 .....
    def keyPressEvent (self, eventQKeyEvent):
        key = eventQKeyEvent.key()
        if key == Qt.Key_Up: #up 키를 누를 때마다  해당일자 호실의 정보를 상당 입력란에 보여주려면.....
            row = self.tw_appcomp.currentRow() #현재 ROW 값을 가져오려면..
            if row == 0: # 처음 일때 값을 1로 하기 위해
                row += 1
            self.tw_appcomp.setCurrentCell(row-1,0)  #한 ROW 위로 이동
            self.sch_yn = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 0).text()  #사용 여부를 읽는다.
            self.sch_comp = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 1).text()  #업체명을 읽는다.
            self.sch_astel = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 2).text()  #대표번호를 읽는다.
            self.sch_homepage = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 3).text()  # 홈페이지를 읽는다.
            self.display_rtn()#해당 일자의 정보를 화면에 보여준다.

        elif key == Qt.Key_Down:  # down 키를 누를 때마다  해당일자 호실의 정보를 상당 입력란에 보여주려면.....
            row = self.tw_appcomp.currentRow() #현재 ROW 값을 가져오려면..
            if row >= (self.tw_appcomp.rowCount() -1): #마지막 ROW일때 계속 마지막 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
               row -= 1
            self.tw_appcomp.setCurrentCell(row + 1, 0) #한 ROW 밑으로 이동
            self.sch_yn = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 0).text()  #사용 여부를 읽는다.
            self.sch_comp = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 1).text()  #업체명을 읽는다.
            self.sch_astel = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 2).text()  #대표번호를 읽는다.
            self.sch_homepage = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 3).text()  # 홈페이지를 읽는다.
            self.display_rtn()#해당 일자의 정보를 화면에 보여준다.

    # 클릭시 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
    def mouse_click_rtn(self):
        row = self.tw_appcomp.currentRow() #현재 ROW 값을 가져오려면..
        self.tw_appcomp.setCurrentCell(row, 0)  # ROW 이동
        self.sch_yn = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 0).text()  #사용 여부를 읽는다.
        self.sch_comp = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 1).text()  #업체명을 읽는다.
        self.sch_astel = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 2).text()  #대표번호를 읽는다.
        self.sch_homepage = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 3).text()  # 홈페이지를 읽는다.
        self.display_rtn()#해당 일자의 정보를 화면에 보여준다.

    #화면에 뿌려주려면....
    def display_rtn(self):
        if self.sch_yn == 'Y':#ID 일시 중단
            self.cb_use.setChecked(True)  # 체크 시에...
        else:
            self.cb_use.setChecked(False)  # 체크 시에...
        self.ed_comp.setText(self.sch_comp)  #업체명을 뿌려준다.
        self.ed_astel.setText(self.sch_astel) #대표번호를 뿌려준다.
        self.ed_homepage.setText(self.sch_homepage)# 홈페이지를 뿌려준다.
        self.save_mode = 'up'

    #자료를 가져와 화면에 뿌려준다.
    def first_sch(self):
        self.appcomp_use_clear()#edit 부분을 초기화....

        #호실정보 조회
        mra = mariadb_conn().conn
        csr = mra.cursor(dictionary=True) #딕셔너리 형태로 표현하기 위해....
        query_sel = ("SELECT DECODE_ORACLE(IFNULL(B.APPCOMP_CODE, '' ),'','','Y')  AS USE01,A.APPCOMP_CODE,A.APPCOMP_NAME,A.APPCOMP_ASTEL,A.APPCOMP_HOMEPAGE "
                     " FROM appcomp_info_tbl a left outer join appcomp_use_info_tbl b"
                     " ON a.appcomp_code = b.appcomp_code and b.comp_code = '"+self.comp_code+"'"
                     " ORDER BY A.APPCOMP_CODE ")
        #t=self.comp_code
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        item_cnt = len(rows)
        self.tw_appcomp.setRowCount(item_cnt)
        style = "::section {""background-color: lightblue; }"
        self.tw_appcomp.horizontalHeader().setStyleSheet(style)
        self.tw_appcomp.resizeRowsToContents()

        if item_cnt > 0:
            #호실 정보 보여주기
            for idx, col in enumerate(rows):
                self.tw_appcomp.setItem(idx, 0, QTableWidgetItem(col["USE01"]))
                self.tw_appcomp.item(idx, 0).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.tw_appcomp.setItem(idx, 1, QTableWidgetItem(col["APPCOMP_NAME"]))
                self.tw_appcomp.item(idx, 1).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.tw_appcomp.setItem(idx, 2, QTableWidgetItem(col["APPCOMP_ASTEL"]))
                self.tw_appcomp.setItem(idx, 3, QTableWidgetItem(col["APPCOMP_HOMEPAGE"]))
                self.tw_appcomp.item(idx, 3).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

                if col["USE01"] =='Y': #사용여부에서 Y 즉 사용하면 노란색으로
                    self.tw_appcomp.item(idx, 0).setBackground(QBrush(QColor(255, 255, 0)))
                    self.tw_appcomp.item(idx, 1).setBackground(QBrush(QColor(255, 255, 0)))
                    self.tw_appcomp.item(idx, 2).setBackground(QBrush(QColor(255, 255, 0)))
                    self.tw_appcomp.item(idx, 3).setBackground(QBrush(QColor(255, 255, 0)))

            self.tw_appcomp.resizeColumnsToContents()#col 자릿수에 맡게 보여주려면...
            self.tw_appcomp.verticalHeader().setVisible(False)  # row header 숨기기
            self.tw_appcomp.setEditTriggers(QAbstractItemView.NoEditTriggers)#수정 불가하게
            self.tw_appcomp.setSelectionBehavior(QAbstractItemView.SelectRows)#한줄씩 선택

