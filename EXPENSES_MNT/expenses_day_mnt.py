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

from function.inlink import inlink_url

# class StockIndexWindow(QMainWindow, form_class):
class Expenses_day_mnt_Window(QMainWindow):
    def __init__(self,pf_os,comp_code,user_id):
        super().__init__()
        self.move(10, 50)
        self.setFixedSize(1729, 903)
        if pf_os == 'Windows':
            option_ui = 'UiDir/expenses_day_mnt.ui'
        else:
            option_ui = 'UiDir/expenses_day_mnt.ui'

        self.comp_code = comp_code
        self.user_id = user_id
        # option_ui = 'UiDir/StockCompInfo.ui'
        uic.loadUi(option_ui, self)

        regExp = QRegExp("[0-9]*") #edit에 숫자만 입력 처리하기 위해
        regExp_tel = QRegExp("[0-9--]*") #edit에 전화번호 처리하기 위해 010-2002-8978  숫자만 입력 처리하기 위해
        palette = QPalette()
        palette.setColor(QPalette.Highlight, QColor(144, 153, 234))  # default ==> Qt.darkBlue
        # palette.setColor(QPalette.HighlightedText, Qt.red)  # default ==> Qt.white
        self.tw_expenses.setPalette(palette)#tablewidget title정의

        self.ed_tel.setValidator(QRegExpValidator(regExp_tel, self))#전화번호
        self.ed_qty.setValidator(QRegExpValidator(regExp, self))#수량
        self.ed_price.setValidator(QRegExpValidator(regExp, self))#단가
        self.ed_sum.setValidator(QRegExpValidator(regExp, self))#금액
        self.chk_qty_po = '' #수량
        self.chk_price_po = '' #단가

        self.init_rtn()#오늘 일자를 먼저 보여주려면......
        self.pb_search.clicked.connect(self.select_rtn)  # 자료 조회
        self.pb_save.clicked.connect(self.expenes_dbsave)  # 자료 저장/수정
        self.pb_delete.clicked.connect(self.expenes_dbdelete)  # 검색(클릭)한 자료를 삭제 한다
        self.pb_clear.clicked.connect(self.expenes_clear)  # 저장 화면을 클리어
        self.ed_qty.textChanged.connect(self.qty_TextFunction)#수량이 변경 될때   수량x단가로 금액을 표현하기 위해
        self.ed_qty.returnPressed.connect(self.qty_TextFunction)#수량이 변경 될때   수량x단가로 금액을 표현하기 위해
        self.ed_price.textChanged.connect(self.price_TextFunction)  # 딘기가 변경 될때   수량x단가로 금액을 표현하기 위해
        self.ed_price.returnPressed.connect(self.price_TextFunction) # 딘기가 변경 될때   수량x단가로 금액을 표현하기 위해
        # self.ed_price.returnPressed.connect(self.price_TextFunction)# 눌렀을때...
        # self.tw_reserve.clicked.connect(self.reserve_display) # 클릭시 정보를 보여 주고 저장, 수정 , 삭제를 하려면...

        self.tw_expenses.clicked.connect(self.mouse_click_rtn) # 클릭시 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
        self.tw_expenses.keyPressEvent = self.keyPressEvent #UP, DOWN 키를 누를 때 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
        self.tb_internet.clicked.connect(self.internet_sch)#링크 주소 인터넷으로 연결하기
        self.first_sch()  # 첫 화면시 현재일자를 검색해온다.

    #오늘 일자를 먼저 보여주려면....
    def init_rtn(self):
        # 현재 일자를 검색
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_sel = """SELECT date_format(date_add(CURDATE(), INTERVAL -31 day),'%Y-%m-%d'),
                       date_format(date_add(CURDATE(), INTERVAL 2 day),'%Y-%m-%d'),
                       date_format(CURDATE(),'%Y-%m-%d')  from dual """
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        self.st_ilja_upno = rows[0][0]#현재일 보다 31일 전의 날짜이면 update를 못하게 한다면.....
        en_ilja = rows[0][1]
        self.now_date = rows[0][2]  # 현재일자를 가져고 검색 및 저장, 초기화에 활용한다.....

        self.de_start_ilja_sch.setDate(datetime.strptime(self.st_ilja_upno, '%Y-%m-%d'))  # 시작일자
        self.de_end_ilja_sch.setDate(datetime.strptime(en_ilja, '%Y-%m-%d'))  # 종료일자

        # 결재수단 정보 조회
        mra = mariadb_conn().conn
        csr = mra.cursor(dictionary=True) #딕셔너리 형태로 표현하기 위해....
        query_sel = "SELECT CODE_NAME FROM YEOGAK_CODE_TBL WHERE CODE_ID = 'PAY' ORDER BY CODE01"
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        self.cb_payment.insertItem(0,'')
        #결재수단 정보 조회
        for idx, col in enumerate(rows):
            self.cb_payment.insertItem(idx+1,col["CODE_NAME"])

        self.save_chk = 'all' #저장 모드로 한다면...

    #인터넷 링크 주소 연결하기
    def internet_sch(self):
        inlink_url(self.ed_inlink.text())#인트넷으로 연결하기
    def qty_TextFunction(self):#수량이 변경되면 금액이 변경되도록하려면....
        if self.chk_qty_po != 'y':#table에서 마우스 클릭 및 위,아래 키보드 눌러서 화면에 보일때는 통과하려면.....
            qty = self.ed_qty.text().replace(',', '')
            if qty is None or qty == '':
                self.ed_qty.setText('') #수량
                self.ed_sum.setText('') #금액
            else:
                if int(qty) > 1000:
                    reply = QMessageBox.question(self, 'Message', "입력하신 수량이 "+format(int(qty), ',')+" 맞습니까?",
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.Yes:  # 수량이 맞으면.....
                        self.chk_qty_po = 'y'
                        self.ed_qty.setText(format(int(qty), ','))
                        price = self.ed_price.text().replace(',', '')  # 단가
                        if price is None or price == '':
                            price = '0'
                        sum = int(qty) * int(price) # 수량*단가
                        self.ed_sum.setText(str(format(sum, ',')))
                        self.ed_qty.setFocus()
                    else:
                        self.chk_qty_po = 'y'
                        self.ed_qty.setText('') #수량
                        self.ed_sum.setText('') #금액
                        self.ed_qty.setFocus()
                else:
                    self.chk_qty_po = 'n'
                    price = self.ed_price.text().replace(',', '')  # 단가
                    if price is None or price == '':
                        price = '0'
                    sum = int(qty) * int(price) # 수량*단가
                    self.ed_sum.setText(str(format(sum, ',')))
        else:
            self.chk_qty_po = 'n'


        # if self.ed_qty.text() is None or self.ed_qty.text() == '' or self.ed_qty.text() == '0':  # 수량이 없으면..
        #    self.ed_sum.setText('0')  #금액
        # elif self.ed_price.text() is None or self.ed_price.text() == '' or self.ed_price.text() == '0':  # 단가
        #     self.ed_sum.setText('0')  # 금액
        # else:
        #     qty = int(self.ed_qty.text().replace(',', '')) # 수량
        #     price = int(self.ed_price.text().replace(',', ''))  # 단가
        #     sum = qty * price # 수량*단가
        #     self.ed_sum.setText(str(format(sum, ',')))

    def price_TextFunction(self): #단가가 변경되면 금액이 변경되도록하려면....
        if self.chk_price_po != 'y':#table에서 마우스 클릭 및 위,아래 키보드 눌러서 화면에 보일때는 통과하려면.....
            price = self.ed_price.text().replace(',', '')
            if price is None or price == '':
                self.ed_price.setText('') #수량
                self.ed_sum.setText('') #금액
            else:
                if int(price) > 1000000:
                    reply = QMessageBox.question(self, 'Message', "입력하신 금액 "+format(int(price), ',')+"원 맞습니까?",
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.Yes:  # 수량이 맞으면.....
                        self.chk_price_po = 'y'
                        self.ed_price.setText(format(int(price), ','))
                        qty = self.ed_qty.text().replace(',', '')  # 단가
                        if qty is None or qty == '':
                            qty = '0'
                        sum = int(qty) * int(price) # 수량*단가
                        self.ed_sum.setText(str(format(sum, ',')))
                        self.ed_price.setFocus()
                    else:
                        self.chk_price_po = 'y'
                        self.ed_price.setText('') #수량
                        self.ed_sum.setText('') #금액
                        self.ed_price.setFocus()
                else:
                    self.chk_price_po = 'n'
                    qty = self.ed_qty.text().replace(',', '')  # 단가
                    if qty is None or qty == '':
                        qty = '0'
                    sum = int(qty) * int(price) # 수량*단가
                    self.ed_sum.setText(str(format(sum, ',')))
        else:
            self.chk_price_po = 'n'




        # if self.ed_qty.text() is None or self.ed_qty.text() == '' or self.ed_qty.text() == '0':  # 수량이 없으면..
        #    self.ed_sum.setText('0')  #금액
        # elif self.ed_price.text() is None or self.ed_price.text() == '' or self.ed_price.text() == '0':  # 단가
        #     self.ed_sum.setText('0')  # 금액
        # else:
        #     qty = int(self.ed_qty.text().replace(',', '')) # 수량
        #     price = int(self.ed_price.text().replace(',', ''))  # 단가
        #     sum = qty * price # 수량*단가
        #     self.ed_sum.setText(str(format(sum, ',')))


    def select_rtn(self):
        if self.de_start_ilja_sch.date() > self.de_end_ilja_sch.date():
            QMessageBox.about(self, "정보", "일자를 정확히 입력하세요....")
            self.de_start_ilja_sch.setFocus()
        else:
            self.first_sch()

    # 자료 저장/수정
    def expenes_dbsave(self):
        if self.ed_name.text() is None or self.ed_name.text() =='': #품명
            QMessageBox.about(self, "정보", "품명을 입력하세요....")
            self.ed_name.setFocus()
        elif self.cb_payment.currentIndex() == 0:  # 결재 수단은 없고 결재 금액만 있을 경우.
            QMessageBox.about(self, "정보", "결재 수단을 선택하세요....")
            self.cb_payment.setFocus()
        elif self.ed_qty.text() is None or self.ed_qty.text() =='' or self.ed_qty.text() =='0': #수량
            QMessageBox.about(self, "정보", "수량을 입력하세요....")
            self.ed_qty.setFocus()
        elif self.ed_price.text() is None or self.ed_price.text() =='' or self.ed_price.text() =='0': #단가
            QMessageBox.about(self, "정보", "단가을 입력하세요....")
            self.ed_price.setFocus()
        else:
            if self.st_ilja_upno > self.de_ilja.date().toString('yyyy-MM-dd') :
                QMessageBox.about(self, "정보", "31일이 경과한 날짜를 선택하였습니다 날짜를 다시 입력하세요....")
                self.de_ilja.setFocus()
            else:#실제 저장 및 수정 부분....
                # print(self.save_chk)
                if self.save_chk == 'sal':  #수정 사항이 있으면 저장하겠는지 묻는다
                    if (self.if_exp_ilja != self.de_ilja.date().toString('yyyy-MM-dd') or
                        self.if_exp_name != self.ed_name.text() or  self.if_exp_payment != self.cb_payment.currentText()
                        or self.if_exp_qty != str(self.ed_qty)
                        or self.if_exp_price != str(self.ed_price.text()) or self.if_exp_po != self.ed_po.text()
                        or self.if_exp_tel != self.ed_tel.text() or self.if_exp_bigo != self.ed_bigo.text()
                        or self.if_exp_inlink != self.ed_inlink.text()) :

                            reply = QMessageBox.question(self, 'Message', '수정된 사항을 저장하시겠습니까?',
                                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                            if reply == QMessageBox.Yes:  # 입실일자와 퇴실일자의 기간중에서 겹치지만 그래도 저장을 하려면 아래에서 실행
                                self.dbdelete()
                                self.dbsave()
                                QMessageBox.about(self, "정보", "수정된 자료가 저장되었습니다.....")
                                self.first_sch()
                    else:
                        QMessageBox.about(self, "정보", "변경된 자료가 없습니다....")

                elif self.save_chk == 'all': #w지출 내역을 저장하려면..
                    reply = QMessageBox.question(self, 'Message', '자료를 저장하시겠습니까?',
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.Yes: #예약을 저장하려면
                        self.dbsave()#저장한다..
                        QMessageBox.about(self, "정보", "자료가 저장되었습니다.....")
                        self.first_sch()
                        self.ed_name.setFocus() #예약자로 포커스를 이동한다
                    else:
                        self.ed_sum.setFocus()

    def expenes_dbdelete(self):
        if self.if_key_ilja is None or self.if_key_ilja =='':
            QMessageBox.about(self, "정보", "삭제할 자료를 선택하세요.....")
        else:
            reply = QMessageBox.question(self, 'Message', '선택한 자료를 삭제하시겠습니까?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes: #예약을 저장하려면
                self.dbdelete()
                QMessageBox.about(self, "정보", "자료가 삭제되었습니다......")
                self.expenes_clear()
                self.first_sch()
            else:
                self.expenes_clear()
    # 자료를 삭세 한다.
    def dbdelete(self):
        # 클릭된 자료를 삭제한다.
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_sel = "delete from expenses_day_tbl " \
                    " WHERE comp_code='" + self.comp_code + "' AND key_ilja='" + self.if_key_ilja + "' " \
                    " AND exp_name='" + self.if_exp_name + "' "

        try:
            csr.execute(query_sel)
            mra.commit()
        except mariadb.Error as e:
            print(f"Error: {e}")

        csr.close()
        mra.close()


    # 전체(처음) 저장하려면...  또는 입실일자가 첫날인 경우(key값이 같은 경우 삭제 후 ) 자료를 저장하려면.....
    def dbsave(self):
        exp_ilja = self.de_ilja.date().toString('yyyy-MM-dd')#일자
        exp_name = self.ed_name.text()#품명
        exp_qty = self.ed_qty.text().replace(',', '')  # 수량
        exp_price = self.ed_price.text().replace(',', '')  # 단가
        exp_sum = self.ed_sum.text().replace(',', '')  # 금액
        exp_po = self.ed_po.text()#구입처
        exp_tel = self.ed_tel.text()#전화번호
        exp_bigo = self.ed_bigo.text()#비고
        exp_inlink = self.ed_inlink.text()#비고
        exp_payment = self.cb_payment.currentText()#결재수단
        if exp_payment is not None or exp_payment !='':
            #코드 값 가져오기
            mra = mariadb_conn().conn
            csr = mra.cursor()
            query_sel = "SELECT FN_CODE_CODE('PAY','"+exp_payment+"') "
            # print(query_sel)
            csr.execute(query_sel)
            rows = csr.fetchall()
            csr.close()
            mra.close()
            re_payment_code = rows[0][0] #결재수단 code값을 가져온다
        else:
            re_payment_code = ''#결재수단 code값을 가져온다

        # 현재 일자를 검색
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_sel = "SELECT now() from dual "
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        key_ilja = rows[0][0]
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_in01 = """insert into expenses_day_tbl (comp_code,key_ilja,exp_ilja,exp_name,exp_payment,exp_qty,
                        exp_price,exp_sum,exp_po,exp_tel,exp_inlink,exp_bigo,mnt_id)
                        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """
        t = (self.comp_code, key_ilja, exp_ilja, exp_name, re_payment_code,
             exp_qty,exp_price,exp_sum,exp_po,exp_tel,exp_inlink,exp_bigo,self.user_id)
        try:
            csr.execute(query_in01, t)
            mra.commit()
        except mariadb.Error as e:
            print(f"Error: {e}")
        csr.close()
        mra.close()

    # 클릭시 층수를 ed_floor_st edit에 보여준다....
    def expenes_clear(self):
        self.chk_qty_po ='n'#결재 금액으로 화면에 보일때 백만원이상 입력시 메시지가 안나오게하려면...
        self.chk_price_po ='n'#예상금액으로 화면에 보일때 백만원이상 입력시 메시지가 안나오게하려면...
        self.if_key_ilja = ''
        self.if_exp_ilja = ''
        self.if_exp_name = ''
        self.if_exp_payment = ''
        self.if_exp_qty = ''
        self.if_exp_price = ''
        self.if_exp_sum = ''
        self.if_exp_po = ''
        self.if_exp_tel = ''
        self.if_exp_bigo = ''
        self.if_exp_inlink = ''

        self.de_ilja.setDate(datetime.strptime(self.now_date, '%Y-%m-%d'))#일자를 현재일로 전환하려면.....
        self.ed_name.setText("")  # 품명
        self.cb_payment.setCurrentIndex(0) #결재수단 정보 다시 가져오기 위해 초기화
        self.ed_qty.setText("")  # 수량
        self.ed_price.setText("")  # 단가
        self.ed_sum.setText("")  # 금액
        self.ed_po.setText("")  # 결재 금액
        self.ed_tel.setText("")  # 당일 근무자
        self.ed_bigo.setText("")  # 예약자
        self.ed_inlink.setText("")  # 예약자

        self.edit_enabled()#입력 모드로 활성화 하려면..

    #KEY_UP, KEY_DOWN을 눌렀다면 .....
    def keyPressEvent (self, eventQKeyEvent):
        key = eventQKeyEvent.key()
        if key == Qt.Key_Up: #up 키를 누를 때마다  해당일자 호실의 정보를 상당 입력란에 보여주려면.....
            row = self.tw_expenses.currentRow() #현재 ROW 값을 가져오려면..
            if row == 0: # 처음 일때 값을 1로 하기 위해
                row += 1
            self.tw_expenses.setCurrentCell(row-1,0)  #한 ROW 위로 이동
            self.sch_ilja = self.tw_expenses.item(self.tw_expenses.currentRow(), 0).text()  #해당일자를 읽는다.
            self.sch_name = self.tw_expenses.item(self.tw_expenses.currentRow(), 2).text()  # 품명을 읽는다.
            self.sch_qty = self.tw_expenses.item(self.tw_expenses.currentRow(), 4).text().replace(',', '')  # 수량을 읽는다.
            self.sch_price = self.tw_expenses.item(self.tw_expenses.currentRow(), 5).text().replace(',', '')  # 단가를 읽는다..
            self.sch_po = self.tw_expenses.item(self.tw_expenses.currentRow(), 7).text()  # 구입처을 읽는다.
            if self.sch_name=='' or self.sch_name is None:
                self.expenes_clear()
                self.de_ilja.setDate(datetime.strptime(self.sch_ilja, '%Y-%m-%d') )  # 일자  같게한다.

                if self.st_ilja_upno > self.sch_ilja:#현재의 일자와 자료의 일자를 비교하여 31일전 과거일자이면 저장버튼을 disabled 하려면
                    self.save_chk = 'clr'  # 저장 할 수 없게 하려면...
                    self.edit_disabled()  # 일자가 지난 경우 수정을 못하게하려면.....
                else:
                    self.save_chk = 'all'#새로운 예약일 경우로 입력모드 전환
                    self.edit_enabled()  # 입력 모드로 전환
            else:
                self.expenes_clear()
                self.search_rtn()

        elif key == Qt.Key_Down:  # down 키를 누를 때마다  해당일자 호실의 정보를 상당 입력란에 보여주려면.....
            row = self.tw_expenses.currentRow() #현재 ROW 값을 가져오려면..
            if row >= (self.tw_expenses.rowCount() -1): #마지막 ROW일때 계속 마지막 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
               row -= 1
            self.tw_expenses.setCurrentCell(row + 1, 0) #한 ROW 밑으로 이동
            self.sch_ilja = self.tw_expenses.item(self.tw_expenses.currentRow(), 0).text()  #해당일자를 읽는다.
            self.sch_name = self.tw_expenses.item(self.tw_expenses.currentRow(), 2).text()  # 품명을 읽는다.
            self.sch_qty = self.tw_expenses.item(self.tw_expenses.currentRow(), 4).text().replace(',', '')  # 수량을 읽는다.
            self.sch_price = self.tw_expenses.item(self.tw_expenses.currentRow(), 5).text().replace(',', '')  # 단가를 읽는다..
            self.sch_po = self.tw_expenses.item(self.tw_expenses.currentRow(), 7).text()  # 구입처을 읽는다.
            if self.sch_name=='' or self.sch_name is None:
                self.expenes_clear()
                self.de_ilja.setDate(datetime.strptime(self.sch_ilja, '%Y-%m-%d') )  # 일자  같게한다.

                if self.st_ilja_upno > self.sch_ilja:#현재의 일자와 자료의 일자를 비교하여 31일전 과거일자이면 저장버튼을 disabled 하려면
                    self.save_chk = 'clr'  # 저장 할 수 없게 하려면...
                    self.edit_disabled()  # 일자가 지난 경우 수정을 못하게하려면.....
                else:
                    self.save_chk = 'all'#새로운 예약일 경우로 입력모드 전환
                    self.edit_enabled()  # 입력 모드로 전환
            else:
                self.expenes_clear()
                self.search_rtn()

    # 클릭시 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
    def mouse_click_rtn(self):
        row = self.tw_expenses.currentRow() #현재 ROW 값을 가져오려면..
        self.tw_expenses.setCurrentCell(row, 0)  # ROW 이동
        self.sch_ilja = self.tw_expenses.item(self.tw_expenses.currentRow(), 0).text()  #해당일자를 읽는다.
        self.sch_name = self.tw_expenses.item(self.tw_expenses.currentRow(), 2).text()  # 품명을 읽는다.
        self.sch_qty = self.tw_expenses.item(self.tw_expenses.currentRow(), 4).text().replace(',', '')  # 수량을 읽는다.
        self.sch_price = self.tw_expenses.item(self.tw_expenses.currentRow(), 5).text().replace(',', '')  # 단가를 읽는다..
        self.sch_po = self.tw_expenses.item(self.tw_expenses.currentRow(), 7).text()  # 구입처을 읽는다.
        if self.sch_name=='' or self.sch_name is None:
            self.expenes_clear()
            self.de_ilja.setDate(datetime.strptime(self.sch_ilja, '%Y-%m-%d') )  # 일자  같게한다.

            if self.st_ilja_upno > self.sch_ilja:#현재의 일자와 자료의 일자를 비교하여 31일전 과거일자이면 저장버튼을 disabled 하려면
                self.save_chk = 'clr'  # 저장 할 수 없게 하려면...
                self.edit_disabled()  # 일자가 지난 경우 수정을 못하게하려면.....
            else:
                self.save_chk = 'all'#새로운 예약일 경우로 입력모드 전환
                self.edit_enabled()  # 입력 모드로 전환
        else:
            self.expenes_clear()
            self.search_rtn()


    #해당일자 호실에 대한 정보를 상단 입력란에 뿌려주려면.....
    def search_rtn(self):
        self.chk_qty_po ='y'#결재 금액으로 화면에 보일때 백만원이상 입력시 메시지가 안나오게하려면...
        self.chk_price_po ='y'#예상금액으로 화면에 보일때 백만원이상 입력시 메시지가 안나오게하려면...
        #일자, 품명,수량,단가,구입처에 해당하는 정보를 가져오려면....
        # 한품목을 다른 집에서 구입한다면 일자,품명,수량,단가가 같은을 경우가 있다면, 있겠지 그럼 구입처가 다를 것이다..
        #그래서 검색을 일자, 품명,수량,단가,구입처까지 한다면..
        mra = mariadb_conn().conn
        # csr = mra.cursor(dictionary=True) #딕셔너리 형태로 표현하기 위해....
        csr = mra.cursor() #딕셔너리 형태로 표현하기 위해....
        query_sel = ("SELECT DATE_FORMAT(KEY_ILJA, '%Y-%m-%d %H:%i:%s') AS KEY_ILJA,EXP_ILJA,EXP_NAME,"
                     "decode_oracle(EXP_PAYMENT,'','',FN_CODE_NAME('PAY',EXP_PAYMENT)) AS EXP_PAYMENT,"
                     "FORMAT(EXP_QTY,0) AS EXP_QTY,FORMAT(EXP_PRICE,0) AS EXP_PRICE,FORMAT(EXP_SUM,0) AS EXP_SUM, "
                    "EXP_PO,EXP_TEL,EXP_INLINK,EXP_BIGO FROM expenses_day_tbl "
                    " WHERE comp_code = %s AND exp_ilja = %s AND "
                    "exp_name = %s AND exp_qty = %s AND "
                    "exp_price = %s AND exp_po = %s ")
        t=(self.comp_code,self.sch_ilja,self.sch_name,self.sch_qty,self.sch_price,self.sch_po)
        # print(query_sel,t)
        csr.execute(query_sel,t)
        rows = csr.fetchall()
        csr.close()
        mra.close()

        self.if_key_ilja = rows[0][0]
        self.if_exp_ilja = rows[0][1]
        self.if_exp_name = rows[0][2]
        self.if_exp_payment = rows[0][3]
        self.if_exp_qty = rows[0][4]
        self.if_exp_price = rows[0][5]
        self.if_exp_sum = rows[0][6]
        self.if_exp_po = rows[0][7]
        self.if_exp_tel = rows[0][8]
        self.if_exp_inlink = rows[0][9]
        self.if_exp_bigo = rows[0][10]


        self.de_ilja.setDate(datetime.strptime(self.if_exp_ilja, '%Y-%m-%d'))#일자
        self.ed_name.setText(self.if_exp_name)  # 품명
        if self.if_exp_payment !='':
            self.cb_payment.setCurrentText(self.if_exp_payment) #결재수단 정보 뿌려주기
        else:
            self.cb_payment.setCurrentText('') #결재수단 정보 없으면..

        self.ed_po.setText(self.if_exp_po) #구입처
        self.ed_tel.setText(self.if_exp_tel) #전화번호
        self.ed_inlink.setText(self.if_exp_inlink) #전화번호
        self.ed_bigo.setText(self.if_exp_bigo) #구입처
        if self.if_exp_qty is None or self.if_exp_qty == ''  or self.if_exp_qty == '0':
            pass
        else:
            self.ed_qty.setText(str(self.if_exp_qty))  # 수량

        if self.if_exp_price is None or self.if_exp_price == ''  or self.if_exp_price == '0':
            pass
        else:
            self.ed_price.setText(str(self.if_exp_price))  # 단가

        if self.if_exp_sum is None or self.if_exp_sum == 0  or self.if_exp_sum == '0':
            pass
        else:
            self.ed_sum.setText(str(self.if_exp_sum))  #금액

        #입실일자가 오늘이면 전체를 변경(수정)할 수 있게 한고...
        #입실일자가 지난 경우 즉 숙박을 하고 있는 경우는 근무자, 참고사항을 남기게하고, 추가 결재 쪽도 저장할 수 있게 하려면...
        #숙박일자가 지난 경우는 보여주기만 가능하게 한다.


        if self.if_key_ilja is None or self.if_key_ilja == '': #새롭게 저장할 수 있는 경우
            self.save_chk = 'all'
        else:
            if  self.st_ilja_upno > self.if_exp_ilja: #오늘 일자가 퇴실일자와 같거나 클 경우 모든것을 입력하지 못하도록 disabled한다.
                self.save_chk = 'clr'  # 저장 할 수 없게 하려면...
                self.edit_disabled() #일자가 지난 경우 수정을 못하게하려면.....
            else:
                self.save_chk = 'sal' # 전체를 수정하여 저장할 수 있는 경우 ...
                self.edit_enabled() # 입력 모드로 전환
    def edit_enabled(self): #전체를 수정 저장하려면...
        self.de_ilja.setEnabled(True) #일자
        self.ed_name.setEnabled(True)  # 품명
        self.cb_payment.setEnabled(True)  # 결재수단 정보 다시 가져오기
        self.ed_qty.setEnabled(True)  # 수량
        self.ed_price.setEnabled(True)  # 단가
        self.ed_sum.setDisabled(True)  # 금액
        self.ed_po.setEnabled(True) # 결재 금액
        self.ed_tel.setEnabled(True)  # 당일 근무자
        self.ed_bigo.setEnabled(True)  # 예약자
        self.ed_inlink.setEnabled(True)  # 인터넷연결

    def edit_disabled(self):#일자가 지난 경우 수정을 못하게하려면.....
        # print('clr')
        self.de_ilja.setDisabled(True) #일자
        self.ed_name.setDisabled(True)  # 품명
        self.cb_payment.setDisabled(True)  # 결재수단 정보 다시 가져오기
        self.ed_qty.setDisabled(True)  # 수량
        self.ed_price.setDisabled(True)  # 단가
        self.ed_sum.setDisabled(True)  # 금액
        self.ed_po.setDisabled(True) # 결재 금액
        self.ed_tel.setDisabled(True)  # 당일 근무자
        self.ed_bigo.setDisabled(True)  # 예약자
        self.ed_inlink.setDisabled(True)  # 인터넷연결

    #자료를 가져와 화면에 뿌려준다.
    def first_sch(self):
        self.expenes_clear()

        start_ilja_sch = self.de_start_ilja_sch.date().toString('yyyy-MM-dd')#시작일자
        end_ilja_sch = self.de_end_ilja_sch.date().toString('yyyy-MM-dd')#종료일자
        self.lb_msg.setText('')
        #기간 동안 총 지출 합계를 계산하려면.....
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_sel = "SELECT DECODE_ORACLE(SUM(EXP_SUM), NULL,0,FORMAT(SUM(EXP_SUM),0)) AS TOT_SUM FROM expenses_day_tbl "\
                    "WHERE comp_code = '"+self.comp_code+"' AND exp_ilja BETWEEN '"+start_ilja_sch+"' AND '"+end_ilja_sch+"' "
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        self.lb_msg.setText('기간 '+start_ilja_sch+' ~ '+end_ilja_sch+'일 까지  총 지출 합계  '+str(rows[0][0])+' 원 입니다.')

        #일자별 호실 정보 가져오기 60일 치
        mra = mariadb_conn().conn
        csr = mra.cursor(dictionary=True) #딕셔너리 형태로 표현하기 위해....
        query_sel = ("SELECT DATE_FORMAT(A.ILJA,'%Y-%m-%d') as ILJA,A.WK,B.EXP_ILJA,B.EXP_NAME,"
                    "decode_oracle(b.exp_payment,'','',FN_CODE_NAME('PAY',b.exp_payment)) AS PAYMENT_NAME, "
                    "FORMAT(B.EXP_QTY,0) AS EXP_QTY,FORMAT(B.EXP_PRICE,0) AS EXP_PRICE,FORMAT(B.EXP_SUM,0) AS EXP_SUM, "
                    "B.EXP_PO,EXP_TEL,B.EXP_BIGO,B.KEY_ILJA,B.EXP_INLINK "
                    "FROM (SELECT ilja,WK  FROM yeogak_reserve_day_tbl "
                    "WHERE ilja BETWEEN '"+start_ilja_sch+"' AND '"+end_ilja_sch+"') a "
                    "LEFT OUTER JOIN expenses_day_tbl b " 
                    "ON b.comp_code = '"+self.comp_code+"' AND a.ilja = b.exp_ilja "
                    "ORDER BY A.ILJA,B.KEY_ILJA ")
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        item_cnt = len(rows)
        self.tw_expenses.setRowCount(item_cnt)
        style = "::section {""background-color: lightblue; }"
        self.tw_expenses.horizontalHeader().setStyleSheet(style)
        # self.tw_reserve.setShowGrid(False)

        #호실 정보 보여주기
        for idx, col in enumerate(rows):
            # self.tw_reserve.item(0, 0).setBackground(QBrush(Qt.red))

            self.tw_expenses.setItem(idx, 0, QTableWidgetItem(col["ILJA"]))#일자
            self.tw_expenses.setItem(idx, 1, QTableWidgetItem(col["WK"]))#요일
            self.tw_expenses.item(idx, 1).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            if col["WK"] == '일':
                self.tw_expenses.item(idx, 0).setForeground(QBrush(Qt.red))
                self.tw_expenses.item(idx, 1).setForeground(QBrush(Qt.red))
                self.tw_expenses.item(idx, 0).setFont(QFont("Arial", 12, QFont.Bold, italic=False))  # 글자 폰트 설정.
                self.tw_expenses.item(idx, 1).setFont(QFont("Arial", 12, QFont.Bold, italic=False))  # 글자 폰트 설정.
            elif col["WK"] == '토':
                self.tw_expenses.item(idx, 0).setForeground(QBrush(Qt.blue))
                self.tw_expenses.item(idx, 1).setForeground(QBrush(Qt.blue))
                self.tw_expenses.item(idx, 0).setFont(QFont("Arial", 12, QFont.Bold, italic=False))  # 글자 폰트 설정.
                self.tw_expenses.item(idx, 1).setFont(QFont("Arial", 12, QFont.Bold, italic=False))  # 글자 폰트 설정.
            else:
                self.tw_expenses.item(idx, 0).setForeground(QBrush(Qt.black))
                self.tw_expenses.item(idx, 1).setForeground(QBrush(Qt.black))

            self.tw_expenses.setItem(idx, 2, QTableWidgetItem(col["EXP_NAME"]))#품명
            self.tw_expenses.setItem(idx, 3, QTableWidgetItem(col["PAYMENT_NAME"]))#결재수단
            if col["EXP_QTY"] is None or col["EXP_QTY"] == 0 or col["EXP_QTY"] == '0':
                self.tw_expenses.setItem(idx, 4, QTableWidgetItem(''))  # 수량
                self.tw_expenses.setItem(idx, 5, QTableWidgetItem(''))  # 단가
                self.tw_expenses.setItem(idx, 6, QTableWidgetItem(''))  # 금액
            else:
                self.tw_expenses.setItem(idx, 4, QTableWidgetItem(str(col["EXP_QTY"])))#수량
                self.tw_expenses.item(idx, 4).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tw_expenses.setItem(idx, 5, QTableWidgetItem(str(col["EXP_PRICE"])))#단가
                self.tw_expenses.item(idx, 5).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tw_expenses.setItem(idx, 6, QTableWidgetItem(str(col["EXP_SUM"])))#금액
                self.tw_expenses.item(idx, 6).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tw_expenses.setItem(idx, 7, QTableWidgetItem(col["EXP_PO"]))#구입처
            self.tw_expenses.setItem(idx, 8, QTableWidgetItem(col["EXP_TEL"]))#전화번호
            self.tw_expenses.setItem(idx, 9, QTableWidgetItem(col["EXP_BIGO"]))#비고
            self.tw_expenses.setItem(idx, 10, QTableWidgetItem(col["EXP_INLINK"]))#비고

        self.tw_expenses.resizeRowsToContents()
        self.tw_expenses.resizeColumnsToContents()#col 자릿수에 맡게 보여주려면...
        self.tw_expenses.verticalHeader().setVisible(False)  # row header 숨기기
        self.tw_expenses.setEditTriggers(QAbstractItemView.NoEditTriggers)#수정 불가하게
        self.tw_expenses.setSelectionBehavior(QAbstractItemView.SelectRows)#한줄씩 선택
        self.tw_expenses.setCurrentCell(item_cnt-1, 0)  # 마지막 ROW 위로 이동
        # if item_cnt > 5 :
        #     self.tw_expenses.setCurrentCell(item_cnt, 0)  # 한 ROW 위로 이동
            # self.tw_expenses.setCurrentCell(item_cnt-4, 0)  # 한 ROW 위로 이동