from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QBrush, QRegExpValidator, QColor, QPalette, QFont
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.gridspec import  GridSpec
import matplotlib.pyplot as plt
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
class Revenue_table_period2025_pst_Window(QMainWindow):
    def __init__(self,pf_os,comp_code,user_id):
        super().__init__()
        self.move(10, 50)
        self.setFixedSize(1910, 903)
        if pf_os == 'Windows':
            option_ui = 'UiDir/revenue_table_period_pst.ui'
        else:
            option_ui = 'UiDir/revenue_table_period_pst.ui'


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
        self.pb_search.clicked.connect(self.select_rtn)  # 자료 조회
        #self.pb_excel.clicked.connect(self.excel_rtn)  #엑셀 파일로 저장 어
        self.first_sch()  # 첫 화면시 현재일자를 검색해온다.
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.first_sch)
        # self.timer.start(1000000)#10분 한번 읽어오려면

    #오늘 일자를 먼저 보여주려면....
    def init_rtn(self):
        # 현재 일자를 검색
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_sel = ("SELECT date_format(date_add(CURDATE(), INTERVAL -10 day),'%Y-%m-%d'), "
                     "date_format(date_add(CURDATE(), INTERVAL 7 day),'%Y-%m-%d') from dual")
        # print(query_sel)
        csr.execute(query_sel)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        # now_ilja = rows[0][0]

        self.de_start_ilja_sch.setDate(datetime.strptime(rows[0][0], '%Y-%m-%d'))  # 조회시작일자
        self.de_end_ilja_sch.setDate(datetime.strptime(rows[0][1], '%Y-%m-%d'))  # 조회종료일자

    def select_rtn(self):
        if self.de_start_ilja_sch.date() > self.de_end_ilja_sch.date():
            QMessageBox.about(self, "정보", "일자를 정확히 입력하세요....")
            self.tw_reserve.setRowCount(0)
            self.de_start_ilja_sch.setFocus()
        else:
            for i in reversed(range(self.lo_grap.count())):
                check = self.lo_grap.itemAt(i).widget()
                self.lo_grap.removeWidget(check)
                check.deleteLater()
            self.first_sch()

    #자료를 가져와 화면에 뿌려준다.
    def first_sch(self):

        start_ilja_sch = self.de_start_ilja_sch.date().toString('yyyy-MM-dd')#입실일자
        end_ilja_sch = self.de_end_ilja_sch.date().toString('yyyy-MM-dd')#퇴실일자

        # 객실 예약 현황 가져오기
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_sel = ("select decode_oracle(a,null,0,a) as a,"
                     "decode_oracle(b,null,0,b) as d,FORMAT(decode_oracle(a,null,0,a) - decode_oracle(b,null,0,b),0) as c,"
                     "decode_oracle(e,null,0,e) as e FROM "
                     "(SELECT FORMAT((SELECT COUNT(*)* DATEDIFF(%s,%s) FROM yeogak_room_name_info_tbl),0) as a,"
                     "FORMAT(count(reserve_site),0) AS b,"
                     "FORMAT(ROUND((count(reserve_site)/(SELECT COUNT(*)* DATEDIFF(%s,%s) FROM yeogak_room_name_info_tbl)*100),2),2) AS E"
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
            self.pb_geak.setText('객실 현황 ('+str(start_ilja_sch)+'~'+str(end_ilja_sch)+')')
            self.ed_geak_01.setText(str(rows[0][0])+'실')  #총 객실수
            self.ed_geak_02.setText(str(rows[0][1])+'실')  # 숙박
            self.ed_geak_03.setText(str(rows[0][2])+'실')  # 공실
            self.ed_geak_04.setText(str(rows[0][3])+'%')  # 예약율


        # 수입 현황 가져오기
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_sel = ("""SELECT decode_oracle(sum(if(a.payment = '7',pay_sum,0)),null,0,sum(if(a.payment = '7',pay_sum,0)))+decode_oracle(sum(if(b.add_payment = '7',add_sum,0)),null,0,sum(if(b.add_payment = '7',add_sum,0))) AS a,
                        decode_oracle(sum(if(payment = '1',pay_sum,0)),null,0,sum(if(payment = '1',pay_sum,0)))+decode_oracle(sum(if(b.add_payment = '1',add_sum,0)),null,0,sum(if(b.add_payment = '1',add_sum,0))) AS b,
                        decode_oracle(sum(if(payment = '5',pay_sum,0)),null,0,sum(if(payment = '5',pay_sum,0)))+decode_oracle(sum(if(b.add_payment = '5',add_sum,0)),null,0,sum(if(b.add_payment = '5',add_sum,0))) AS c,
                        decode_oracle(sum(if(payment = '3' OR payment = '9',pay_sum,0)),null,0,sum(if(payment = '3' OR payment = '9',pay_sum,0)))+decode_oracle(sum(if(b.add_payment = '3' OR b.add_payment = '9',add_sum,0)),null,0,sum(if(b.add_payment = '3' OR b.add_payment = '9',add_sum,0))) AS d,                     
                        decode_oracle(SUM(a.pay_sum),NULL,0,SUM(a.pay_sum))+decode_oracle(SUM(b.add_sum),NULL,0,SUM(b.add_sum)) AS e
                        FROM yeogak_reserve2025_tbl a LEFT OUTER JOIN yeogak_addpayment2025_tbl b
                        USING(comp_code,key_ilja,room_ilja)
                        WHERE comp_code = %s and room_ilja BETWEEN %s AND %s  AND a.cancel_chk = '0' """)
        # print(query_sel)
        t=(self.comp_code,start_ilja_sch,end_ilja_sch)
        csr.execute(query_sel,t)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        cnt = len(rows)
        if cnt > 0 :
            reven_in01 = rows[0][0]  # 신용카드(인트넷)
            reven_si01 = rows[0][1]  # 신용카드(현장)
            reven_tr01 = rows[0][2]  # 계좌이체
            reven_cd01 = rows[0][3]  # 현금
            reven_tot01 = rows[0][4]  # 합계
            # self.pb_mea.setText('기간 '+str(start_ilja_sch)+'~'+str(end_ilja_sch)+'  매출 현황')
            self.ed_reven_in01.setText(format(int(reven_in01), ',')+'원')  # 신용카드(인트넷)
            self.ed_reven_si01.setText(format(int(reven_si01), ',')+'원')  # 신용카드(현장)
            self.ed_reven_tr01.setText(format(int(reven_tr01), ',')+'원')  # 계좌이체
            self.ed_reven_cd01.setText(format(int(reven_cd01), ',')+'원')  # 현금
            self.ed_reven_hap01.setText(format(int(reven_tot01), ',')+'원')  # 합계


        # 지출 현황 가져오기
        #환불(취소) 현황
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_sel = ("""SELECT decode_oracle(sum(if(cancel_payment = '1',cancel_sum,0)),null,0,sum(if(cancel_payment = '1',cancel_sum,0))) AS a,
                        decode_oracle(sum(if(cancel_payment = '5',cancel_sum,0)),null,0,sum(if(cancel_payment = '5',cancel_sum,0))) AS b,
                        decode_oracle(sum(if(cancel_payment = '3' OR cancel_payment = '9',cancel_sum,0)),null,0,sum(if(cancel_payment = '3' OR cancel_payment = '9',cancel_sum,0))) AS c,
                        decode_oracle(sum(if(cancel_payment = '7',cancel_sum,0)),null,0,sum(if(cancel_payment = '7',cancel_sum,0))) AS d,                     
                        decode_oracle(SUM(cancel_sum),NULL,0,SUM(cancel_sum)) AS e
                        FROM yeogak_reserve2025_cancel_tbl
                        WHERE comp_code = %s and cancel_ilja BETWEEN %s AND %s """)
        # print(query_sel)
        t=(self.comp_code,start_ilja_sch,end_ilja_sch)
        csr.execute(query_sel,t)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        cnt = len(rows)
        if cnt > 0 :
            exp_rep_in01 = rows[0][0] # 신용카드(인트넷)
            exp_rep_si01 = rows[0][1]  # 신용카드(현장)
            exp_rep_tr01 = rows[0][2] # 계좌이체
            exp_rep_cd01 = rows[0][3] # 현금
            exp_rep_tot01 = rows[0][4]  # 환불(취소) 소계
            # self.pb_mea.setText('기간 '+str(start_ilja_sch)+'~'+str(end_ilja_sch)+'  매출 현황')
            self.ed_exp_rep_in01.setText(format(int(exp_rep_in01), ',')+'원')  # 신용카드(인트넷)
            self.ed_exp_rep_si01.setText(format(int(exp_rep_si01), ',')+'원')  # 신용카드(현장)
            self.ed_exp_rep_tr01.setText(format(int(exp_rep_tr01), ',')+'원')  # 계좌이체
            self.ed_exp_rep_cd01.setText(format(int(exp_rep_cd01), ',')+'원')  # 현금
            self.ed_exp_rep_tot01.setText(format(int(exp_rep_tot01), ',')+'원')  #환불(취소)  소계

        # 물품 구입 지출 현황
        mra = mariadb_conn().conn
        csr = mra.cursor()
        query_sel = ("""SELECT decode_oracle(sum(if(exp_payment = '5',exp_sum,0)),null,0,sum(if(exp_payment = '5',exp_sum,0))) AS a,
                        decode_oracle(sum(if(exp_payment = '3' OR exp_payment = '9',exp_sum,0)),null,0,sum(if(exp_payment = '3' OR exp_payment = '9',exp_sum,0))) AS b,
                        decode_oracle(sum(if(exp_payment = '7',exp_sum,0)),null,0,sum(if(exp_payment = '7',exp_sum,0))) AS c,
                        decode_oracle(sum(if(exp_payment = '1',exp_sum,0)),null,0,sum(if(exp_payment = '1',exp_sum,0))) AS d,                     
                        decode_oracle(SUM(exp_sum),NULL,0,SUM(exp_sum)) AS e
                        FROM expenses_day_tbl
                        WHERE comp_code = %s and exp_ilja BETWEEN %s AND %s """)
        # print(query_sel)
        t=(self.comp_code,start_ilja_sch,end_ilja_sch)
        csr.execute(query_sel,t)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        cnt = len(rows)
        if cnt > 0 :
            exp_buy_in01 = rows[0][0]  # 신용카드(인트넷)
            exp_buy_si01 = rows[0][1]  # 신용카드(현장)
            exp_buy_tr01 = rows[0][2]  # 계좌이체
            exp_buy_cd01 = rows[0][3] # 현금
            exp_buy_tot01 = rows[0][4] # 물품 구입 지출 소계

            self.ed_exp_buy_in01.setText(format(int(exp_buy_in01), ',')+'원')  # 신용카드(인트넷)
            self.ed_exp_buy_si01.setText(format(int(exp_buy_si01), ',')+'원')  # 신용카드(현장)
            self.ed_exp_buy_tr01.setText(format(int(exp_buy_tr01), ',')+'원')  # 계좌이체
            self.ed_exp_buy_cd01.setText(format(int(exp_buy_cd01), ',')+'원')  # 현금
            self.ed_exp_buy_tot01.setText(format(int(exp_buy_tot01), ',')+'원')  #환불(취소)  소계

            #지출현황 합계
            self.ed_exp_tot01.setText(format(int(exp_buy_tot01+exp_rep_tot01), ',')+ '원')  # 지출현황에서  총 합 계

            #매출현황  지출부분
            self.ed_reven_tot01.setText(format(int(reven_tot01), ',')+'원')  # 합계
            #매출현황  지출부분
            self.ed_reven_tot02.setText(format(int(exp_rep_tot01+exp_buy_tot01), ',')+'원')  # 합계
            #매출현황 합계
            self.ed_reven_tot03.setText(format(int(reven_tot01 - (exp_rep_tot01+exp_buy_tot01)), ',')+'원')  # 합계

        #사이트 별  수입현황
        mra = mariadb_conn().conn
        csr = mra.cursor() #딕셔너리 형태로 표현하기 위해....
        query_sel = (""" SELECT FN_APPCOMP_NAME(RESERVE_SITE) AS RESERVE_SITE,decode_oracle(payment,'','',NULL,'', FN_CODE_NAME('PAY',payment)) AS PAYMENT,
                        PAY_SUM,EXP_SUM,TOT_SUM FROM 
                        (SELECT reserve_site,payment,SUM(pay_sum) AS pay_sum,SUM(cancel_sum) as exp_sum, SUM(pay_sum) - SUM(cancel_sum) AS tot_sum  FROM 
                        ((SELECT reserve_site,payment,pay_sum,0 AS cancel_sum from
                        (SELECT reserve_site,payment,sum(pay_sum) AS pay_sum FROM 
                        ((SELECT reserve_site,payment,pay_sum FROM yeogak_reserve2025_tbl 
                        WHERE  comp_code = %s and room_ilja BETWEEN %s AND %s AND cancel_chk = '0' )
                        UNION all
                        (SELECT a.reserve_site, b.add_payment AS payment,sum(b.add_sum) AS pay_sum
                        FROM yeogak_reserve2025_tbl a JOIN yeogak_addpayment2025_tbl b
                        USING (comp_code,key_ilja,room_ilja)
                        where a.comp_code = %s AND a.room_ilja BETWEEN %s AND %s AND a.cancel_chk = '0') )   AS a
                        GROUP BY reserve_site,payment) AS a 
                        WHERE pay_sum > 0) 
                        UNION  all
                        (SELECT reserve_site,payment,0 as pay_sum,cancel_sum FROM 
                        (SELECT a.reserve_site, b.cancel_payment AS payment,decode_oracle(b.cancel_sum,NULL,0,b.cancel_sum) AS cancel_sum
                        FROM yeogak_reserve2025_tbl a LEFT OUTER JOIN yeogak_reserve2025_cancel_tbl b
                        ON  a.comp_code = b.comp_code AND a.key_ilja = b.key_ilja AND a.room_ilja = b.cancel_start_ilja 
                        where a.comp_code = %s AND a.room_ilja BETWEEN %s AND %s AND a.cancel_chk = '0') a
                        WHERE cancel_sum > 0) )a
                        GROUP BY 	reserve_site,payment	) a""")
        # print(query_sel)
        t = (self.comp_code,start_ilja_sch,end_ilja_sch,self.comp_code,start_ilja_sch,end_ilja_sch,self.comp_code,start_ilja_sch,end_ilja_sch)
        csr.execute(query_sel,t)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        cnt = len(rows)
        if cnt > 0 :
            df = pd.DataFrame(rows, columns=['site', 'payment', 'pay_sum','exp_sum','tot_sum'])
            table=pd.pivot_table(df, values=['pay_sum','exp_sum','tot_sum'], index=['site', 'payment'],aggfunc='sum')
            df_incom = pd.concat([d._append(d.sum().rename((k,  '소   계'))) for k, d in table.groupby('site')])._append(table.sum().rename(('합',  '계')))
            df_incom = df_incom.reset_index()

            item_cnt = len(df_incom)
            self.tw_income.setRowCount(item_cnt)
            style = "::section {""background-color: '#bacdf5'; }"
            self.tw_income.horizontalHeader().setStyleSheet(style)

            self.tw_income.resizeRowsToContents()
            # self.tw_reserve.setShowGrid(False)
            site_chk = ''
            # 정보 보여주기
            for idx, col in df_incom.iterrows():
                if df_incom.loc[idx, "site"] != site_chk:
                    if df_incom.loc[idx, "site"] =='합' and df_incom.loc[idx, "payment"] == '계':
                        self.tw_income.setItem(idx, 0, QTableWidgetItem(df_incom.loc[idx, "site"]))#구분
                        self.tw_income.item(idx, 0).setBackground(QBrush(QColor('#f7e1dc')))
                        self.tw_income.item(idx, 0).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.tw_income.setItem(idx, 1, QTableWidgetItem(df_incom.loc[idx, "payment"]))#결제수단
                        self.tw_income.item(idx, 1).setBackground(QBrush(QColor('#f7e1dc')))
                        self.tw_income.item(idx, 1).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.tw_income.setItem(idx, 2, QTableWidgetItem(format(int(df_incom.loc[idx, "pay_sum"]), ',')+'원'))#호실
                        self.tw_income.item(idx, 2).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.tw_income.item(idx, 2).setFont(QFont('Arial', 12))
                        self.tw_income.item(idx, 2).setForeground(QBrush(Qt.red))  # 글자색
                        self.tw_income.item(idx, 2).setBackground(QBrush(QColor('#f7e1dc')))
                        self.tw_income.setItem(idx, 3, QTableWidgetItem(format(int(df_incom.loc[idx, "exp_sum"]), ',')+'원'))#호실
                        self.tw_income.item(idx, 3).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.tw_income.item(idx, 3).setFont(QFont('Arial', 12))
                        self.tw_income.item(idx, 3).setForeground(QBrush(Qt.red))  # 글자색
                        self.tw_income.item(idx, 3).setBackground(QBrush(QColor('#f7e1dc')))
                        self.tw_income.setItem(idx, 4, QTableWidgetItem(format(int(df_incom.loc[idx, "tot_sum"]), ',')+'원'))#호실
                        self.tw_income.item(idx, 4).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.tw_income.item(idx, 4).setFont(QFont('Arial', 12))
                        self.tw_income.item(idx, 4).setForeground(QBrush(Qt.red))  # 글자색
                        self.tw_income.item(idx, 4).setBackground(QBrush(QColor('#f7e1dc')))
                    else:
                        self.tw_income.setItem(idx, 0, QTableWidgetItem(df_incom.loc[idx, "site"]))#구분
                        self.tw_income.item(idx, 0).setBackground(QBrush(QColor('#baf5c8')))
                        self.tw_income.item(idx, 0).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                        self.tw_income.setItem(idx, 1, QTableWidgetItem(df_incom.loc[idx, "payment"]))#결제수단
                        self.tw_income.item(idx, 1).setBackground(QBrush(QColor('#baf5c8')))
                        self.tw_income.item(idx, 1).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                        self.tw_income.setItem(idx, 2, QTableWidgetItem(format(int(df_incom.loc[idx, "pay_sum"]), ',')+'원'))#호실
                        self.tw_income.item(idx, 2).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.tw_income.item(idx, 2).setForeground(QBrush(Qt.blue))  # 글자색
                        self.tw_income.item(idx, 2).setFont(QFont('Arial', 10))
                        self.tw_income.setItem(idx, 3, QTableWidgetItem(format(int(df_incom.loc[idx, "exp_sum"]), ',')+'원'))#호실
                        self.tw_income.item(idx, 3).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.tw_income.item(idx, 3).setForeground(QBrush(Qt.blue))  # 글자색
                        self.tw_income.item(idx, 3).setFont(QFont('Arial', 10))
                        self.tw_income.setItem(idx, 4, QTableWidgetItem(format(int(df_incom.loc[idx, "tot_sum"]), ',')+'원'))#호실
                        self.tw_income.item(idx, 4).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.tw_income.item(idx, 4).setForeground(QBrush(Qt.blue))  # 글자색
                        self.tw_income.item(idx, 4).setFont(QFont('Arial', 10))

                    site_chk = df_incom.loc[idx, "site"]
                else:
                    self.tw_income.setItem(idx, 0, QTableWidgetItem(''))#구분
                    self.tw_income.item(idx, 0).setBackground(QBrush(QColor(255,255,255)))
                    #self.tw_income.item(idx, 0).setBackground(QBrush(QColor('#baf5c8')))
                    self.tw_income.item(idx, 0).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    if df_incom.loc[idx, "payment"] !='소   계':
                        self.tw_income.setItem(idx, 1, QTableWidgetItem(df_incom.loc[idx, "payment"]))#결제수단
                        self.tw_income.item(idx, 1).setBackground(QBrush(QColor('#baf5c8')))
                        self.tw_income.item(idx, 1).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                        self.tw_income.setItem(idx, 2, QTableWidgetItem(format(int(df_incom.loc[idx, "pay_sum"]), ',')+'원'))#호실
                        self.tw_income.item(idx, 2).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.tw_income.item(idx, 2).setForeground(QBrush(Qt.blue))  # 글자색
                        self.tw_income.item(idx, 2).setFont(QFont('Arial', 10)) # font
                        self.tw_income.setItem(idx, 3, QTableWidgetItem(format(int(df_incom.loc[idx, "exp_sum"]), ',')+'원'))#호실
                        self.tw_income.item(idx, 3).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.tw_income.item(idx, 3).setForeground(QBrush(Qt.blue))  # 글자색
                        self.tw_income.item(idx, 3).setFont(QFont('Arial', 10)) # font
                        self.tw_income.setItem(idx, 4, QTableWidgetItem(format(int(df_incom.loc[idx, "tot_sum"]), ',')+'원'))#호실
                        self.tw_income.item(idx, 4).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.tw_income.item(idx, 4).setForeground(QBrush(Qt.blue))  # 글자색
                        self.tw_income.item(idx, 4).setFont(QFont('Arial', 10)) # font
                    else:
                        self.tw_income.setItem(idx, 1, QTableWidgetItem(df_incom.loc[idx, "payment"]))#결제수단
                        self.tw_income.item(idx, 1).setBackground(QBrush(QColor( '#f9fad4')))
                        self.tw_income.item(idx, 1).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                        self.tw_income.setItem(idx, 2, QTableWidgetItem(format(int(df_incom.loc[idx, "pay_sum"]), ',')+'원'))#호실
                        self.tw_income.item(idx, 2).setBackground(QBrush(QColor( '#f9fad4')))
                        self.tw_income.item(idx, 2).setForeground(QBrush(Qt.red))  # 글자색
                        self.tw_income.item(idx, 2).setFont(QFont('Arial', 10))
                        self.tw_income.item(idx, 2).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.tw_income.setItem(idx, 3, QTableWidgetItem(format(int(df_incom.loc[idx, "exp_sum"]), ',')+'원'))#호실
                        self.tw_income.item(idx, 3).setBackground(QBrush(QColor( '#f9fad4')))
                        self.tw_income.item(idx, 3).setForeground(QBrush(Qt.red))  # 글자색
                        self.tw_income.item(idx, 3).setFont(QFont('Arial', 10))
                        self.tw_income.item(idx, 3).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.tw_income.setItem(idx, 4, QTableWidgetItem(format(int(df_incom.loc[idx, "tot_sum"]), ',')+'원'))#호실
                        self.tw_income.item(idx, 4).setBackground(QBrush(QColor( '#f9fad4')))
                        self.tw_income.item(idx, 4).setForeground(QBrush(Qt.red))  # 글자색
                        self.tw_income.item(idx, 4).setFont(QFont('Arial', 10))
                        self.tw_income.item(idx, 4).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.tw_income.resizeColumnsToContents()#col 자릿수에 맡게 보여주려면...
            self.tw_income.verticalHeader().setVisible(False)  # row header 숨기기
            self.tw_income.setEditTriggers(QAbstractItemView.NoEditTriggers)#수정 불가하게
            self.tw_income.setSelectionBehavior(QAbstractItemView.SelectRows)#한줄씩 선택
            # self.tw_reserve.setCurrentCell(row_focus_cnt-1, 0)  # 한 ROW 위로 이동
        else:
            self.tw_income.setRowCount(0)
            style = "::section {""background-color: '#bacdf5'; }"
            self.tw_income.horizontalHeader().setStyleSheet(style)

            self.tw_income.resizeRowsToContents()
            self.tw_income.resizeColumnsToContents()#col 자릿수에 맡게 보여주려면...
            self.tw_income.verticalHeader().setVisible(False)  # row header 숨기기
            self.tw_income.setEditTriggers(QAbstractItemView.NoEditTriggers)#수정 불가하게


        mra = mariadb_conn().conn
        csr = mra.cursor()  # 딕셔너리 형태로 표현하기 위해....
        # query_sel = (""" SELECT b.exp_ilja as exp_ilja,
        # query_sel = (""" SELECT STR_TO_DATE(b.exp_ilja, '%Y-%m-%d') as exp_ilja,
        query_sel = (""" SELECT b.exp_ilja as exp_ilja,
                    CAST(a.pay_sum/10000  AS UNSIGNED) as pay_sum, CAST(b.exp_sum/10000 AS UNSIGNED) as exp_sum,
                    abs((a.pay_sum - b.exp_sum)/10000) AS tot_sum
                    FROM 
                    (SELECT room_ilja, SUM(pay_sum) AS pay_sum from
                    ((SELECT a.ilja AS room_ilja,decode_oracle(b.pay_sum,NULL,0,b.pay_sum) AS pay_sum FROM yeogak_reserve_day_tbl AS a LEFT OUTER JOIN yeogak_reserve2025_tbl  AS b
                    ON  b.comp_code = %s AND a.ilja = b.room_ilja
                    WHERE a.ilja BETWEEN %s AND %s)
                    union
                    (SELECT room_ilja,add_sum AS pay_sum
                    FROM yeogak_addpayment2025_tbl 
                    where comp_code = %s AND room_ilja BETWEEN %s AND %s)) AS  a
                    GROUP BY room_ilja) AS a,                    
                    (SELECT a.room_ilja AS exp_ilja,decode_oracle(cancel_sum + exp_sum,NULL,0,cancel_sum + exp_sum) exp_sum FROM 
                    (SELECT a.ilja AS room_ilja,sum(decode_oracle(b.cancel_sum,'',0,NULL,0,b.cancel_sum)) AS cancel_sum
                    FROM  yeogak_reserve_day_tbl AS a LEFT OUTER JOIN  yeogak_reserve2025_cancel_tbl AS b
                    ON  b.comp_code = %s AND a.ilja = b.cancel_ilja 
                    WHERE   a.ilja BETWEEN %s AND %s 
                    GROUP BY ilja) AS a 
                    LEFT OUTER JOIN 
                    (SELECT exp_ilja AS room_ilja, sum(exp_sum) as exp_sum FROM  expenses_day_tbl
                    WHERE  comp_code = %s AND exp_ilja BETWEEN %s AND %s
                    GROUP BY exp_ilja) AS b
                    USING(room_ilja)
                    ORDER BY room_ilja) AS b                    
                    WHERE a.room_ilja = b.exp_ilja  ORDER BY B.EXP_ILJA
                    """)
        # print(query_sel)
        t = (self.comp_code,start_ilja_sch,end_ilja_sch,self.comp_code,start_ilja_sch,end_ilja_sch,
             self.comp_code,start_ilja_sch,end_ilja_sch,self.comp_code,start_ilja_sch,end_ilja_sch)
        # t = ('A010001', '2024-01-01', '2024-02-20', 'A010001', '2024-01-01', '2024-02-20')
        csr.execute(query_sel,t)
        rows = csr.fetchall()
        csr.close()
        mra.close()
        item_cnt = len(rows)
        if item_cnt > 0 :
            df = pd.DataFrame(rows, columns=['exp_ilja', 'pay_sum', 'exp_sum','tot_sum'])


            # layout를 초기화 하려면....
            if self.lo_grap.count() > 0:
                for i in reversed(range(self.lo_grap.count())):
                    self.lo_grap.itemAt(i).widget().setParent(None)

            figure = plt.figure(figsize=(20,20))
            canvas = FigureCanvas(figure)

            self.lo_grap.addWidget(canvas)
            self.ax = canvas.figure.subplots()
            # self.ax.plot([0, 1, 2], [1, 5, 3], '-')
            barWidth = 0.25
            # Set position of bar on X axis
            x0 = np.arange(len(df.index))
            x1 = [x0 + barWidth for x0 in x0]
            x2 = [x0 + barWidth for x0 in x1]
            # Make the plot

            self.ax.set_title('매출 현황 ('+str(start_ilja_sch)+'~'+str(end_ilja_sch)+')\n',fontweight ='bold', fontsize = 18)
            self.ax.set_xlabel('', fontweight ='bold', fontsize = 15)
            self.ax.set_ylabel('가격(단위:만원)', fontweight ='bold', fontsize = 15)
            bar_res01 = self.ax.bar(x0, df['tot_sum'], label='매출',color ='r',width = barWidth, edgecolor ='grey')
            bar_res02 = self.ax.bar(x1, df['pay_sum'],  label='수입', color ='g',width = barWidth, edgecolor ='grey')
            bar_res03 = self.ax.bar(x2, df['exp_sum'], label ='지출',color ='b',  width = barWidth, edgecolor ='grey')
            # self.ax.bar_label(bar_res01, padding=3)
            # self.ax.bar_label(bar_res02, padding=3)
            # self.ax.bar_label(bar_res03, padding=3)
            self.ax.legend()
            # rule = rrulewrapper(YEARLY, byeaster=1, interval=5)
            # loc = RRuleLocator(rule)
            # self.ax.xaxis.set_major_locator(loc)
            div01 = int(len(df.index)/10)
            if div01 < 1 :
                div01 = 1

            cnt = len(df.index)
            s1= []
            for r in range(len(df.index)):
                if r%div01 == 0:
                    s1.append(df.loc[r,'exp_ilja'])
                else:
                    s1.append('')
            # print(s1)
            df['title_day'] = s1

            self.ax.set_xticks([r + barWidth for r in range(len(df.index))],df['title_day'],rotation=45, fontsize = 8)


            # cursor = Cursor(self.ax, horizOn=True, vertOn=True, useblit=True,
            #                 color='r', linewidth=1)
            cursor = Cursor(self.ax, color='green', linewidth=2)
            # Creating an annotating box
            annot = self.ax.annotate("", xy=(0, 0), xytext=(-40, 40), textcoords="offset points",
                                bbox=dict(boxstyle='round4', fc='linen', ec='k', lw=1),
                                arrowprops=dict(arrowstyle='-|>'))
            annot.set_visible(False)


            self.coord = []


            def onclick(event):
                # global coord
                self.coord.append((event.xdata, event.ydata))
                x = event.xdata
                y = event.ydata

                # printing the values of the selected point
                # print([x, y])
                annot.xy = (x, y)
                text = "{:,.0f}".format(y)
                annot.set_text(text)
                annot.set_visible(True)
                figure.canvas.draw()  # redraw the figure

            figure.canvas.mpl_connect('button_press_event', onclick)


