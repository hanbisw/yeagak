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
import threading
import time
# from function.inputtypehandler import InputTypeHandler

from function.inlink import inlink_url

# class StockIndexWindow(QMainWindow, form_class):
class Expenses_day_pst_Window(QMainWindow):
    def __init__(self,pf_os,comp_code,user_id):
        super().__init__()
        self.move(10, 50)
        self.setFixedSize(1729, 903)
        if pf_os == 'Windows':
            option_ui = 'UiDir/expenses_day_pst.ui'
        else:
            option_ui = 'UiDir/expenses_day_pst.ui'

        self.comp_code = comp_code
        self.user_id = user_id
        # option_ui = 'UiDir/StockCompInfo.ui'
        uic.loadUi(option_ui, self)

        regExp = QRegExp("[0-9]*") #edit에 숫자만 입력 처리하기 위해
        palette = QPalette()
        palette.setColor(QPalette.Highlight, QColor(144, 153, 234))  # default ==> Qt.darkBlue
        # palette.setColor(QPalette.HighlightedText, Qt.red)  # default ==> Qt.white
        self.tw_expenses.setPalette(palette)
        self.init_rtn()#오늘 일자를 먼저 보여주려면......
        self.pb_search.clicked.connect(self.first_sch)  # 자료 조회
        self.pb_clear.clicked.connect(self.expenes_clear)  # 저장 화면을 클리어
        self.tw_expenses.clicked.connect(self.mouse_click_rtn) # 클릭시 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
        self.tw_expenses.keyPressEvent = self.keyPressEvent #UP, DOWN 키를 누를 때 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
        self.tb_internet.clicked.connect(self.internet_sch)#링크 주소 인터넷으로 연결하기
        self.thread_rtn()#쓰레드 30초마다 자료를 다시 가져오려면

    def thread_rtn(self):
        self.first_sch()
        tt= threading.Timer(30, self.thread_rtn)

    #오늘 일자를 먼저 보여주려면....
    def init_rtn(self):
        # 현재 일자를 검색
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_sel = ("SELECT date_format(CURDATE(),'%Y-%m-%d') from dual")
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        # now_ilja = rows[0][0]

        self.de_start_ilja_sch.setDate(datetime.strptime(rows[0][0], '%Y-%m-%d'))  #일자

    #인터넷 링크 주소 연결하기
    def internet_sch(self):
        inlink_url(self.ed_inlink.text())#인트넷으로 연결하기

    def expenes_clear(self):
        self.ed_ilja.setText("")#일자
        self.ed_name.setText("")  # 품명
        self.ed_qty.setText("")  # 수량
        self.ed_price.setText("")  # 단가
        self.ed_sum.setText("")  # 금액
        self.ed_po.setText("")  # 결재 금액
        self.ed_tel.setText("")  # 당일 근무자
        self.ed_bigo.setText("")  # 예약자
        self.ed_inlink.setText("")  # 예약자

    #KEY_UP, KEY_DOWN을 눌렀다면 .....
    def keyPressEvent (self, eventQKeyEvent):
        key = eventQKeyEvent.key()
        if key == Qt.Key_Up: #up 키를 누를 때마다  해당일자 호실의 정보를 상당 입력란에 보여주려면.....
            row = self.tw_expenses.currentRow() #현재 ROW 값을 가져오려면..
            if row == 0: # 처음 일때 값을 1로 하기 위해
                row += 1
            self.tw_expenses.setCurrentCell(row-1,0)  #한 ROW 위로 이동
            self.search_rtn()

        elif key == Qt.Key_Down:  # down 키를 누를 때마다  해당일자 호실의 정보를 상당 입력란에 보여주려면.....
            row = self.tw_expenses.currentRow() #현재 ROW 값을 가져오려면..
            if row >= (self.tw_expenses.rowCount() -1): #마지막 ROW일때 계속 마지막 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
               row -= 1
            self.tw_expenses.setCurrentCell(row + 1, 0) #한 ROW 밑으로 이동
            self.search_rtn()

    # 클릭시 해당일자 호실의 정보를 상당 입력란에 보여주려면.....
    def mouse_click_rtn(self):
        row = self.tw_expenses.currentRow() #현재 ROW 값을 가져오려면..
        self.tw_expenses.setCurrentCell(row, 0)  # ROW 이동
        self.search_rtn()


    #해당일자 호실에 대한 정보를 상단 입력란에 뿌려주려면.....
    def search_rtn(self):
        self.ed_ilja.setText(self.tw_expenses.item(self.tw_expenses.currentRow(), 0).text())#일자
        self.ed_name.setText(self.tw_expenses.item(self.tw_expenses.currentRow(), 2).text())  # 품명
        self.ed_payment.setText(self.tw_expenses.item(self.tw_expenses.currentRow(), 3).text())  # 수량
        self.ed_qty.setText(self.tw_expenses.item(self.tw_expenses.currentRow(), 4).text())  # 수량
        self.ed_price.setText(self.tw_expenses.item(self.tw_expenses.currentRow(), 5).text())  # 단가
        self.ed_sum.setText(self.tw_expenses.item(self.tw_expenses.currentRow(), 6).text())  #금액
        self.ed_po.setText(self.tw_expenses.item(self.tw_expenses.currentRow(), 7).text()) #구입처
        self.ed_tel.setText(self.tw_expenses.item(self.tw_expenses.currentRow(), 8).text()) #전화번호
        self.ed_bigo.setText(self.tw_expenses.item(self.tw_expenses.currentRow(), 9).text()) #구입처
        self.ed_inlink.setText(self.tw_expenses.item(self.tw_expenses.currentRow(), 10).text()) #인트넷링크

    #자료를 가져와 화면에 뿌려준다.
    def first_sch(self):
        self.expenes_clear()

        start_ilja_sch = self.de_start_ilja_sch.date().toString('yyyy-MM-dd')#시작일자
        # end_ilja_sch = self.de_end_ilja_sch.date().toString('yyyy-MM-dd')#종료일자

        if self.ed_name_search.text() is None or self.ed_name_search.text()=='':
            name_sch = '%'
        else:
            name_sch = '%'+self.ed_name_search.text()+'%'

        #기간 동안 총 지출 합계를 계산하려면.....
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_sel = ("SELECT DECODE_ORACLE(SUM(EXP_SUM), NULL,0,FORMAT(SUM(EXP_SUM),0)) AS TOT_SUM,"
                     "COUNT(*) FROM expenses_day_tbl "
                    "WHERE comp_code = %s AND exp_ilja = %s and exp_name like %s ")
        # print(query_sel)
        t=(self.comp_code,start_ilja_sch,name_sch)
        csr.execute(query_sel,t)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        self.ed_ge_1.setText(start_ilja_sch)#기간
        self.ed_ge_2.setText(str(rows[0][1])+'건')  # 건수
        self.ed_ge_3.setText(str(rows[0][0])+'원')  # 합계

        #기간 내에 지출 정보정보 가져오기
        mra = mariadb_conn().conn
        csr = mra.cursor(dictionary=True) #딕셔너리 형태로 표현하기 위해....
        query_sel = ("SELECT DATE_FORMAT(A.ILJA,'%Y-%m-%d') as ILJA,A.WK,B.EXP_ILJA,B.EXP_NAME,"
                     "decode_oracle(EXP_PAYMENT,'','',FN_CODE_NAME('PAY',EXP_PAYMENT)) AS EXP_PAYMENT,"
                    "FORMAT(B.EXP_QTY,0) AS EXP_QTY,FORMAT(B.EXP_PRICE,0) AS EXP_PRICE,FORMAT(B.EXP_SUM,0) AS EXP_SUM, "
                    "B.EXP_PO,EXP_TEL,B.EXP_BIGO,B.KEY_ILJA,B.EXP_INLINK "
                    "FROM (SELECT ilja,WK  FROM yeogak_reserve_day_tbl "
                    "WHERE ilja = %s) a, "
                    "expenses_day_tbl b "
                    " where b.comp_code = %s AND a.ilja = b.exp_ilja and b.exp_name like %s "
                    "ORDER BY A.ILJA,B.KEY_ILJA ")
        # print(query_sel)
        t=(start_ilja_sch,self.comp_code,name_sch)
        csr.execute(query_sel,t)
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
            self.tw_expenses.setItem(idx, 3, QTableWidgetItem(col["EXP_PAYMENT"]))#결재수단
            if col["EXP_QTY"] is None or col["EXP_QTY"] == 0 or col["EXP_QTY"] == '0':
                self.tw_expenses.setItem(idx, 4, QTableWidgetItem(''))  # 수량
                self.tw_expenses.setItem(idx, 5, QTableWidgetItem(''))  # 단가
                self.tw_expenses.setItem(idx, 6, QTableWidgetItem(''))  # 금액
            else:
                self.tw_expenses.setItem(idx, 4, QTableWidgetItem(str(col["EXP_QTY"])))#수량
                self.tw_expenses.item(idx, 4).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tw_expenses.setItem(idx, 5, QTableWidgetItem(str(col["EXP_PRICE"])+'원'))#단가
                self.tw_expenses.item(idx, 5).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tw_expenses.setItem(idx, 6, QTableWidgetItem(str(col["EXP_SUM"])+'원'))#금액
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