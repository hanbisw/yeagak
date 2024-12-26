from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QBrush, QRegExpValidator, QColor, QPalette, QFont
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.gridspec import  GridSpec
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.widgets import Cursor

import numpy as np
import pandas as pd
import subprocess
import webbrowser
from pathlib import Path
import os

from config.mariadb_connection import mariadb_conn
import mariadb
from datetime import timedelta,datetime
from openpyxl import Workbook
from openpyxl.styles import Font,Alignment,PatternFill,Border,Side,colors
# 한글 폰트 사용을 위해서 세팅
from matplotlib import font_manager, rc
import threading
import time
# from function.inputtypehandler import InputTypeHandler


# class StockIndexWindow(QMainWindow, form_class):
class Revenue_table_month2025_pst_Window(QMainWindow):
    def __init__(self,pf_os,comp_code,user_id):
        super().__init__()
        self.move(10, 50)
        self.setFixedSize(1910, 903)
        if pf_os == 'Windows':
            option_ui = 'UiDir/revenue_table_month_pst.ui'
        else:
            option_ui = 'UiDir/revenue_table_month_pst.ui'


        self.comp_code = comp_code
        self.user_id = user_id
        # option_ui = 'UiDir/StockCompInfo.ui'
        uic.loadUi(option_ui, self)

        font_path = "C:/Windows/Fonts/batang.ttc"
        font = font_manager.FontProperties(fname=font_path).get_name()
        rc('font', family=font)

        regExp = QRegExp("[0-9]*") #edit에 숫자만 입력 처리하기 위해
        palette = QPalette()
        palette.setColor(QPalette.Highlight, QColor(144, 153, 234))  # default ==> Qt.darkBlue
        self.str_ = '-'  # 203-1호실일때 -호일이 있는가를 찾으려면.....
        self.tw_income.setPalette(palette)
        self.init_rtn()#오늘 일자를 먼저 보여주려면......
        self.pb_search.clicked.connect(self.first_sch)  # 자료 조회
        #self.pb_excel.clicked.connect(self.excel_rtn)  #엑셀 파일로 저장 어
        self.first_sch()  # 첫 화면시 현재일자를 검색해온다.
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.first_sch)
        # self.timer.start(1000000)#10분 한번 읽어오려면

    #오늘 일자를 먼저 보여주려면....
    def init_rtn(self):
        # 현재 일자를 검색
        mra = mariadb_conn().conn
        csr = mra.cursor(dictionary=True) #딕셔너리 형태로 표현하기 위해....
        query_sel = "SELECT distinct(YEAR(ilja)) as Year from yeogak_reserve_day_tbl"
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        # now_ilja = rows[0][0]
        #객실 타입 보여주기
        for idx, col in enumerate(rows):
            self.cb_year.addItem(str(col["Year"]))

        # 현재 년과 월을 검색
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_sel = """SELECT date_format(date_add(CURDATE(), INTERVAL 0 day),'%Y'), 
                       date_format(date_add(CURDATE(), INTERVAL 0 day),'%m')"""
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        self.cb_year.setCurrentText(str(rows[0][0]))#해당년도에 매칭하려면...
        self.cb_month.setCurrentText(str(rows[0][1]))  # 해당월에 매칭하려면...
    #자료를 가져와 화면에 뿌려준다.
    def first_sch(self):

        year_sch = self.cb_year.currentText()#조회년도
        month_sch = self.cb_month.currentText()  # 조회월
        start_ilja_sch = year_sch + '-' + month_sch + '%'
        #월최대값을 가져오기 31,30,29일
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_sel = "SELECT MIN(ilja), MAX(ilja) from yeogak_reserve_day_tbl WHERE ilja LIKE '"+start_ilja_sch+"' "
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        start_ilja_sch = str(rows[0][0]) #월의 최저값을 갖는다.
        end_ilja_sch = str(rows[0][1]) #월의 최대값  31,20,29을 가져온다
        # print("%s,%s"% (start_ilja_sch,end_ilja_sch))

        # 객실 예약 현황 가져오기
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_sel = ("select  FORMAT(a,0),FORMAT(b,0),FORMAT(a - b,0) AS c,FORMAT(e,2) AS e  FROM "
                     "(SELECT (SELECT COUNT(*)* DATEDIFF(%s,%s) FROM yeogak_room_name_info_tbl) as a,"
                     "count(reserve_site) AS b,"
                     "ROUND((count(reserve_site)/(SELECT COUNT(*)* DATEDIFF(%s,%s) FROM yeogak_room_name_info_tbl)*100),2) AS E"
                     " FROM yeogak_reserve2025_tbl WHERE comp_code = %s and room_ilja BETWEEN %s AND %s AND cancel_chk = '0' ) a")
        # print(query_sel)
        t=(end_ilja_sch,start_ilja_sch,end_ilja_sch,start_ilja_sch,self.comp_code,start_ilja_sch,end_ilja_sch)
        # print(t)
        csr.execute(query_sel,t)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        cnt = len(rows)
        if cnt > 0 :
            self.pb_geak.setText(year_sch+'년 '+month_sch+'월  객 실  현 황 ')
            self.ed_geak_01.setText(str(rows[0][0])+'실')  #총 객실수
            self.ed_geak_02.setText(str(rows[0][1])+'실')  # 숙박
            self.ed_geak_03.setText(str(rows[0][2])+'실')  # 공실
            self.ed_geak_04.setText(str(rows[0][3])+'%')  # 예약율

        query_sel01 = ("select DATE_FORMAT(ILJA,'%Y-%m-%d') as ILJA,SUBSTR( _UTF8'일월화수목금토', DAYOFWEEK(DATE_FORMAT(ILJA,'%Y-%m-%d')), 1) AS wk, "
                        "SUM(a) AS a, SUM(b) AS b , SUM(c) AS c, SUM(d) AS d, SUM(e) AS e,SUM(aa) AS aa, SUM(bb) AS bb, SUM(cc) AS cc, SUM(dd) AS dd, SUM(ee) AS ee, "
                        "SUM(aaa) AS aaa, SUM(bbb) AS bbb, SUM(ccc) AS ccc, SUM(ddd) AS ddd, SUM(eee) AS eee FROM "
                        "(SELECT aa.ilja AS ilja, "
                        "decode_oracle(sum(if(payment = '1',pay_sum,0)),null,0,sum(if(payment = '1',pay_sum,0)))+decode_oracle(sum(if(b.add_payment = '1',add_sum,0)),null,0,sum(if(b.add_payment = '1',add_sum,0))) AS a, "
                        "decode_oracle(sum(if(payment = '5',pay_sum,0)),null,0,sum(if(payment = '5',pay_sum,0)))+decode_oracle(sum(if(b.add_payment = '5',add_sum,0)),null,0,sum(if(b.add_payment = '5',add_sum,0))) AS b, "
                        "decode_oracle(sum(if(payment = '3' OR payment = '9',pay_sum,0)),null,0,sum(if(payment = '3' OR payment = '9',pay_sum,0)))+decode_oracle(sum(if(b.add_payment = '3' OR b.add_payment = '9',add_sum,0)),null,0,sum(if(b.add_payment = '3' OR b.add_payment = '9',add_sum,0))) AS c, "
                        "decode_oracle(sum(if(a.payment = '7',pay_sum,0)),null,0,sum(if(a.payment = '7',pay_sum,0)))+decode_oracle(sum(if(b.add_payment = '7',add_sum,0)),null,0,sum(if(b.add_payment = '7',add_sum,0))) AS d, "
                        "decode_oracle(SUM(a.pay_sum),NULL,0,SUM(a.pay_sum))+decode_oracle(SUM(b.add_sum),NULL,0,SUM(b.add_sum)) AS e, "
                        "0 AS aa, 0 AS bb, 0 AS cc, 0 AS dd, 0 AS ee, 0 AS aaa, 0 AS bbb, 0 AS ccc, 0 AS ddd, 0 AS eee "
                        "FROM yeogak_reserve_day_tbl aa LEFT OUTER JOIN yeogak_reserve2025_tbl a ON aa.ilja =  a.room_ilja AND a.comp_code = %s  AND a.cancel_chk = '0' "
                        "LEFT OUTER JOIN yeogak_addpayment2025_tbl b ON a.comp_code = b.comp_code AND a.key_ilja = b.key_ilja AND a.room_ilja =b.room_ilja "
                        "WHERE aa.ilja BETWEEN %s AND %s GROUP by aa.ilja "
                        "UNION all "
                        "SELECT aa.ilja AS ilja,0 AS a, 0 AS b, 0 AS c, 0 AS d, 0 AS e, "
                        "decode_oracle(sum(if(d.cancel_payment = '1',d.cancel_sum,0)),null,0,sum(if(d.cancel_payment = '1',d.cancel_sum,0))) AS aa, "
                        "decode_oracle(sum(if(d.cancel_payment = '5',d.cancel_sum,0)),null,0,sum(if(d.cancel_payment = '5',d.cancel_sum,0))) AS bb, "
                        "decode_oracle(sum(if(d.cancel_payment = '3' OR d.cancel_payment = '9',d.cancel_sum,0)),null,0,sum(if(d.cancel_payment = '3' OR d.cancel_payment = '9',d.cancel_sum,0))) AS cc, "
                        "decode_oracle(sum(if(d.cancel_payment = '7',d.cancel_sum,0)),null,0,sum(if(d.cancel_payment = '7',d.cancel_sum,0))) AS dd, "
                        "decode_oracle(SUM(d.cancel_sum),NULL,0,SUM(d.cancel_sum)) AS ee, "
                        "0 AS aaa, 0 AS bbb, 0 AS ccc, 0 AS ddd, 0 AS eee "
                        "FROM yeogak_reserve_day_tbl aa "
                        "LEFT OUTER JOIN yeogak_reserve2025_cancel_tbl d ON aa.ilja =  d.cancel_ilja AND d.comp_code = %s "
                        "WHERE aa.ilja BETWEEN %s AND %s group by aa.ilja "
                        "UNION all "
                        "SELECT aa.ilja AS ilja,0 AS a, 0 AS b, 0 AS c, 0 AS d, 0 AS e, 0 AS aa, 0 AS bb, 0 AS cc, 0 AS dd, 0 AS ee, "
                        "decode_oracle(sum(if(exp_payment = '1',exp_sum,0)),null,0,sum(if(exp_payment = '1',exp_sum,0))) AS aaa, "
                        "decode_oracle(sum(if(exp_payment = '5',exp_sum,0)),null,0,sum(if(exp_payment = '5',exp_sum,0))) AS bbb, "
                        "decode_oracle(sum(if(exp_payment = '3' OR exp_payment = '9',exp_sum,0)),null,0,sum(if(exp_payment = '3' OR exp_payment = '9',exp_sum,0))) AS ccc, "
                        "decode_oracle(sum(if(exp_payment = '7',exp_sum,0)),null,0,sum(if(exp_payment = '7',exp_sum,0))) AS ddd, "
                        "decode_oracle(SUM(exp_sum),NULL,0,SUM(exp_sum)) AS eee "
                        "FROM yeogak_reserve_day_tbl aa "
                        "LEFT OUTER JOIN expenses_day_tbl e ON aa.ilja =  e.exp_ilja AND e.comp_code = %s "
                        "WHERE aa.ilja BETWEEN %s AND %s group by aa.ilja) a GROUP BY a.ilja")

        # #년간 월별  매출현황
        mra = mariadb_conn().conn
        csr = mra.cursor() #딕셔너리 형태로 표현하기 위해....
        # print(query_sel01)
        t = (self.comp_code,start_ilja_sch,end_ilja_sch,self.comp_code,start_ilja_sch,end_ilja_sch,self.comp_code,start_ilja_sch,end_ilja_sch)
        # print(t)
        csr.execute(query_sel01,t)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        # print(rows)
        cnt = len(rows)
        if cnt > 0 :
            df = pd.DataFrame(rows, columns=['ilja','wk','pay_01','pay_02','pay_03','pay_04','pay_05',
                                             'cancel_01','cancel_02','cancel_03','cancel_04','cancel_05',
                                             'exp_01','exp_02','exp_03','exp_04','exp_05'])
            df.set_index('ilja', inplace=False)
            df['tot_05'] = df['pay_05'] - (df['cancel_05']+df['exp_05'])
            df01=df.sum()
            # print(df01)
            df = df._append(df01, ignore_index=True)
            df.reset_index()
            df.loc[df.index[-1], 'ilja'] = '합 계'
            df.loc[df.index[-1], 'wk'] = ''

            # print(df)
            reven_tot01 = 0
            exp_rep_tot01 = 0
            exp_buy_tot01 = 0

            # df_incom = df.reset_index()
            # print(df)
            item_cnt = len(df)
            # print(item_cnt)
            if item_cnt > 0:

                self.pb_title.setText(year_sch+'년 '+month_sch+'월 매출 현황')
                self.tw_income.setRowCount(item_cnt)
                style = "::section {""background-color: '#bacdf5'; }"
                self.tw_income.horizontalHeader().setStyleSheet(style)

                self.tw_income.resizeRowsToContents()#
                # 정보 보여주기
                for idx, col in df.iterrows():
                    if df.loc[idx, "ilja"] == '합 계':
                        self.pb_mea.setText(year_sch+'년 '+month_sch+'월 매출 현황')
                        self.ed_reven_in01.setText(format(int(df.loc[idx, "pay_01"]), ',')+'원')  # 온라인결재
                        self.ed_reven_si01.setText(format(int(df.loc[idx, "pay_02"]), ',')+'원')   # 신용카드(현장)
                        self.ed_reven_tr01.setText(format(int(df.loc[idx, "pay_03"]), ',')+'원')   # 계좌이체
                        self.ed_reven_cd01.setText(format(int(df.loc[idx, "pay_04"]), ',')+'원')  # 현금
                        self.ed_reven_tot01.setText(format(int(df.loc[idx, "pay_05"]), ',')+'원')   # 합계

                        self.ed_reven_in02.setText(format(int(df.loc[idx, "cancel_01"]+df.loc[idx, "exp_01"]), ',')+'원')  # 지출 온라인결재
                        self.ed_reven_si02.setText(format(int(df.loc[idx, "cancel_02"]+df.loc[idx, "exp_02"]), ',')+'원')   # 지출 신용카드(현장)
                        self.ed_reven_tr02.setText(format(int(df.loc[idx, "cancel_03"]+df.loc[idx, "exp_03"]), ',')+'원')   # 지출 계좌이체
                        self.ed_reven_cd02.setText(format(int(df.loc[idx, "cancel_04"]+df.loc[idx, "exp_04"]), ',')+'원')   # 지출 현금
                        self.ed_reven_tot02.setText(format(int(df.loc[idx, "cancel_05"]+df.loc[idx, "exp_05"]), ',')+'원')   #지출   소계

                        self.ed_reven_in03.setText(format(int(df.loc[idx, "pay_01"]-(df.loc[idx, "cancel_01"]+df.loc[idx, "exp_01"])), ',')+'원')  # 합계 온라인결재
                        self.ed_reven_si03.setText(format(int(df.loc[idx, "pay_02"]-(df.loc[idx, "cancel_02"]+df.loc[idx, "exp_02"])), ',')+'원')   # 합계 신용카드(현장)
                        self.ed_reven_tr03.setText(format(int(df.loc[idx, "pay_03"]-(df.loc[idx, "cancel_03"]+df.loc[idx, "exp_03"])), ',')+'원')   # 합계 계좌이체
                        self.ed_reven_cd03.setText(format(int(df.loc[idx, "pay_04"]-(df.loc[idx, "cancel_04"]+df.loc[idx, "exp_04"])), ',')+'원')   # 합계 현금
                        self.ed_reven_tot03.setText(format(int(df.loc[idx, "pay_05"]-(df.loc[idx, "cancel_05"]+df.loc[idx, "exp_05"])), ',')+'원')   #합계

                        reven_tot01 = int(df.loc[idx, "pay_05"])
                        exp_rep_tot01 = int(df.loc[idx, "cancel_05"])
                        exp_buy_tot01 = int(df.loc[idx, "exp_05"])
                        self.tw_income.setItem(idx, 0, QTableWidgetItem(df.loc[idx, "ilja"]))#해당 월
                        self.tw_income.item(idx, 0).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.tw_income.setItem(idx, 1, QTableWidgetItem(df.loc[idx, "wk"]))#해당 요일
                        self.tw_income.item(idx, 1).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        if df.loc[idx, "wk"] == '일':
                            self.tw_income.item(idx, 0).setForeground(QBrush(Qt.red))
                            self.tw_income.item(idx, 1).setForeground(QBrush(Qt.red))
                            self.tw_income.item(idx, 0).setFont(QFont("Arial", 10, QFont.Bold, italic=False))  # 글자 폰트 설정.
                            self.tw_income.item(idx, 1).setFont(QFont("Arial", 10, QFont.Bold, italic=False))  # 글자 폰트 설정.
                        elif df.loc[idx, "wk"] == '토':
                            self.tw_income.item(idx, 0).setForeground(QBrush(Qt.blue))
                            self.tw_income.item(idx, 1).setForeground(QBrush(Qt.blue))
                            self.tw_income.item(idx, 0).setFont(QFont("Arial", 10, QFont.Bold, italic=False))  # 글자 폰트 설정.
                            self.tw_income.item(idx, 1).setFont(QFont("Arial", 10, QFont.Bold, italic=False))  # 글자 폰트 설정.
                        else:
                            self.tw_income.item(idx, 0).setForeground(QBrush(Qt.black))
                            self.tw_income.item(idx, 1).setForeground(QBrush(Qt.black))
                            self.tw_income.item(idx, 0).setFont(QFont("Arial", 10, QFont.Bold, italic=False))  # 글자 폰트 설정.
                            self.tw_income.item(idx, 1).setFont(QFont("Arial", 10, QFont.Bold, italic=False))  # 글자 폰트 설정.

                        self.tw_income.setItem(idx, 2, QTableWidgetItem(format(int(df.loc[idx, "pay_05"]), ',')+'원'))#수익현황
                        self.tw_income.item(idx, 2).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.tw_income.item(idx, 2).setFont(QFont('Arial', 10))

                        self.tw_income.setItem(idx, 3, QTableWidgetItem(format(int(df.loc[idx, "cancel_05"]), ',')+'원'))#환불현황
                        self.tw_income.item(idx, 3).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.tw_income.item(idx, 3).setFont(QFont('Arial', 10))

                        self.tw_income.setItem(idx, 4, QTableWidgetItem(format(int(df.loc[idx, "exp_05"]), ',')+'원'))#물품구입 지출현황
                        self.tw_income.item(idx, 4).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.tw_income.item(idx, 4).setFont(QFont('Arial', 10))

                        self.tw_income.setItem(idx, 5, QTableWidgetItem(format(int(df.loc[idx, "tot_05"]), ',')+'원'))#해당 월 합게
                        self.tw_income.item(idx, 5).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.tw_income.item(idx, 5).setFont(QFont('Arial', 10))
                        self.tw_income.item(idx, 5).setForeground(QBrush(Qt.red))  # 글자색
                    else:
                        self.tw_income.setItem(idx, 0, QTableWidgetItem(df.loc[idx, "ilja"]))#해당 월
                        self.tw_income.item(idx, 0).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.tw_income.setItem(idx, 1, QTableWidgetItem(df.loc[idx, "wk"]))#해당 요일
                        self.tw_income.item(idx, 1).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        if df.loc[idx, "wk"] == '일':
                            self.tw_income.item(idx, 0).setForeground(QBrush(Qt.red))
                            self.tw_income.item(idx, 1).setForeground(QBrush(Qt.red))
                            self.tw_income.item(idx, 0).setFont(QFont("Arial", 10, QFont.Bold, italic=False))  # 글자 폰트 설정.
                            self.tw_income.item(idx, 1).setFont(QFont("Arial", 10, QFont.Bold, italic=False))  # 글자 폰트 설정.
                        elif df.loc[idx, "wk"] == '토':
                            self.tw_income.item(idx, 0).setForeground(QBrush(Qt.blue))
                            self.tw_income.item(idx, 1).setForeground(QBrush(Qt.blue))
                            self.tw_income.item(idx, 0).setFont(QFont("Arial", 10, QFont.Bold, italic=False))  # 글자 폰트 설정.
                            self.tw_income.item(idx, 1).setFont(QFont("Arial", 10, QFont.Bold, italic=False))  # 글자 폰트 설정.
                        else:
                            self.tw_income.item(idx, 0).setForeground(QBrush(Qt.black))
                            self.tw_income.item(idx, 1).setForeground(QBrush(Qt.black))
                            self.tw_income.item(idx, 0).setFont(QFont("Arial", 10, QFont.Bold, italic=False))  # 글자 폰트 설정.
                            self.tw_income.item(idx, 1).setFont(QFont("Arial", 10, QFont.Bold, italic=False))  # 글자 폰트 설정.

                        self.tw_income.setItem(idx, 2, QTableWidgetItem(format(int(df.loc[idx, "pay_05"]), ',')+'원'))#수익현황
                        self.tw_income.item(idx, 2).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.tw_income.item(idx, 2).setFont(QFont('Arial', 10))

                        self.tw_income.setItem(idx, 3, QTableWidgetItem(format(int(df.loc[idx, "cancel_05"]), ',')+'원'))#환불현황
                        self.tw_income.item(idx, 3).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.tw_income.item(idx, 3).setFont(QFont('Arial', 10))

                        self.tw_income.setItem(idx, 4, QTableWidgetItem(format(int(df.loc[idx, "exp_05"]), ',')+'원'))#물품구입 지출현황
                        self.tw_income.item(idx, 4).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.tw_income.item(idx, 4).setFont(QFont('Arial', 10))

                        self.tw_income.setItem(idx, 5, QTableWidgetItem(format(int(df.loc[idx, "tot_05"]), ',')+'원'))#해당 월 합게
                        self.tw_income.item(idx, 5).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.tw_income.item(idx, 5).setFont(QFont('Arial', 10))
                        self.tw_income.item(idx, 5).setForeground(QBrush(Qt.red))  # 글자색

                self.tw_income.resizeColumnsToContents()#col 자릿수에 맡게 보여주려면...
                self.tw_income.verticalHeader().setVisible(False)  # row header 숨기기
                self.tw_income.setEditTriggers(QAbstractItemView.NoEditTriggers)#수정 불가하게
                self.tw_income.setSelectionBehavior(QAbstractItemView.SelectRows)#한줄씩 선택
            else:
                self.tw_income.setRowCount(0)
                style = "::section {""background-color: '#bacdf5'; }"
                self.tw_income.horizontalHeader().setStyleSheet(style)

                self.tw_income.resizeRowsToContents()
                self.tw_income.resizeColumnsToContents()  # col 자릿수에 맡게 보여주려면...
                self.tw_income.verticalHeader().setVisible(False)  # row header 숨기기
                self.tw_income.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 수정 불가하게
            # self.tw_reserve.setCurrentCell(row_focus_cnt-1, 0)  # 한 ROW 위로 이동

            # 실제 그래프 그리기

        # pie  chart 그리기 전 금액이 없다면 통과하고 있다면 그리려면.....
        if int(reven_tot01) > 0 or  int(exp_rep_tot01) > 0 or  int(exp_buy_tot01) > 0:
            #pie  chart 그리기

            #layout를 초기화 하려면....
            if self.lo_grap.count() > 0 :
                for i in reversed(range(self.lo_grap.count())):
                    self.lo_grap.itemAt(i).widget().setParent(None)
            # colors
            # colors = ['#FF0000', '#0000FF', '#FFFF00', '#ADFF2F', '#FFA500']
            colors = ['#147bb7', '#ff7f00', '#f7e600']

            sizes = [int(reven_tot01), int(exp_rep_tot01),int(exp_buy_tot01)]#숙박금액,환불금액,물품구입금액

            labels = ['숙박금액', '환불금액','물품구입금액']
            # self.MplWidget.canvas.figure.clear()#
            # explosion
            explode = (0.05, 0.05, 0.05)
            textprops = {"fontsize":15} # Font size of text in pie chart
            # self.lo_grap.clear()
            figure = plt.figure(figsize=(30,30))
            canvas = FigureCanvas(figure)
            self.lo_grap.addWidget(canvas)
            self.ax = canvas.figure.subplots()

            self.ax.set_title(year_sch+'년도 '+month_sch+'월 매출 현황\n',fontweight ='bold', fontsize = 18)
            # Pie Chart
            self.ax.pie(sizes, colors=colors, labels=labels,
                    autopct='%1.1f%%', pctdistance=0.85,
                    explode=explode,
                    textprops =textprops)
            # draw circle
            centre_circle = Circle((0, 0), 0.70, fc='white')
            self.ax.add_patch(centre_circle)
            # self.ax.legend(loc=(1.2,0.25), title='구 분')
            # self.ax.legend(loc=(0, 0), title='구 분')
            self.ax.legend(loc="upper right", title='구 분')
        else:
            # print(self.lo_grap.count())
            if self.lo_grap.count() > 0 :
                for i in reversed(range(self.lo_grap.count())):
                    # print('aaaa')
                    self.lo_grap.itemAt(i).widget().setParent(None)