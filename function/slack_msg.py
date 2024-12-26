import mariadb
import requests
import json

from config.mariadb_connection import mariadb_conn

def slack_push(comp_code,text):
    # webhook url
    # url = "https://hooks.slack.com/services/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"

    # 서버에서 오늘 날짜를 가져오려면
    mra = mariadb_conn().conn
    csr = mra.cursor()
    query_sel = "SELECT slack_url from slack_url_tbl where comp_code = '"+comp_code+"' "
    # print(query_sel)

    csr.execute(query_sel)
    rows = csr.fetchall()
    csr.close()
    mra.close()
    url = rows[0][0]


    payload = {
        "text": text
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
    	rtn_msg = '메시지를 성공적으로 보냈습니다.'
    else:
    	rtn_msg = '메시지를 성공적으로 보내지 못했습니다. 오류메시지 : ' + str(response.status_code)
    return(rtn_msg)


# # slack massge 보내기
# text = "일자 : " + to_day_in + "  종목 명 : " + self.stockname
# slack_push(text)