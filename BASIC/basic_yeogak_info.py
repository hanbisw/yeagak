from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QBrush, QRegExpValidator
from PyQt5.QtWidgets import *
import os

from config.mariadb_connection import mariadb_conn
import mariadb
from datetime import timedelta,datetime

# class StockIndexWindow(QMainWindow, form_class):
class Basic_yeogak_info_Window(QMainWindow):
    def __init__(self,pf_os,comp_code,user_id):
        super().__init__()
        self.move(10, 50)
        self.setFixedSize(1303, 857)
        if pf_os == 'Windows':
            option_ui = 'UiDir/basic_yeogak_info.ui'
        else:
            option_ui = 'UiDir/basic_yeogak_info.ui'
        self.comp_code = comp_code
        self.user_id = user_id
        # option_ui = 'UiDir/StockCompInfo.ui'
        uic.loadUi(option_ui, self)

        regExp = QRegExp("[0-9]*") #edit에 숫자만 입력 처리하기 위해
        self.ed_floor_st.setValidator(QRegExpValidator(regExp, self))
        # self.show()
        # self.setWindowTitle("기업 정보 자료 등록(StockCompInfo.py)")
        # self.rb_clicked_rtn() #첫 화면일 경우 셋팅하려면.....
        self.pb_floor_save.clicked.connect(self.floor_dbsave)  # 숙박으로 이용하는 층수 저장/수정
        self.pb_floor_delete.clicked.connect(self.floor_dbdelete)    # 숙박으로 이용하는 층수 삭제
        self.pb_floor_clear.clicked.connect(self.floor_clear)    # 숙박으로 이용하는 층수 edit clear
        self.pb_room_type_delete.clicked.connect(self.room_type_dbdelete)  # 객실 타입 삭제
        self.pb_room_type_save.clicked.connect(self.room_type_dbsave)  # 객실 타입  저장/수정
        self.pb_room_type_clear.clicked.connect(self.room_type_clear)  # 객실 타입  edit clear
        self.pb_room_name_save.clicked.connect(self.room_name_dbsave)  # 호실 정보 저장/수정
        self.pb_room_name_delete.clicked.connect(self.room_name_dbdelete)  # 호실 정보 삭제
        self.pb_room_name_clear.clicked.connect(self.room_name_clear)  # 호실 정보 edit clear
        self.tw_floor.clicked.connect(self.tw_floor_display) # 클릭시 층수를 ed_floor_st edit에 보여준다....
        self.tw_room_type.clicked.connect(self.tw_room_type_display) # 클릭시 객실 타입를 edit에 보여준다....
        self.tw_room_name.clicked.connect(self.tw_room_name_display) # 클릭시 호실 정보를 edit에 보여준다....
        self.rb_use_true.clicked.connect(self.rb_clicked_rtn)#사용 가능 클릭시
        self.rb_use_false.clicked.connect(self.rb_clicked_rtn)#사용 불가 클릭시
        self.tw_room_name.keyPressEvent = self.keyPressEvent #UP, DOWN 키를 누를 때 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
        self.first_sch()  # 처음 값을 가져와 뿌려준다.

    # def init_rtn(self):
    #키 이벤트 발생시
    def keyPressEvent(self, eventQKeyEvent):
        key = eventQKeyEvent.key()
        if key == Qt.Key_Up: #up 키를 누를 때마다  종목코드를 가져오려면....
            row = self.tw_room_name.currentRow() #현재 ROW 값을 가져오려면..
            if row == 0: # 처음 일때 값을 1로 하기 위해
                row += 1
            self.tw_room_name.setCurrentCell(row - 1, 0)  # 한 ROW 위로 이동
            self.cb_floor.setCurrentText(self.tw_room_name.item(self.tw_room_name.currentRow(), 0).text())  # 층수.
            self.cb_room_type.setCurrentText(self.tw_room_name.item(self.tw_room_name.currentRow(), 1).text())  # 객실타입.
            self.ed_room_name.setText(self.tw_room_name.item(self.tw_room_name.currentRow(), 2).text())  # 호실명.
            self.ed_room_name.setText(self.tw_room_name.item(self.tw_room_name.currentRow(), 2).text())  # 호실명.

            room_use = self.tw_room_name.item(self.tw_room_name.currentRow(), 3).text()  # 사용 가능 여부 선택
            if room_use == '사용':
                self.rb_use_true.setChecked(True)  # 사용 가능 체크시
                self.rb_clicked_rtn()  # 사용 가능 셋팅하려면.....
                # self.rb_use_false.setChecked(False)
            else:
                # self.rb_use_true.setChecked(False)
                self.rb_use_false.setChecked(True)  # 사용 불가 체크시
                self.rb_clicked_rtn()  # 사용 가능 셋팅하려면.....
                self.de_start_ilja.setDate(
                    datetime.strptime(self.tw_room_name.item(self.tw_room_name.currentRow(), 4).text(), '%Y-%m-%d'))  # 불가시작일자
                self.de_end_ilja.setDate(
                    datetime.strptime(self.tw_room_name.item(self.tw_room_name.currentRow(), 5).text(), '%Y-%m-%d'))  # 불가종료일자
                self.ed_bigo.setText(self.tw_room_name.item(self.tw_room_name.currentRow(), 6).text())  # 불가시 사유

        elif key == Qt.Key_Down:  # down 키를 누를 때마다  종목코드를 가져오려면....
            row = self.tw_room_name.currentRow() #현재 ROW 값을 가져오려면..
            if row >= (self.tw_room_name.rowCount() -1): #마지막 ROW일때 계속 마지막 종목코드를 주기위해
               row -= 1
            self.tw_room_name.setCurrentCell(row + 1, 0)  # 한 ROW 위로 이동
            self.cb_floor.setCurrentText(self.tw_room_name.item(self.tw_room_name.currentRow(), 0).text())  # 층수.
            self.cb_room_type.setCurrentText(self.tw_room_name.item(self.tw_room_name.currentRow(), 1).text())  # 객실타입.
            self.ed_room_name.setText(self.tw_room_name.item(self.tw_room_name.currentRow(), 2).text())  # 호실명.
            self.ed_room_name.setText(self.tw_room_name.item(self.tw_room_name.currentRow(), 2).text())  # 호실명.

            room_use = self.tw_room_name.item(self.tw_room_name.currentRow(), 3).text()  # 사용 가능 여부 선택
            if room_use == '사용':
                self.rb_use_true.setChecked(True)  # 사용 가능 체크시
                self.rb_clicked_rtn()  # 사용 가능 셋팅하려면.....
                # self.rb_use_false.setChecked(False)
            else:
                # self.rb_use_true.setChecked(False)
                self.rb_use_false.setChecked(True)  # 사용 불가 체크시
                self.rb_clicked_rtn()  # 사용 가능 셋팅하려면.....
                self.de_start_ilja.setDate(
                    datetime.strptime(self.tw_room_name.item(self.tw_room_name.currentRow(), 4).text(), '%Y-%m-%d'))  # 불가시작일자
                self.de_end_ilja.setDate(
                    datetime.strptime(self.tw_room_name.item(self.tw_room_name.currentRow(), 5).text(), '%Y-%m-%d'))  # 불가종료일자
                self.ed_bigo.setText(self.tw_room_name.item(self.tw_room_name.currentRow(), 6).text())  # 불가시 사유

    # 층수 edit clear
    def floor_clear(self):
        self.ed_floor_st.setText('')

    # 객실 타입  edit clear
    def room_type_clear(self):
        self.ed_room_type.setText('')

    # 호실 정보 edit clear
    def room_name_clear(self):
        self.ed_room_type.setText("")
        self.ed_floor_st.setText("")
        self.ed_room_name.setText("")
        self.ed_bigo.setText("")

        self.cb_floor.setCurrentIndex(0) #층수를 다시 가져오기 위해 초기화
        self.cb_room_type.setCurrentIndex(0) #객실 타입 다시 가져오기 위해 초기화
        self.rb_use_true.setChecked(True) #호실 정보 사용가능에 체크 초기화
        #숙박으로 이용하는 층수 조회


    #호실 사용 및 사용불가시 enable, disable 시키려면....
    def rb_clicked_rtn(self):
        if self.rb_use_true.isChecked() :
            # 현재 날짜를 db에서 가져오기
            mra = mariadb_conn().conn
            csr = mra.cursor()
            query_sel = "SELECT CURDATE() AS ILJA,DATE_ADD(CURDATE(), INTERVAL 1  day) AS ILJA01 "
            # print(query_sel)
            csr.execute(query_sel)
            rows = csr.fetchall()
            csr.close()
            mra.close()
            self.now_date = rows[0][0]#사용 불가시 오늘 날자보다 적을 경우에 비교하기 위해

            self.de_start_ilja.setDate(rows[0][0])#불가 시작일
            self.de_end_ilja.setDate(rows[0][1])#불가 종료일
            self.ed_bigo.setText('')#불가 사유 clear

            self.de_start_ilja.setDisabled(True)
            self.de_end_ilja.setDisabled(True)
            self.ed_bigo.setDisabled(True)
        else:
            self.de_start_ilja.setEnabled(True)
            self.de_end_ilja.setEnabled(True)
            self.ed_bigo.setEnabled(True)

    # 숙박으로 이용하는 층수 저장/수정
    def floor_dbsave(self):
        if self.ed_floor_st.text() is None or self.ed_floor_st.text() =='':
            QMessageBox.about(self, "정보", "층수를 입력하세요....")
        else:

            mra = mariadb_conn().conn
            csr = mra.cursor()
            query_in01 = "insert into yeogak_floor_info_tbl (comp_code,floor_st) " \
                         " values (%s,%s)"
                          # " values (:1,:2,0,0,0,0,'D')"
            t = (self.comp_code, self.ed_floor_st.text())
            try:
                csr.execute(query_in01, t)
                mra.commit()
            except mariadb.Error as e:
                print(f"Error: {e}")

            csr.close()
            mra.close()

            QMessageBox.about(self, "정보", self.ed_floor_st.text()+"층수가 저장/수정 되었습니다.....")
            self.first_sch()

    # 숙박으로 이용하는 층수 삭제
    def floor_dbdelete(self):
        if self.ed_floor_st.text() is None or self.ed_floor_st.text() =='':
            QMessageBox.about(self, "정보", "삭제 할 층수를 클릭하세요....")
        else:
            floor_st = int(self.ed_floor_st.text())
            mra = mariadb_conn().conn
            csr = mra.cursor()
            query_sel = "delete from yeogak_floor_info_tbl  "\
                         "WHERE comp_code = '" + self.comp_code + "' and floor_st =  " +str(floor_st)

            try:
                csr.execute(query_sel)
                mra.commit()
            except mariadb.Error as e:
                print(f"Error: {e}")

            csr.close()
            mra.close()

            QMessageBox.about(self, "정보", floor_st+" 층수는 삭제되었습니다.....")
            self.first_sch()

    # 객실 타입  저장/수정
    def room_type_dbsave(self):
        if self.ed_room_type.text() is None or self.ed_room_type.text() == '':
            QMessageBox.about(self, "정보", "객실 타입을 입력하세요....")
        else:

            mra = mariadb_conn().conn
            csr = mra.cursor()
            query_in01 = "insert into yeogak_room_type_info_tbl (comp_code,room_type) " \
                         " values (%s,%s)"
                          # " values (:1,:2,:3,'C1',0,0,0,0,'D')"
            t = (self.comp_code, self.ed_room_type.text())

            try:
                csr.execute(query_in01, t)
                mra.commit()
            except mariadb.Error as e:
                print(f"Error: {e}")

            csr.close()
            mra.close()
            QMessageBox.about(self, "정보",  self.ed_room_type.text()+"객실 타입이 저장/수정 되었습니다.....")
            self.first_sch()

    # 객실 타입 삭제
    def room_type_dbdelete(self):
        if self.ed_room_type.text() is None or self.ed_room_type.text() =='':
            QMessageBox.about(self, "정보", "삭제 할 객실 타입을 클릭하세요....")
        else:
            mra = mariadb_conn().conn
            csr = mra.cursor()
            query_sel = "delete from yeogak_room_type_info_tbl  "\
                         "WHERE comp_code = '" + self.comp_code + "' and room_type =  '" +self.ed_room_type.text() +"' "
            try:
                csr.execute(query_sel)
                mra.commit()
            except mariadb.Error as e:
                print(f"Error: {e}")

            csr.close()
            mra.close()
            QMessageBox.about(self, "정보", self.ed_room_type.text()+" 객실 타입을 삭제되었습니다.....")
            self.first_sch()

    # 호실 정보 저장/수정
    def room_name_dbsave(self):

        if self.ed_room_name.text() is None or self.ed_room_name.text() == '': #호실 사용 가능 여부 체크
            QMessageBox.about(self, "정보", "호실을 입력하세요....")
            self.ed_room_name.setFocus()
        else:
            if self.rb_use_true.isChecked(): #사용
                use_name = "1"
                start_ilja = ""  # 불가시작일자
                end_ilja = "" # 불가종료일자
                bigo = ""
                self.room_name_dbsave_rtn(use_name,start_ilja,end_ilja,bigo)#실제 저장 루틴
            else:
                use_name = "2" #불가
                if self.ed_bigo.text() is None or self.ed_bigo.text() == '':
                    QMessageBox.about(self, "정보", "사용 불가 사유를 입력하세요....")
                    self.ed_bigo.setFocus()
                else:
                    if self.now_date > self.de_start_ilja.date():#사용 불가 시작일자가 현재일자와 같거나 커야함
                        QMessageBox.about(self, "정보", "사용 불가 시작일자가 현재일자와 같거나 커야함! 정확히 입력하세요....")
                        self.de_start_ilja.setFocus()

                    elif self.de_start_ilja.date() > self.de_end_ilja.date():#사용 불가 기간에서 시작일자와 종료일자 비고
                        QMessageBox.about(self, "정보", "사용 불가 기간에서 시작일자와 종료일자를 정확히 입력하세요....")
                        self.de_start_ilja.setFocus()
                    else:
                        start_ilja = self.de_start_ilja.date().toString('yyyy-MM-dd')  # 불가시작일자
                        end_ilja = self.de_end_ilja.date().toString('yyyy-MM-dd')  # 불가종료일자
                        bigo = self.ed_bigo.text()
                        self.room_name_dbsave_rtn(use_name,start_ilja,end_ilja,bigo)#실제 저장 루틴

    def room_name_dbsave_rtn(self,use_name,start_ilja,end_ilja,bigo):  # 실제 저장 루틴

        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_in01 = "insert into yeogak_room_name_info_tbl (comp_code,room_name,floor_st,room_type,room_use," \
                     "room_start_ilja,room_end_ilja,room_bigo) " \
                     " values (%s,%s,%s,%s,%s,%s,%s,%s) " \
                     " ON DUPLICATE KEY UPDATE room_name=%s,floor_st=%s,room_type=%s," \
                     "room_use=%s,room_start_ilja=%s,room_end_ilja=%s,room_bigo=%s"
        t = (self.comp_code, self.ed_room_name.text(), self.cb_floor.currentText(), self.cb_room_type.currentText(),
             use_name, start_ilja, end_ilja, bigo,
             self.ed_room_name.text(), self.cb_floor.currentText(), self.cb_room_type.currentText(),
             use_name, start_ilja, end_ilja, bigo)
        # print(query_in01)
        try:
            csr.execute(query_in01, t)
            mra.commit()
        except mariadb.Error as e:
            print(f"Error: {e}")
        csr.close()
        mra.close()
        QMessageBox.about(self, "정보", self.ed_room_name.text() + "호실 저장/수정 되었습니다.....")
        self.first_sch()
    # 호실 정보 삭제
    def room_name_dbdelete(self):
        if self.ed_room_name.text() is None or self.ed_room_name.text() == '':
            QMessageBox.about(self, "정보", "호실 명을 입력하세요....")
        else:
            mra = mariadb_conn().conn
            csr = mra.cursor()
            query_sel = "delete from yeogak_room_name_info_tbl  "\
                         "WHERE comp_code = '" + self.comp_code + "' and "\
                         " room_name = '"+self.ed_room_name.text()+"' "
            # print(query_sel)
            try:
                csr.execute(query_sel)
                mra.commit()
            except mariadb.Error as e:
                print(f"Error: {e}")

            csr.close()
            mra.close()
            QMessageBox.about(self, "정보", self.ed_room_name.text() +  "호실 명이 삭제되었습니다.....")
            self.first_sch()

    # 클릭시 층수를 ed_floor_st edit에 보여준다....
    def tw_floor_display(self):
        row = self.tw_floor.currentRow()  # 현재 ROW 값을 가져오려면..
        self.tw_floor.setCurrentCell(row, 0)  # ROW 이동
        self.ed_floor_st.setText(self.tw_floor.item(self.tw_floor.currentRow(), 0).text())  # 층수 선택

        #print(self.ed_floor_st.text())
    # 클릭시 객실 타입를 edit에 보여준다....
    def tw_room_type_display(self):
        row = self.tw_room_type.currentRow()  # 현재 ROW 값을 가져오려면..
        self.tw_room_type.setCurrentCell(row, 0)  # 한 ROW 위로 이동
        self.ed_room_type.setText(self.tw_room_type.item(self.tw_room_type.currentRow(), 0).text())  # 객실 타입 선택.

    # 클릭시 호실 정보를 edit에 보여준다....
    def tw_room_name_display(self):

        row = self.tw_room_name.currentRow()  # 현재 ROW 값을 가져오려면..
        self.tw_room_name.setCurrentCell(row, 0)  # 한 ROW 위로 이동
        self.cb_floor.setCurrentText(self.tw_room_name.item(self.tw_room_name.currentRow(), 0).text())  # 층수.
        self.cb_room_type.setCurrentText(self.tw_room_name.item(self.tw_room_name.currentRow(), 1).text())  # 객실타입.
        self.ed_room_name.setText(self.tw_room_name.item(self.tw_room_name.currentRow(), 2).text())  # 호실명.
        self.ed_room_name.setText(self.tw_room_name.item(self.tw_room_name.currentRow(), 2).text())  # 호실명.

        room_use = self.tw_room_name.item(self.tw_room_name.currentRow(), 3).text() #사용 가능 여부 선택
        if room_use =='사용':
            self.rb_use_true.setChecked(True)#사용 가능 체크시
            self.rb_clicked_rtn()  # 사용 가능 셋팅하려면.....
            # self.rb_use_false.setChecked(False)
        else:
            # self.rb_use_true.setChecked(False)
            self.rb_use_false.setChecked(True)#사용 불가 체크시
            self.rb_clicked_rtn()  # 사용 가능 셋팅하려면.....
            self.de_start_ilja.setDate(datetime.strptime(self.tw_room_name.item(self.tw_room_name.currentRow(), 4).text(), '%Y-%m-%d'))  # 불가시작일자
            self.de_end_ilja.setDate(datetime.strptime(self.tw_room_name.item(self.tw_room_name.currentRow(), 5).text(), '%Y-%m-%d'))  # 불가종료일자
            self.ed_bigo.setText(self.tw_room_name.item(self.tw_room_name.currentRow(), 6).text())  # 불가시 사유


    #자료를 가져와 화면에 뿌려준다.
    def first_sch(self):
        self.floor_clear()#edit 부분을 초기화....
        self.room_type_clear()#edit 부분을 초기화....
        self.room_name_clear()#edit 부분을 초기화....
        self.rb_clicked_rtn()  # 사용 가능 셋팅하려면.....
        if self.cb_floor.currentText() is not None or self.cb_floor.currentText() !='':
            self.cb_floor.clear()  # 층수를 다시 가져오기 위해 초기화
        if self.cb_room_type.currentText() is not None or self.cb_room_type.currentText() !='':
           self.cb_room_type.clear()  # 객실 타입 다시 가져오기 위해 초기화

        #숙박으로 이용하는 층수 조회
        mra = mariadb_conn().conn
        csr = mra.cursor(dictionary=True) #딕셔너리 형태로 표현하기 위해....
        query_sel = "SELECT CAST(FLOOR_ST AS CHAR) AS FLOOR_ST FROM yeogak_floor_info_tbl WHERE comp_code = '" + self.comp_code + "'  ORDER BY floor_st "

        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        item_cnt = len(rows)
        self.tw_floor.setRowCount(item_cnt)
        style = "::section {""background-color: lightblue; }"
        self.tw_floor.horizontalHeader().setStyleSheet(style)
        #숙박으로 이용하는 층수
        for idx, col in enumerate(rows):
            self.tw_floor.setItem(idx, 0, QTableWidgetItem(col["FLOOR_ST"]))
            self.tw_floor.item(idx, 0).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.cb_floor.addItem(col["FLOOR_ST"])
        # self.tw_floor.setHorizontalHeaderLabels(headertitle)
        self.tw_floor.resizeRowsToContents()
        self.tw_floor.resizeColumnsToContents()#col 자릿수에 맡게 보여주려면...
        self.tw_floor.verticalHeader().setVisible(False)  # row header 숨기기
        self.tw_floor.setEditTriggers(QAbstractItemView.NoEditTriggers)#수정 불가하게
        self.tw_floor.setSelectionBehavior(QAbstractItemView.SelectRows)#한줄씩 선택
        #
        #객실타입 조회
        mra = mariadb_conn().conn
        csr = mra.cursor(dictionary=True) #딕셔너리 형태로 표현하기 위해....
        query_sel = "SELECT ROOM_TYPE FROM yeogak_room_type_info_tbl WHERE comp_code = '" + self.comp_code + "' ORDER BY room_type "
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        item_cnt = len(rows)
        self.tw_room_type.setRowCount(item_cnt)
        style = "::section {""background-color: lightblue; }"
        self.tw_room_type.horizontalHeader().setStyleSheet(style)
        #객실 타입 보여주기
        for idx, col in enumerate(rows):
            self.tw_room_type.setItem(idx, 0, QTableWidgetItem(col["ROOM_TYPE"]))
            self.cb_room_type.addItem(col["ROOM_TYPE"])

        self.tw_room_type.resizeRowsToContents()
        self.tw_room_type.resizeColumnsToContents()#col 자릿수에 맡게 보여주려면...
        self.tw_room_type.verticalHeader().setVisible(False)  # row header 숨기기
        self.tw_room_type.setEditTriggers(QAbstractItemView.NoEditTriggers)#수정 불가하게
        self.tw_room_type.setSelectionBehavior(QAbstractItemView.SelectRows)#한줄씩 선택

        #호실정보 조회
        mra = mariadb_conn().conn
        csr = mra.cursor(dictionary=True) #딕셔너리 형태로 표현하기 위해....
        query_sel = "SELECT CAST(FLOOR_ST AS CHAR) AS FLOOR_ST,ROOM_TYPE,ROOM_NAME,DECODE_ORACLE(ROOM_USE, 1, '사용','불가') AS ROOM_USE," \
                     "ROOM_START_ILJA,ROOM_END_ILJA,ROOM_BIGO " \
                     " FROM yeogak_room_name_info_tbl " \
                     "WHERE comp_code = '" + self.comp_code + "'  " \
                     "ORDER BY FLOOR_ST,ROOM_NAME "
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        item_cnt = len(rows)
        # self.tw_room_name.clear()
        # self.tw_room_name.setHorizontalHeaderLabels(["층수", "객실 타입", "호 실", "사용여부", "불가시작일", "불가종료일", "불가사유"])
        # self.tw_room_name.verticalHeader().setVisible(False)

        if item_cnt > 0:
            self.tw_room_name.setRowCount(item_cnt)
            style = "::section {""background-color: lightblue; }"
            self.tw_room_name.horizontalHeader().setStyleSheet(style)
            #호실 정보 보여주기
            for idx, col in enumerate(rows):
                self.tw_room_name.setItem(idx, 0, QTableWidgetItem(col["FLOOR_ST"]))
                self.tw_room_name.item(idx, 0).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.tw_room_name.setItem(idx, 1, QTableWidgetItem(col["ROOM_TYPE"]))
                self.tw_room_name.setItem(idx, 2, QTableWidgetItem(col["ROOM_NAME"]))
                self.tw_room_name.item(idx, 2).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.tw_room_name.setItem(idx, 3, QTableWidgetItem(col["ROOM_USE"]))
                self.tw_room_name.item(idx, 3).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.tw_room_name.setItem(idx, 4, QTableWidgetItem(col["ROOM_START_ILJA"]))
                self.tw_room_name.item(idx, 4).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.tw_room_name.setItem(idx, 5, QTableWidgetItem(col["ROOM_END_ILJA"]))
                self.tw_room_name.item(idx, 5).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.tw_room_name.setItem(idx, 6, QTableWidgetItem(col["ROOM_BIGO"]))

            self.tw_room_name.resizeRowsToContents()
            self.tw_room_name.resizeColumnsToContents()#col 자릿수에 맡게 보여주려면...
            self.tw_room_name.verticalHeader().setVisible(False)  # row header 숨기기
            self.tw_room_name.setEditTriggers(QAbstractItemView.NoEditTriggers)#수정 불가하게
            self.tw_room_name.setSelectionBehavior(QAbstractItemView.SelectRows)#한줄씩 선택

