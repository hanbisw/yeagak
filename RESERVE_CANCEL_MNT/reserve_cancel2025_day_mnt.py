from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QBrush, QRegExpValidator, QColor, QPalette, QFont
from PyQt5.QtWidgets import *

import pandas as pd
import subprocess
import webbrowser
import os

from config.mariadb_connection import mariadb_conn
import mariadb
from datetime import timedelta,datetime
# from function.inputtypehandler import InputTypeHandler


# class StockIndexWindow(QMainWindow, form_class):
class Reserve_cancel2025_day_mnt_Window(QMainWindow):
    def __init__(self,pf_os,comp_code,user_id):
        super().__init__()
        self.move(10, 50)
        self.setFixedSize(1543, 903)
        if pf_os == 'Windows':
            option_ui = 'UiDir/reserve_cancel2025_day_mnt.ui'
        else:
            option_ui = 'UiDir/reserve_cancel2025_day_mnt.ui'


        self.comp_code = comp_code
        self.user_id = user_id
        # option_ui = 'UiDir/StockCompInfo.ui'
        uic.loadUi(option_ui, self)

        regExp = QRegExp("[0-9]*") #edit에 숫자만 입력 처리하기 위해
        palette = QPalette()
        palette.setColor(QPalette.Highlight, QColor(144, 153, 234))  # default ==> Qt.darkBlue
        # palette.setColor(QPalette.HighlightedText, Qt.red)  # default ==> Qt.white
        self.tw_reserve.setPalette(palette)

        self.ed_cancel_sum.setValidator(QRegExpValidator(regExp, self))#숫자 만 입력 하려면.....
        self.str_ = '-'  # 203-1호실일때 -호일이 있는가를 찾으려면.....
        self.sch_room_name = ''  # 첫 화면시 호실 정보가 없는 경우에.....
        self.init_rtn()#오늘 일자를 먼저 보여주려면......
        self.pb_search.clicked.connect(self.select_rtn)  # 자료 조회
        self.pb_save.clicked.connect(self.reserve_dbsave)  # 자료 저장/수정
        self.pb_clear.clicked.connect(self.reserve_clear)  # 저장 화면을 클리어

        self.tw_reserve.clicked.connect(self.mouse_click_rtn) # 클릭시 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
        self.tw_reserve.keyPressEvent = self.keyPressEvent #UP, DOWN 키를 누를 때 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
        self.ed_cancel_sum.textChanged.connect(self.cancel_sum_check)#백만원 이상 입력하면 메지지를 나오게 하려면...
        self.ed_cancel_sum.returnPressed.connect(self.cancel_sum_check)#백만원 이상 입력하면 메지지를 나오게 하려면...
        self.first_sch()  # 첫 화면시 현재일자를 검색해온다.

    #오늘 일자를 먼저 보여주려면....
    def init_rtn(self):

        self.find_row='' # qtable에 현재 row 보여 주려면...  refresh 시
        # 현재 일자를 검색
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_sel = ("SELECT date_format(date_add(CURDATE(), INTERVAL -1  day),'%Y-%m-%d'),"
                     "date_format(CURDATE(),'%Y-%m-%d'),CURDATE() AS ILJA,DATE_ADD(CURDATE(), INTERVAL 1  day) from dual ")
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        self.yesterday_chk = rows[0][0]
        start_ilja = rows[0][0]
        end_ilja = rows[0][1]
        self.now_date = str(rows[0][2])  # 오늘 일자를 기준으로 자료의 입력을 결정하기 위해

        self.de_start_ilja_sch.setDate(datetime.strptime(start_ilja, '%Y-%m-%d'))  # 기간 조회 시작일자
        self.de_end_ilja_sch.setDate(datetime.strptime(end_ilja, '%Y-%m-%d'))  # 기간 조회 종료일자

        # # 호실 정보 조회
        # mra = mariadb_conn().conn
        # csr = mra.cursor(dictionary=True) #딕셔너리 형태로 표현하기 위해....
        # query_sel = "SELECT room_name FROM yeogak_room_name_info_tbl WHERE comp_code = '" + self.comp_code + "'  ORDER BY room_name "
        # # print(query_sel)
        # csr.execute(query_sel)
        # rows = csr.fetchall()
        # csr.close()
        # mra.close()
        # item_cnt = len(rows)
        # self.cb_room_name_sch.addItem('전체')#빈줄을 하나입력한다.
        # #호실 정보 조회
        # for idx, col in enumerate(rows):
        #     self.cb_room_name_sch.addItem(str(col["room_name"]))

        # 환불수단 정보 조회
        mra = mariadb_conn().conn
        csr = mra.cursor(dictionary=True) #딕셔너리 형태로 표현하기 위해....
        query_sel = "SELECT CODE_NAME FROM YEOGAK_CODE_TBL WHERE CODE_ID = 'CPY' ORDER BY CODE01"
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        self.cb_cancel_payment.insertItem(0,'')
        #결재수단 정보 조회
        for idx, col in enumerate(rows):
            self.cb_cancel_payment.insertItem(idx+1,col["CODE_NAME"])


    # 결재 금액을 1천만원 이상이면 체크하여 메시지를 주려면....
    def cancel_sum_check(self):
        if self.chk_cancel_sum_po != 'y':#table에서 마우스 클릭 및 위,아래 키보드 눌러서 화면에 보일때는 통과하려면.....
            sum = self.ed_cancel_sum.text().replace(',', '')
            if sum is None or sum == '':
                pass
            else:
                if int(sum) > 1000000:
                    reply = QMessageBox.question(self, 'Message', "입력하신 금액이 "+format(int(sum), ',')+"원 맞습니까?",
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.Yes:  # 입실일자와 퇴실일자의 기간중에서 겹치지만 그래도 저장을 하려면 아래에서 실행
                        self.chk_cancel_sum_po = 'y'
                        self.ed_cancel_sum.setText(format(int(sum), ','))
                        self.ed_cancel_sum.setFocus()
                    else:
                        self.chk_cancel_sum_po = 'y'
                        self.ed_cancel_sum.setText("")
                        self.ed_cancel_sum.setFocus()
                else:
                    self.chk_cancel_sum_po = 'n'
                    self.ed_cancel_sum.setText(format(int(sum), ','))
        else:
            self.chk_cancel_sum_po = 'n'
    def select_rtn(self):
        if self.de_start_ilja_sch.date() > self.de_end_ilja_sch.date():
            QMessageBox.about(self, "정보", "일자를 정확히 입력하세요....")
            self.de_start_ilja_sch.setFocus()
        else:
            self.first_sch()

    # 자료 저장/수정
    def reserve_dbsave(self):
        if self.cb_cancel_payment.currentText() is None or self.cb_cancel_payment.currentText() =='':#환불 수단에 값이 없는 경우 물어보려면....
            reply = QMessageBox.question(self, 'Message', '환불 수단이 없읍니다. 그래도 저장하시겠습니까?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.No: # 환불 사항이 없이 자료 저장
                # self.cb_cancel_payment.setFocus()
                self.ed_cancel_sum.setFocus()
            else: # yes 선택
                # 취소 사유를 꼭 입력해야 한다면.....
                if self.ed_cancel_bigo.text() is None or self.ed_cancel_bigo.text() == '':
                    QMessageBox.about(self, "정보", "취소 사유는 꼭 입력하세요....")
                    self.ed_cancel_bigo.setFocus()
                else: #마지막으로 자료 저장을 묻고 cancel_dbsave로 이동한다.
                    reply = QMessageBox.question(self, 'Message', '예약 취소 자료를 저장하시겠습니까?',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                    if reply == QMessageBox.Yes:
                        # self.cb_cancel_payment.setFocus()
                        self.cancel_dbsave()#마지막으로 자료 저장을 묻고 cancel_dbsave로 이동한다.

                    else: #no선택시
                        self.ed_cancel_sum.setFocus() # 포커스를 금액으로 이동한다.
        else: #환불 수단을 선택되었다면....
            # 환불 수단에 값이 있는 경우 금액을 꼭 입력해야 한다면.....
            if self.ed_cancel_sum.text() is None or self.ed_cancel_sum.text() == ''  or self.ed_cancel_sum.text() == '0':
                QMessageBox.about(self, "정보", "환불 금액을 입력하세요....")
                self.ed_cancel_sum.setFocus()

            # 취소 사유를 꼭 입력해야 한다면.....
            else:
                if self.ed_cancel_bigo.text() is None or self.ed_cancel_bigo.text() == '':
                    QMessageBox.about(self, "정보", "취소 사유는 꼭 입력하세요....")
                    self.ed_cancel_bigo.setFocus()
                else :
                    reply = QMessageBox.question(self, 'Message', '예약 취소 자료를 저장하시겠습니까?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                    if reply == QMessageBox.Yes:
                        # self.cb_cancel_payment.setFocus()
                        self.cancel_dbsave()

                    else:
                        self.ed_cancel_sum.setFocus()

    def cancel_dbsave(self):
        # 실질적인 자료를 저장은 여기서 부터 ........
        cancel_start_ilja = self.ed_cancel_start_ilja.text()
        cancel_end_ilja = self.ed_cancel_end_ilja.text()
        reserve_num = self.ed_reserve_number.text()

        cancel_payment = self.cb_cancel_payment.currentText()  # 환불수단
        if cancel_payment is None or cancel_payment =='':
            cancel_payment_code = ''#추가 결재수단 code값을 가져온다
        else:
            #코드 값 가져오기
            mra = mariadb_conn().conn
            csr = mra.cursor()
            query_sel = "SELECT FN_CODE_CODE('CPY','"+cancel_payment+"') "
            # print(query_sel)
            csr.execute(query_sel)
            rows = csr.fetchall()
            csr.close()
            mra.close()
            cancel_payment_code = rows[0][0] #추가 결재수단 code값을 가져온다
        cancel_sum = self.ed_cancel_sum.text()
        cancel_bigo = self.ed_cancel_bigo.text()
        #환불 금액 입력하려면......
        if self.ed_cancel_sum.text() == '' or self.ed_cancel_sum.text() is None or self.ed_cancel_sum.text() == '0':
            cancel_sum = '0'
        else:
            cancel_sum = self.ed_cancel_sum.text().replace(',', '')#환불 금액
        # print('aaaaaaaaaaaaaaaaaaa')

        # 해당일 회사,일자,호실, 사용가능 방을  select해서 key_ilja
        mra = mariadb_conn().conn
        csr = mra.cursor()  # 딕셔너리 형태로 표현하기 위해....
        query_sel = "SELECT DATE_FORMAT(KEY_ILJA, '%Y-%m-%d %H:%i:%s') AS KEY_ILJA FROM yeogak_reserve2025_tbl  " \
                    " WHERE comp_code='" + self.comp_code + "' AND room_ilja='" + self.sch_ilja + "' AND reserve_name='" + self.sch_reserve_name + "' AND cancel_chk = '0' "
        # print(query_sel)

        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        key_ilja = rows[0][0]

        # 취소에 해당하는 일을 검색하여 cancel_chk 필더에 '1'로 변경하는 작업을 하려면.......
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_in01 = ("UPDATE yeogak_reserve2025_tbl SET reserve_start_ilja=%s,reserve_end_ilja=%s,cancel_chk='1' "
                      " WHERE comp_code=%s AND key_ilja=%s AND "
                      " reserve_name=%s AND "
                      " room_ilja BETWEEN %s AND DATE_ADD(%s, INTERVAL -1  day)  ")
        # print(query_in01)
        t= (cancel_start_ilja,cancel_end_ilja,self.comp_code,key_ilja,self.sch_reserve_name,cancel_start_ilja,cancel_end_ilja)
        try:
            csr.execute(query_in01,t)
            mra.commit()
        except mariadb.Error as e:
            print(f"Error: {e}")
        csr.close()
        mra.close()

        #남아 있는 예약 현황에 퇴실일자를 숙박하고자 하는 일자까지 변경해주려 한다면.......
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_in01 = "UPDATE yeogak_reserve2025_tbl SET reserve_end_ilja='" + cancel_start_ilja + "' " \
                      " WHERE comp_code='" + self.comp_code + "' AND key_ilja='" + key_ilja + "' AND " \
                      " room_name='" + self.sch_room_name + "' AND cancel_chk = '0' "
        # print(query_in01)
        try:
            csr.execute(query_in01)
            mra.commit()
        except mariadb.Error as e:
            print(f"Error: {e}")
        csr.close()
        mra.close()

        #예약 취소 내용의 자료를 yeogak_reserve_cancel_tbl에 자료를 저장하려면.....
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_in01 = "insert into yeogak_reserve2025_cancel_tbl (comp_code,key_ilja,cancel_ilja,reserve_number,cancel_start_ilja," \
                     "cancel_end_ilja,cancel_payment,cancel_sum,mnt_id,cancel_bigo) " \
                     " values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
        t = (self.comp_code, key_ilja, self.now_date , reserve_num, cancel_start_ilja, cancel_end_ilja,
             cancel_payment_code, cancel_sum,self.user_id, cancel_bigo)
        try:
            csr.execute(query_in01, t)
            mra.commit()
        except mariadb.Error as e:
            print(f"Error: {e}")
        csr.close()
        mra.close()

        QMessageBox.about(self, "정보", "예약 취소 자료가 저장되었습니다.....")
        self.first_sch()

    # 클릭시 층수를 ed_floor_st edit에 보여준다....
    def reserve_clear(self):
        self.ed_name.setText("")  # 예약자
        self.ed_reserve_number.setText("")  # 예약번호
        self.ed_room_name.setText("")  # 호실
        self.ed_room_type.setText("")  # 호실 타입
        self.ed_sum.setText("")  # 결재 금액
        self.ed_worker.setText("")  # 당일 근무자
        self.ed_bigo.setText("")  # 요구사항
        self.ed_special_note.setText("")  # 특이사항
        self.ed_select_ilja.setText("")  # 선택일자
        self.ed_addsum.setText("")  # 추가 금액
        self.ed_expec_sum.setText("")  # 예상 금액
        self.ed_addbigo.setText("")  # 추가결재 비고
        self.ed_reserve_ilja.setText("")#예약일자
        self.ed_start_ilja.setText("")#입실일자
        self.ed_end_ilja.setText("")#퇴실일자

        self.ed_reserve_site.setText("") #예약 사이트 다시 가져오기 위해 초기화
        self.ed_payment.setText("") #결재수단 정보 다시 가져오기 위해 초기화
        self.ed_addpayment.setText("") #추가 결재수단 정보 다시 가져오기 위해 초기화
        self.ed_cancel_start_ilja.setText("")#예약 현재일을 가져와 취소 시작일자로 한다. 10박중 5박만 취소하는 경우....
        self.ed_cancel_end_ilja.setText("")#퇴실일자는 그래로 가져와 마지막을 표시한다.
        self.ed_mnt_id.setText(self.user_id)#로그인 id를 보여주고 취소 자료 처리를 누가 했는지를 알기 위해......
        self.ed_cancel_sum.setText("")#환불 금액을 초기화
        self.ed_cancel_bigo.setText("")#예약 취소 사유를 초기화
        self.cb_cancel_payment.setCurrentIndex(0)#환불 결재수단 정보 다시 가져오기 위해 초기화
        #기준일 메시지
        # self.lb_msg.setText("")#메시지를 초기화한다.

        self.edit_disabled()#취소 현황 내용도 입력못하도록 막아 준다.

    # 클릭시 객실 타입를 edit에 보여준다....
    def tw_room_type_display(self):
        row = self.tw_room_type.currentRow()  # 현재 ROW 값을 가져오려면..
        self.tw_room_type.setCurrentCell(row, 0)  # 한 ROW 위로 이동
        self.ed_room_type.setText(self.tw_room_type.item(self.tw_room_type.currentRow(), 0).text())  # 객실 타입 선택.

    #KEY_UP, KEY_DOWN을 눌렀다면 .....
    def keyPressEvent (self, eventQKeyEvent):
        key = eventQKeyEvent.key()
        if key == Qt.Key_Up: #up 키를 누를 때마다  해당일자 호실의 정보를 상당 입력란에 보여주려면.....
            row = self.tw_reserve.currentRow() #현재 ROW 값을 가져오려면..
            if row == 0: # 처음 일때 값을 1로 하기 위해
                row += 1
            self.tw_reserve.setCurrentCell(row-1,0)  #한 ROW 위로 이동
            self.sch_ilja = self.tw_reserve.item(self.tw_reserve.currentRow(), 0).text()  #해당일자를 읽는다.
            self.sch_room_name = self.tw_reserve.item(self.tw_reserve.currentRow(), 2).text()  # 호실명을 읽는다.
            self.sch_room_type = self.tw_reserve.item(self.tw_reserve.currentRow(), 3).text()  # 호실 타입을 읽는다.
            self.sch_start_ilja = self.tw_reserve.item(self.tw_reserve.currentRow(), 9).text()  # 일자를 읽는다.
            self.reserve_clear()
            self.search_rtn()#해당 일자의 정보를 화면에 보여준다.

        elif key == Qt.Key_Down:  # down 키를 누를 때마다  해당일자 호실의 정보를 상당 입력란에 보여주려면.....
            row = self.tw_reserve.currentRow() #현재 ROW 값을 가져오려면..
            if row >= (self.tw_reserve.rowCount() -1): #마지막 ROW일때 계속 마지막 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
               row -= 1
            self.tw_reserve.setCurrentCell(row + 1, 0) #한 ROW 밑으로 이동
            self.sch_ilja = self.tw_reserve.item(self.tw_reserve.currentRow(), 0).text()  #해당일자를 읽는다.
            self.sch_reserve_name = self.tw_reserve.item(self.tw_reserve.currentRow(), 4).text()  # 예약자을 읽는다.
            self.sch_room_type = self.tw_reserve.item(self.tw_reserve.currentRow(), 3).text()  # 호실 타입을 읽는다.
            self.sch_start_ilja = self.tw_reserve.item(self.tw_reserve.currentRow(), 9).text()  # 일자를 읽는다.
            self.reserve_clear()
            self.search_rtn()#해당 일자의 정보를 화면에 보여준다.

    # 클릭시 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
    def mouse_click_rtn(self):
        row = self.tw_reserve.currentRow() #현재 ROW 값을 가져오려면..
        self.tw_reserve.setCurrentCell(row, 0)  # ROW 이동
        self.sch_ilja = self.tw_reserve.item(self.tw_reserve.currentRow(), 0).text()  #해당일자를 읽는다.
        self.sch_reserve_name = self.tw_reserve.item(self.tw_reserve.currentRow(), 4).text()  # 예약자을 읽는다.
        self.sch_room_type = self.tw_reserve.item(self.tw_reserve.currentRow(), 3).text()  # 호실 타입을 읽는다.
        self.sch_start_ilja = self.tw_reserve.item(self.tw_reserve.currentRow(), 9).text()  # 입실일자를 읽는다.
        self.sch_end_ilja = self.tw_reserve.item(self.tw_reserve.currentRow(), 10).text()  # 입실일자를 읽는다.
        self.reserve_clear()
        self.search_rtn()#해당 일자의 정보를 화면에 보여준다.

    #해당일자 호실에 대한 정보를 상단 입력란에 뿌려주려면.....
    def search_rtn(self):
        self.chk_cancel_sum_po = 'y'#환불금액으로 화면에 보일때 백만원이상 입력시 메시지가 안나오게하려면...
        #일자별 호실 정보 가져오기
        mra = mariadb_conn().conn
        # csr = mra.cursor(dictionary=True) #딕셔너리 형태로 표현하기 위해....
        csr = mra.cursor() #딕셔너리 형태로 표현하기 위해....
        query_sel = ("SELECT DATE_FORMAT(A.KEY_ILJA, '%Y-%m-%d %H:%i:%s') AS KEY_ILJA,A.ROOM_ILJA,A.ROOM_NAME,"
                     "A.RESERVE_NAME,decode_oracle(A.RESERVE_SITE,'','',FN_APPCOMP_NAME(A.RESERVE_SITE)) AS RESERVE_SITE, "
                     " A.RESERVE_ILJA,A.RESERVE_NUMBER,A.RESERVE_START_ILJA,A.RESERVE_END_ILJA, "
                    "decode_oracle(A.PAYMENT,'','',FN_CODE_NAME('PAY',A.PAYMENT)) AS PAYMENT,FORMAT(A.PAY_SUM,0) AS PAY_SUM, " 
                    "FORMAT(A.EXPEC_SUM, 0) AS EXPEC_SUM, A.WORKER, A.BIGO,"
                     "DECODE_ORACLE(A.DORMITORY_SEX,'g','여자','m','남자','') AS DORMITORY_SEX,A.DORMITORY_CLOSE, "
                    "decode_oracle(B.ADD_PAYMENT,'', '',FN_CODE_NAME('CPY',B.ADD_PAYMENT)) AS ADD_PAYMENT,FORMAT(B.ADD_SUM,0) AS ADD_SUM,B.ADD_BIGO,"
                     "A.SPECIAL_NOTE "
                    " FROM yeogak_reserve2025_tbl a left outer join yeogak_addpayment2025_tbl b "
                    " USING(comp_code,key_ilja,room_ilja) "
                    " WHERE a.comp_code = '"+self.comp_code+"' AND "
                    "a.room_ilja = '"+self.sch_ilja+"' AND "
                    "a.reserve_name ='"+self.sch_reserve_name+"' AND a.cancel_chk ='0' ")
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()

        cnt_chk = len(rows)
        self.find_row = ''
        # print(cnt_chk)
        # 월별이든 기간별이든 다른 컴퓨터든 변경사항이 있으면 새롭게 읽어오려면.........
        if cnt_chk != 0 :
            self.if_reserve_start_ilja = rows[0][7]
            if self.if_reserve_start_ilja != self.sch_start_ilja:
                self.find_row = 'chk'#새로운
        else:
            if  self.sch_start_ilja is None or self.sch_start_ilja =='':
                pass
            else:
                self.find_row = 'chk'#새로운

        if self.find_row == 'chk':

            self.first_sch()
        else:
            key_ilja = rows[0][0]
            room_ilja = rows[0][1]
            room_name = rows[0][2]
            reserve_name = rows[0][3]
            reserve_site = rows[0][4]
            reserve_ilja = rows[0][5]
            reserve_number = rows[0][6]
            reserve_start_ilja = rows[0][7]
            # print(reserve_start_ilja)
            reserve_end_ilja = rows[0][8]
            payment = rows[0][9]
            # print(type(payment))
            pay_sum = rows[0][10]
            expec_sum = rows[0][11]#예상 금액
            worker = rows[0][12]
            bigo = rows[0][13]#
            dormitory_sex = rows[0][14]
            dormitory_close = rows[0][15]
            add_payment = rows[0][16]
            add_sum = rows[0][17]
            add_bigo = rows[0][18]
            self.if_special_note = rows[0][19]

            self.ed_name.setText(reserve_name)  # 예약자
            self.ed_reserve_site.setText(reserve_site) #싸이트
            self.ed_reserve_ilja.setText(reserve_ilja)
            self.ed_reserve_number.setText(reserve_number)  # 예약번호
            self.ed_room_name.setText(room_name) #호실 다시 가져오기
            self.ed_room_type.setText(self.sch_room_type) #호실 타입 가져오기
            self.ed_start_ilja.setText(reserve_start_ilja)#현재 클릭한 일자
            self.ed_select_ilja.setText(self.sch_ilja)#현재 클릭한 일자  선택일자
            self.ed_special_note.setText(self.if_special_note)#현재 클릭한 일자  선택일자
            self.ed_end_ilja.setText(reserve_end_ilja)#퇴실일자
            if payment !='':
                self.ed_payment.setText(payment) #결재수단 정보 다시 가져오기
            if pay_sum is None or pay_sum == 0  or pay_sum == '0':
                pass
            else:
                self.ed_sum.setText(str(pay_sum))  # 결재 금액
            if expec_sum is None or expec_sum == 0  or expec_sum == '0':
                pass
            else:
                self.ed_expec_sum.setText(str(expec_sum))  # 예상 금액

            self.ed_sex.setText(dormitory_sex)  # 여자, 남자를 매칭한다.

            if dormitory_close == 'c': #마감 처리가 있다면
                self.cb_close.setChecked(True)  # 체크 시에...
            else:
                self.cb_close.setChecked(False)  # 체크 시에...

            self.ed_worker.setText(worker)  # 당일 근무자
            self.ed_bigo.setText(bigo)  # 예약자
            # self.de_reserve_ilja.setDate(self.sch_ilja)
            # print(add_sum)
            # 추가 결재 정보가 있으면 가져오기...
            if add_sum is None:
                pass
                # print('967')
            else:
                # print('969')
                self.ed_addsum.setText(str(add_sum))  # 추가 금액
                self.ed_addbigo.setText(add_bigo)  # 추가결재 비고
                self.ed_addpayment.setText(add_payment) # 추가 결재수단 정보 다시 가져오기



            #203-1 '-' 있는지를 체크하여 활성화 및 비활성화하려면...
            if self.sch_room_name.find(self.str_) != -1:
                self.cb_close.setVisible(True)# 마감 체크 보여주려면
                self.cb_close.setEnabled(False)  # 마감 체크를 활성화한다...
                self.lb_sex.setVisible(True)#남/여 호실 구분 보여주려면
                self.ed_sex.setVisible(True)# 남/여 호실 보여주려면
                self.ed_sex.setEnabled(True)  # 남/여 호실을 활성화한다...
            else:
                self.cb_close.setVisible(False)# 마감 체크 보여주려면
                self.lb_sex.setVisible(False)#남/여 호실 구분 보여주려면
                self.ed_sex.setVisible(False)# 남/여 호실 보여주려면

            #기준일 메시지
            # self.lb_msg.setText("현재 "+self.sch_ilja+"일 기준 일자입니다.")

            #예약 취소 현황에 내용 보여주기
            self.ed_cancel_start_ilja.setText(self.sch_ilja)#예약 현재일을 가져와 취소 시작일자로 한다. 10박중 5박만 취소하는 경우....
            self.ed_cancel_end_ilja.setText(reserve_end_ilja)#퇴실일자는 그래로 가져와 마지막을 표시한다.


            #입력 모드 를 확인하기 위해 지난 날은 보기만 한다.self.yesterday_chk
            # if self.now_date > room_ilja or self.now_date >= reserve_end_ilja: #오늘 일자가 퇴실일자와 같거나 클 경우 모든것을 입력하지 못하도록 disabled한다.
            if self.yesterday_chk > room_ilja or self.yesterday_chk >= reserve_end_ilja: #노부킹에 따라 어제 일자 까지 처리하기 위해......
                self.edit_disabled() #일자가 지난 경우 수정을 못하게하려면.....
            else:
                self.edit_enabled() # 입력 모드로 전환

    def edit_enabled(self): #예약 취소 현황을 저장하려면하려면...
        self.pb_save.setEnabled(True) # 저장 버튼을 Disabled
        # print('all')
        # 입실일자 당일 또는 입실일자 되기 전 전체 또는 부분 저장시
        self.cb_cancel_payment.setEnabled(True) # 환불 수단
        self.ed_cancel_sum.setEnabled(True) #환불금액
        self.ed_cancel_bigo.setEnabled(True)  # 취소 사유

        # self.cb_cancel_payment.setStyleSheet("background-color:rgba(240, 240, 240, 255);")#환불수단 disable
        self.cb_cancel_payment.setStyleSheet("background-color: rgba(255, 255, 255, 255);")#환불수단 enable

    def edit_disabled(self):#일자가 지난 경우 취소를 못하게하려면.....
        self.pb_save.setDisabled(True) # 저장 버튼을 Disabled
        # print('clr')
        self.cb_cancel_payment.setDisabled(True) # 환불 수단
        self.ed_cancel_sum.setDisabled(True) #환불금액
        self.ed_cancel_bigo.setDisabled(True)  # 취소 사유

        self.cb_cancel_payment.setStyleSheet("background-color:rgba(240, 240, 240, 255);")#환불수단 disable
        # self.cb_cancel_payment.setStyleSheet("background-color: rgba(255, 255, 255, 255);")#환불수단 enable

        #예약 취소 일자를 보여주지 안으려면.....
        self.ed_cancel_start_ilja.setText("")#예약 현재일을 가져와 취소 시작일자로 한다. 10박중 5박만 취소하는 경우....
        self.ed_cancel_end_ilja.setText("")#퇴실일자는 그래로 가져와 마지막을 표시한다.

    #자료를 가져와 화면에 뿌려준다.
    def first_sch(self):
        self.reserve_clear()

        start_ilja_sch = self.de_start_ilja_sch.date().toString('yyyy-MM-dd')#입실일자
        end_ilja_sch = self.de_end_ilja_sch.date().toString('yyyy-MM-dd')#퇴실일자

        #일자별 호실 정보 가져오기 60일 치
        mra = mariadb_conn().conn
        csr = mra.cursor(dictionary=True) #딕셔너리 형태로 표현하기 위해....
        query_sel = ("SELECT DATE_FORMAT(a.room_ilja,'%Y-%m-%d') as ILJA, "
                    "(select WK from yeogak_reserve_day_tbl where ilja = a.room_ilja) AS WK,a.room_name AS RN, " 
                    "(SELECT room_type from yeogak_room_name_info_tbl where comp_code = a.comp_code and room_name = a.room_name) AS ROOM_TYPE, "  
                    "A.RESERVE_NAME,decode_oracle(A.RESERVE_SITE,'','',FN_APPCOMP_NAME(A.RESERVE_SITE)) AS SITE_NAME, "
                    "A.RESERVE_ILJA,A.RESERVE_NUMBER,A.RESERVE_START_ILJA,A.RESERVE_END_ILJA, "
                    "decode_oracle(a.payment,'','',FN_CODE_NAME('PAY',a.payment)) AS PAYMENT_NAME, " 
                    "FORMAT(A.PAY_SUM,0) AS PAY_SUM,A.SPECIAL_NOTE,FORMAT(A.EXPEC_SUM,0) AS EXPEC_SUM, "
                    "DECODE_ORACLE(A.DORMITORY_SEX,'g','여자','m','남자','') AS DORMITORY_SEX,DECODE_ORACLE(A.DORMITORY_CLOSE,'c','Yes','') AS DORMITORY_CLOSE,A.WORKER,A.BIGO, "  
                    "(SELECT decode_oracle(add_payment,'', '',FN_CODE_NAME('PAY',add_payment)) from yeogak_addpayment2025_tbl WHERE comp_code = a.comp_code AND key_ilja = a.key_ilja AND room_ilja =a.room_ilja) AS ADD_PAYMENT, "  
                    "(SELECT decode_oracle(add_sum, NULL, '',FORMAT(add_sum,0)) from yeogak_addpayment2025_tbl WHERE comp_code = a.comp_code AND key_ilja = a.key_ilja AND room_ilja =a.room_ilja) AS ADD_SUM, " 
                    "(SELECT decode_oracle(add_bigo, NULL, '',add_bigo) from yeogak_addpayment2025_tbl WHERE comp_code = a.comp_code AND key_ilja = a.key_ilja AND room_ilja = a.room_ilja) AS ADD_BIGO, "  
                    "datediff(date_format(a.reserve_end_ilja, '%Y-%m-%d'),date_format(a.reserve_start_ilja, '%Y-%m-%d')) AS DATE_CHA "
                    "FROM yeogak_reserve2025_tbl a "
                    "where a.comp_code =  '"+self.comp_code+"' AND a.room_ilja BETWEEN '"+start_ilja_sch+"' AND '"+end_ilja_sch+"' AND a.cancel_chk = '0' "
                    "ORDER BY a.room_ilja,a.reserve_name")
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        item_cnt = len(rows)
        self.tw_reserve.setRowCount(item_cnt)
        style = "::section {""background-color: lightblue; }"
        self.tw_reserve.horizontalHeader().setStyleSheet(style)

        self.tw_reserve.resizeRowsToContents()
        # self.tw_reserve.setShowGrid(False)

        #호실 정보 보여주기
        for idx, col in enumerate(rows):
            # self.tw_reserve.item(0, 0).setBackground(QBrush(Qt.red))

            self.tw_reserve.setItem(idx, 0, QTableWidgetItem(col["ILJA"]))#일자
            self.tw_reserve.setItem(idx, 1, QTableWidgetItem(col["WK"]))#요일
            self.tw_reserve.item(idx, 1).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            if col["WK"] == '일':
                self.tw_reserve.item(idx, 0).setForeground(QBrush(Qt.red))
                self.tw_reserve.item(idx, 1).setForeground(QBrush(Qt.red))
                self.tw_reserve.item(idx, 0).setFont(QFont("Arial", 12, QFont.Bold, italic=False))  # 글자 폰트 설정.
                self.tw_reserve.item(idx, 1).setFont(QFont("Arial", 12, QFont.Bold, italic=False))  # 글자 폰트 설정.
            elif col["WK"] == '토':
                self.tw_reserve.item(idx, 0).setForeground(QBrush(Qt.blue))
                self.tw_reserve.item(idx, 1).setForeground(QBrush(Qt.blue))
                self.tw_reserve.item(idx, 0).setFont(QFont("Arial", 12, QFont.Bold, italic=False))  # 글자 폰트 설정.
                self.tw_reserve.item(idx, 1).setFont(QFont("Arial", 12, QFont.Bold, italic=False))  # 글자 폰트 설정.
            else:
                self.tw_reserve.item(idx, 0).setForeground(QBrush(Qt.black))
                self.tw_reserve.item(idx, 1).setForeground(QBrush(Qt.black))
            self.tw_reserve.setItem(idx, 2, QTableWidgetItem(col["RN"]))#호실
            self.tw_reserve.item(idx, 2).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tw_reserve.setItem(idx, 3, QTableWidgetItem(col["ROOM_TYPE"]))#객실타입
            self.tw_reserve.item(idx, 3).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tw_reserve.setItem(idx, 4, QTableWidgetItem(col["RESERVE_NAME"]))#예약자
            self.tw_reserve.setItem(idx, 5, QTableWidgetItem(col["SITE_NAME"]))#예약사이트
            self.tw_reserve.setItem(idx, 6, QTableWidgetItem(col["RESERVE_ILJA"]))#예약일자
            self.tw_reserve.setItem(idx, 7, QTableWidgetItem(col["RESERVE_NUMBER"]))#예약번호
            if col["EXPEC_SUM"] is None or col["EXPEC_SUM"] == '0' or col["EXPEC_SUM"] == 0:
                self.tw_reserve.setItem(idx, 8, QTableWidgetItem(''))  # 결재금액
            else:
                self.tw_reserve.setItem(idx, 8, QTableWidgetItem(str(col["EXPEC_SUM"])+'원'))#결재금액
            self.tw_reserve.item(idx, 8).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tw_reserve.setItem(idx, 9, QTableWidgetItem(col["RESERVE_START_ILJA"]))#입실일자
            self.tw_reserve.setItem(idx, 10, QTableWidgetItem(col["RESERVE_END_ILJA"]))#퇴실일자
            self.tw_reserve.setItem(idx, 11, QTableWidgetItem(col["PAYMENT_NAME"]))#결재수단
            # if col["PAY_SUM"] is None or col["PAY_SUM"] == '0' or col["PAY_SUM"] == 0:
            #     self.tw_reserve.setItem(idx, 12, QTableWidgetItem(''))  # 결재금액
            # else:
            #     self.tw_reserve.setItem(idx, 12, QTableWidgetItem(str(col["PAY_SUM"])+'원'))#결재금액
            # self.tw_reserve.item(idx, 12).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.tw_reserve.setItem(idx, 13, QTableWidgetItem(col["SPECIAL_NOTE"]))#특이사항
            self.tw_reserve.setItem(idx, 14, QTableWidgetItem(col["WORKER"]))#근무자
            self.tw_reserve.setItem(idx, 15, QTableWidgetItem(col["BIGO"]))#참고사항
            # self.tw_reserve.setItem(idx, 16, QTableWidgetItem(col["ADD_PAYMENT"]))#추가결재수단
            # self.tw_reserve.setItem(idx, 17, QTableWidgetItem(''))  # 추가결재금액  아래에 정의 되어 있음
            # self.tw_reserve.setItem(idx, 18, QTableWidgetItem('')) # 추가참고사항 아래(밑)에 정의 되어 있음

           # #203-1 '-' 있는지를 체크하여 활성화 및 비활성화하려면...
           #  if col["RN"].find(self.str_) != -1:
           #      self.tw_reserve.setItem(idx, 19, QTableWidgetItem(col["DORMITORY_SEX"]))  # 도미토리 성별
           #      self.tw_reserve.setItem(idx, 20, QTableWidgetItem(col["DORMITORY_CLOSE"]))  # 도미토리 마감 여부
           #      self.tw_reserve.item(idx, 19).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
           #      self.tw_reserve.item(idx, 20).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
           #  else:
           #      self.tw_reserve.setItem(idx, 19, QTableWidgetItem(''))  # 도미토리 성별
           #      self.tw_reserve.setItem(idx, 20, QTableWidgetItem(''))  # 도미토리 마감 여부

            if col["RESERVE_START_ILJA"] is None:
                self.tw_reserve.item(idx, 0).setBackground(QBrush(QColor(255, 255, 255)))
                self.tw_reserve.item(idx, 1).setBackground(QBrush(QColor(255, 255, 255)))
                self.tw_reserve.item(idx, 2).setBackground(QBrush(QColor(255, 255, 255)))
                self.tw_reserve.item(idx, 3).setBackground(QBrush(QColor(255, 255, 255)))
                self.tw_reserve.item(idx, 4).setBackground(QBrush(QColor(255, 255, 255)))
                self.tw_reserve.item(idx, 5).setBackground(QBrush(QColor(255, 255, 255)))
                self.tw_reserve.item(idx, 6).setBackground(QBrush(QColor(255, 255, 255)))
                self.tw_reserve.item(idx, 7).setBackground(QBrush(QColor(255, 255, 255)))
                self.tw_reserve.item(idx, 8).setBackground(QBrush(QColor(255, 255, 255)))
                self.tw_reserve.item(idx, 9).setBackground(QBrush(QColor(255, 255, 255)))
                self.tw_reserve.item(idx, 10).setBackground(QBrush(QColor(255, 255, 255)))
                self.tw_reserve.item(idx, 11).setBackground(QBrush(QColor(255, 255, 255)))
                # self.tw_reserve.item(idx, 12).setBackground(QBrush(QColor(255, 255, 255)))
                self.tw_reserve.item(idx, 13).setBackground(QBrush(QColor(255, 255, 255)))
                self.tw_reserve.item(idx, 14).setBackground(QBrush(QColor(255, 255, 255)))
                self.tw_reserve.item(idx, 15).setBackground(QBrush(QColor(255, 255, 255)))
                # self.tw_reserve.item(idx, 15).setBackground(QBrush(QColor(255, 255, 255)))
                # self.tw_reserve.item(idx, 16).setBackground(QBrush(QColor(255, 255, 255)))
                # self.tw_reserve.item(idx, 17).setBackground(QBrush(QColor(255, 255, 255)))
                # self.tw_reserve.item(idx, 18).setBackground(QBrush(QColor(255, 255, 255)))
                # self.tw_reserve.item(idx, 19).setBackground(QBrush(QColor(255, 255, 255)))
                # self.tw_reserve.item(idx, 20).setBackground(QBrush(QColor(255, 255, 255)))
            else:#입실일자가 있는 즉 숙박이 예약된 경우.....1박 노란색 연박 연두색....
                if col["DATE_CHA"] ==1 : #숙박 하루이면 노란색으로
                    self.tw_reserve.item(idx, 0).setBackground(QBrush(QColor(255, 255, 0)))
                    self.tw_reserve.item(idx, 1).setBackground(QBrush(QColor(255, 255, 0)))
                    self.tw_reserve.item(idx, 2).setBackground(QBrush(QColor(255, 255, 0)))
                    self.tw_reserve.item(idx, 3).setBackground(QBrush(QColor(255, 255, 0)))
                    self.tw_reserve.item(idx, 4).setBackground(QBrush(QColor(255, 255, 0)))
                    self.tw_reserve.item(idx, 5).setBackground(QBrush(QColor(255, 255, 0)))
                    self.tw_reserve.item(idx, 6).setBackground(QBrush(QColor(255, 255, 0)))
                    self.tw_reserve.item(idx, 7).setBackground(QBrush(QColor(255, 255, 0)))
                    self.tw_reserve.item(idx, 8).setBackground(QBrush(QColor(255, 255, 0)))
                    self.tw_reserve.item(idx, 9).setBackground(QBrush(QColor(255, 255, 0)))
                    self.tw_reserve.item(idx, 10).setBackground(QBrush(QColor(255, 255, 0)))
                    self.tw_reserve.item(idx, 11).setBackground(QBrush(QColor(255, 255, 0)))
                    # self.tw_reserve.item(idx, 12).setBackground(QBrush(QColor(255, 255, 0)))
                    self.tw_reserve.item(idx, 13).setBackground(QBrush(QColor(255, 255, 0)))
                    self.tw_reserve.item(idx, 14).setBackground(QBrush(QColor(255, 255, 0)))
                    self.tw_reserve.item(idx, 15).setBackground(QBrush(QColor(255, 255, 0)))
                    # self.tw_reserve.item(idx, 15).setBackground(QBrush(QColor(255, 255, 0)))
                    # self.tw_reserve.item(idx, 16).setBackground(QBrush(QColor(255, 255, 0)))
                    # self.tw_reserve.item(idx, 17).setBackground(QBrush(QColor(255, 255, 0)))
                    # self.tw_reserve.item(idx, 18).setBackground(QBrush(QColor(255, 255, 0)))
                    # self.tw_reserve.item(idx, 19).setBackground(QBrush(QColor(255, 255, 0)))
                    # self.tw_reserve.item(idx, 20).setBackground(QBrush(QColor(255, 255, 0)))

                else: #연박이면 연두색으로 표현
                    self.tw_reserve.item(idx, 0).setBackground(QBrush(QColor(179, 255, 175)))
                    self.tw_reserve.item(idx, 1).setBackground(QBrush(QColor(179, 255, 175)))
                    self.tw_reserve.item(idx, 2).setBackground(QBrush(QColor(179, 255, 175)))
                    self.tw_reserve.item(idx, 3).setBackground(QBrush(QColor(179, 255, 175)))
                    self.tw_reserve.item(idx, 4).setBackground(QBrush(QColor(179, 255, 175)))
                    self.tw_reserve.item(idx, 5).setBackground(QBrush(QColor(179, 255, 175)))
                    self.tw_reserve.item(idx, 6).setBackground(QBrush(QColor(179, 255, 175)))
                    self.tw_reserve.item(idx, 7).setBackground(QBrush(QColor(179, 255, 175)))
                    self.tw_reserve.item(idx, 8).setBackground(QBrush(QColor(179, 255, 175)))
                    self.tw_reserve.item(idx, 9).setBackground(QBrush(QColor(179, 255, 175)))
                    self.tw_reserve.item(idx, 10).setBackground(QBrush(QColor(179, 255, 175)))
                    self.tw_reserve.item(idx, 11).setBackground(QBrush(QColor(179, 255, 175)))
                    # self.tw_reserve.item(idx, 12).setBackground(QBrush(QColor(179, 255, 175)))
                    self.tw_reserve.item(idx, 13).setBackground(QBrush(QColor(179, 255, 175)))
                    self.tw_reserve.item(idx, 14).setBackground(QBrush(QColor(179, 255, 175)))
                    self.tw_reserve.item(idx, 15).setBackground(QBrush(QColor(179, 255, 175)))
                    # self.tw_reserve.item(idx, 15).setBackground(QBrush(QColor(179, 255, 175)))
                    # self.tw_reserve.item(idx, 16).setBackground(QBrush(QColor(179, 255, 175)))
                    # self.tw_reserve.item(idx, 17).setBackground(QBrush(QColor(179, 255, 175)))
                    # self.tw_reserve.item(idx, 18).setBackground(QBrush(QColor(179, 255, 175)))
                    # self.tw_reserve.item(idx, 19).setBackground(QBrush(QColor(179, 255, 175)))
                    # self.tw_reserve.item(idx, 20).setBackground(QBrush(QColor(179, 255, 175)))

            if col["PAY_SUM"] is None or col["PAY_SUM"] == '0' or col["PAY_SUM"] == 0:
                self.tw_reserve.setItem(idx, 12, QTableWidgetItem(''))  # 결재금액
                if col["RESERVE_START_ILJA"] is None:
                    self.tw_reserve.item(idx, 12).setBackground(QBrush(QColor(255, 255, 255)))
                else:
                    if col["DATE_CHA"] ==1 : #숙박 하루이면 노란색으로
                         self.tw_reserve.item(idx, 12).setBackground(QBrush(QColor(255, 255, 0)))
                    else:  # 연박이면 연두색으로 표현
                         self.tw_reserve.item(idx, 12).setBackground(QBrush(QColor(179, 255, 175)))
            else:
                self.tw_reserve.setItem(idx, 12, QTableWidgetItem(str(col["PAY_SUM"])+'원'))#결재금액
                self.tw_reserve.item(idx, 12).setBackground(QBrush(QColor(255,0, 0)))
            self.tw_reserve.item(idx, 12).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # if col["ADD_SUM"] is None or col["ADD_SUM"] == '0' or col["ADD_SUM"] == 0: #추가 결재 금액
            #     self.tw_reserve.setItem(idx, 17, QTableWidgetItem(''))  #추가결재금액
            #     self.tw_reserve.item(idx, 16).setBackground(QBrush(QColor(255, 255, 0)))
            #     self.tw_reserve.item(idx, 17).setBackground(QBrush(QColor(255, 255, 0)))
            #     self.tw_reserve.item(idx, 18).setBackground(QBrush(QColor(255, 255, 0)))
            #     if col["RESERVE_START_ILJA"] is None:
            #         self.tw_reserve.item(idx, 16).setBackground(QBrush(QColor(255, 255, 255)))
            #         self.tw_reserve.item(idx, 17).setBackground(QBrush(QColor(255, 255, 255)))
            #         self.tw_reserve.item(idx, 18).setBackground(QBrush(QColor(255, 255, 255)))
            #     else:
            #         if col["DATE_CHA"] ==1 : #숙박 하루이면 노란색으로
            #              self.tw_reserve.item(idx, 16).setBackground(QBrush(QColor(255, 255, 0)))
            #              self.tw_reserve.item(idx, 17).setBackground(QBrush(QColor(255, 255, 0)))
            #              self.tw_reserve.item(idx, 18).setBackground(QBrush(QColor(255, 255, 0)))
            #         else:  # 연박이면 연두색으로 표현
            #              self.tw_reserve.item(idx, 16).setBackground(QBrush(QColor(179, 255, 175)))
            #              self.tw_reserve.item(idx, 17).setBackground(QBrush(QColor(179, 255, 175)))
            #              self.tw_reserve.item(idx, 18).setBackground(QBrush(QColor(179, 255, 175)))
            # else:
            #     self.tw_reserve.setItem(idx, 17, QTableWidgetItem(str(col["ADD_SUM"])+'원'))#추가결재금액
            #     self.tw_reserve.setItem(idx, 18, QTableWidgetItem(col["ADD_BIGO"]))#추가참고사항
            #     self.tw_reserve.item(idx, 16).setBackground(QBrush(QColor(255, 170, 0)))
            #     self.tw_reserve.item(idx, 17).setBackground(QBrush(QColor(255, 170, 0)))
            #     self.tw_reserve.item(idx, 18).setBackground(QBrush(QColor(255, 170, 0)))

        self.tw_reserve.resizeColumnsToContents()#col 자릿수에 맡게 보여주려면...
        self.tw_reserve.verticalHeader().setVisible(False)  # row header 숨기기
        self.tw_reserve.setEditTriggers(QAbstractItemView.NoEditTriggers)#수정 불가하게
        self.tw_reserve.setSelectionBehavior(QAbstractItemView.SelectRows)#한줄씩 선택
        #self.tw_reserve.setCurrentCell(row_focus_cnt-1, 0)  # / ROW 위로 이동