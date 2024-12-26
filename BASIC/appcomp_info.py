from PyQt5.QtWidgets import *
from PyQt5 import uic
# from PyQt5.QtCore import *
from PyQt5.QtGui import QBrush, QRegExpValidator
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QRegExp
import webbrowser
import os

from config.mariadb_connection import mariadb_conn
import mariadb
from datetime import timedelta,datetime
# from function.inputtypehandler import InputTypeHandler
from function.inlink import inlink_url

# class StockIndexWindow(QMainWindow, form_class):
class Appcomp_info_Window(QWidget):
    def __init__(self,pf_os,comp_code,user_id):
        super().__init__()
        self.move(10, 50)
        self.setFixedSize(1600, 900)
        # self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        # self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        if pf_os == 'Windows':
            option_ui = 'UiDir/appcomp_info.ui'
        else:
            option_ui = 'UiDir/appcomp_info.ui'
        self.comp_code = comp_code
        self.user_id = user_id
        # option_ui = 'UiDir/StockCompInfo.ui'
        uic.loadUi(option_ui, self)
        # self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        regExp = QRegExp("[0-9--]*") #edit에 숫자만 입력 처리하기 위해
        self.ed_astel.setValidator(QRegExpValidator(regExp, self))
        self.pb_save.clicked.connect(self.appcomp_dbsave)  #  저장/수정
        self.pb_delete.clicked.connect(self.appcomp_dbdelete)  #  삭제
        self.pb_clear.clicked.connect(self.appcomp_clear)  #  edit clear

        self.tw_appcomp.clicked.connect(self.mouse_click_rtn) # 클릭시 입력란에 보여주려면.....
        self.tw_appcomp.keyPressEvent = self.keyPressEvent #UP, DOWN 키를 누를 때 입력란에 보여주려면.....
        self.tb_internet.clicked.connect(self.internet_sch)#링크 주소 인터넷으로 연결하기
        self.first_sch()  # 처음 값을 가져와 뿌려준다.

    #인터넷 링크 주소 연결하기
    def internet_sch(self):
        inlink_url(self.ed_homepage.text())#인트넷으로 연결하기

    #자료 저장 또는 수정 하려면....
    def appcomp_dbsave(self):
        if self.ed_comp.text() is None or self.ed_comp.text() =='':
            QMessageBox.about(self, "정보", "업체명을 입력하세요.....")
            self.ed_comp.setFocus()
        else:
            if self.ed_astel.text() is None or self.ed_astel.text() =='':
                QMessageBox.about(self, "정보", "대표번호를 입력하세요.....")
                self.ed_astel.setFocus()
            else:
                if self.ed_homepage.text() is None or self.ed_homepage.text() =='':
                    QMessageBox.about(self, "정보", "홈페이지를 입력하세요.....")
                    self.ed_homepage.setFocus()
                else:
                    if self.save_mode == 'up':#업데이트 하려면..
                        #변경사항이 있는지 먼저 알아보고 변경사항이 있으면 update한다...
                        if self.sch_comp == self.ed_comp.text() and self.sch_astel == self.ed_astel.text() and self.sch_homepage == self.ed_homepage.text():
                            QMessageBox.about(self, "정보", "수정할 자료가 없습니다...")
                            self.ed_comp.setFocus()
                        else:
                            # 업데이트 하려면.....
                            mra = mariadb_conn().conn
                            csr = mra.cursor()

                            query_in01 = "update appcomp_info_tbl set appcomp_name=%s,appcomp_astel=%s,appcomp_homepage=%s " \
                                         " WHERE appcomp_code=(SELECT appcomp_code FROM appcomp_info_tbl where appcomp_name = %s) "
                            t = (self.ed_comp.text(), self.ed_astel.text(),self.ed_homepage.text(),self.sch_comp)
                            try:
                                csr.execute(query_in01, t)
                                mra.commit()
                            except mariadb.Error as e:
                                print(f"Error: {e}")
                            csr.close()
                            mra.close()

                            QMessageBox.about(self, "정보", "자료가 수정되었습니다.....")
                            self.first_sch()
                    else:
                        #숙박 어플 업체를 저장하려면.....
                        mra = mariadb_conn().conn
                        csr = mra.cursor()

                        query_in01 = "insert into appcomp_info_tbl (appcomp_name,appcomp_astel,appcomp_homepage) " \
                                     " values (%s,%s,%s)"
                        t = (self.ed_comp.text(), self.ed_astel.text(),self.ed_homepage.text())
                        try:
                            csr.execute(query_in01, t)
                            mra.commit()
                        except mariadb.Error as e:
                            print(f"Error: {e}")
                        csr.close()
                        mra.close()

                        QMessageBox.about(self, "정보", "자료가 처리되었습니다....")
                        self.first_sch()

    #자료를 삭제하려면....
    def appcomp_dbdelete(self):
        if self.ed_comp.text() is None or self.ed_comp.text() =='':
            QMessageBox.about(self, "정보", "삭제할 자료를 선택하세요.....")
        else:
            reply = QMessageBox.question(self, 'Message', '선택한 자료를 삭제하시겠습니까?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes: #예약을 저장하려면....
                # 한번이도 사용이 있는 업체라면 자료를 삭제를 못하게 하려면.....
                mra = mariadb_conn().conn
                csr = mra.cursor()
                query_sel = ("SELECT (SELECT COUNT(*) FROM appcomp_use_info_tbl where appcomp_code = a.appcomp_code) as use_cnt,"
                             "(SELECT count(*) FROM yeogak_reserve_tbl where reserve_site =a.appcomp_code) as site_cnt"
                             " FROM appcomp_info_tbl a WHERE appcomp_name  = '"+self.sch_comp+"'")
                # print(query_sel)
                # t=(self.sch_comp)
                csr.execute(query_sel)
                rows = csr.fetchall()
                csr.close()
                mra.close()

                if rows[0][0] > 0 or rows[0][1] > 0:
                    QMessageBox.about(self, "정보", "현재 자료는 사용 중입니다 삭제 할 수 없습니다....")
                    self.appcomp_clear()
                else:
                    self.dbdelete()
                    QMessageBox.about(self, "정보", "자료가 삭제되었습니다......")
                    self.first_sch()
            else:
                self.appcomp_clear()
    # 자료를 삭세 한다.
    def dbdelete(self):
        # 클릭된 자료를 삭제한다.
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_sel = "delete from appcomp_info_tbl " \
                    " WHERE appcomp_name = '" + self.sch_comp + "' "
        try:
            csr.execute(query_sel)
            mra.commit()
        except mariadb.Error as e:
            print(f"Error: {e}")

        csr.close()
        mra.close()

    #edit clear 및 초기화
    def appcomp_clear(self):
        self.ed_comp.setText('')  #업체명을 뿌려준다.
        self.ed_astel.setText('') #대표번호를 뿌려준다.
        self.ed_homepage.setText('')# 홈페이지를 뿌려준다.
        self.save_mode = 'sa'

    #KEY_UP, KEY_DOWN을 눌렀다면 .....
    def keyPressEvent (self, eventQKeyEvent):
        key = eventQKeyEvent.key()
        if key == Qt.Key_Up: #up 키를 누를 때마다  해당일자 호실의 정보를 상당 입력란에 보여주려면.....
            row = self.tw_appcomp.currentRow() #현재 ROW 값을 가져오려면..
            if row == 0: # 처음 일때 값을 1로 하기 위해
                row += 1
            self.tw_appcomp.setCurrentCell(row-1,0)  #한 ROW 위로 이동
            self.sch_comp = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 0).text()  #업체명을 읽는다.
            self.sch_astel = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 1).text()  #대표번호를 읽는다.
            self.sch_homepage = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 2).text()  # 홈페이지를 읽는다.
            self.display_rtn()#해당 일자의 정보를 화면에 보여준다.

        elif key == Qt.Key_Down:  # down 키를 누를 때마다  해당일자 호실의 정보를 상당 입력란에 보여주려면.....
            row = self.tw_appcomp.currentRow() #현재 ROW 값을 가져오려면..
            if row >= (self.tw_appcomp.rowCount() -1): #마지막 ROW일때 계속 마지막 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
               row -= 1
            self.tw_appcomp.setCurrentCell(row + 1, 0) #한 ROW 밑으로 이동
            self.sch_comp = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 0).text()  #업체명을 읽는다.
            self.sch_astel = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 1).text()  #대표번호를 읽는다.
            self.sch_homepage = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 2).text()  # 홈페이지를 읽는다.
            self.display_rtn()#해당 일자의 정보를 화면에 보여준다.

    # 클릭시 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
    def mouse_click_rtn(self):
        row = self.tw_appcomp.currentRow() #현재 ROW 값을 가져오려면..
        self.tw_appcomp.setCurrentCell(row, 0)  # ROW 이동
        self.sch_comp = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 0).text()  #업체명을 읽는다.
        self.sch_astel = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 1).text()  #대표번호를 읽는다.
        self.sch_homepage = self.tw_appcomp.item(self.tw_appcomp.currentRow(), 2).text()  # 홈페이지를 읽는다.
        self.display_rtn()#해당 일자의 정보를 화면에 보여준다.

    #화면에 뿌려주려면....
    def display_rtn(self):
        self.ed_comp.setText(self.sch_comp)  #업체명을 뿌려준다.
        self.ed_astel.setText(self.sch_astel) #대표번호를 뿌려준다.
        self.ed_homepage.setText(self.sch_homepage)# 홈페이지를 뿌려준다.
        self.save_mode = 'up'

    #자료를 가져와 화면에 뿌려준다.
    def first_sch(self):
        self.appcomp_clear()#edit 부분을 초기화....

        #호실정보 조회
        mra = mariadb_conn().conn
        csr = mra.cursor(dictionary=True) #딕셔너리 형태로 표현하기 위해....
        query_sel = "SELECT APPCOMP_CODE,APPCOMP_NAME,APPCOMP_ASTEL,APPCOMP_HOMEPAGE " \
                     " FROM appcomp_info_tbl  ORDER BY APPCOMP_CODE "
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
                self.tw_appcomp.setItem(idx, 0, QTableWidgetItem(col["APPCOMP_NAME"]))
                self.tw_appcomp.item(idx, 0).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.tw_appcomp.setItem(idx, 1, QTableWidgetItem(col["APPCOMP_ASTEL"]))
                self.tw_appcomp.setItem(idx, 2, QTableWidgetItem(col["APPCOMP_HOMEPAGE"]))
                self.tw_appcomp.item(idx, 2).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)


            self.tw_appcomp.resizeColumnsToContents()#col 자릿수에 맡게 보여주려면...
            self.tw_appcomp.verticalHeader().setVisible(False)  # row header 숨기기
            self.tw_appcomp.setEditTriggers(QAbstractItemView.NoEditTriggers)#수정 불가하게
            self.tw_appcomp.setSelectionBehavior(QAbstractItemView.SelectRows)#한줄씩 선택

