
# 인터넷을 통해 종목코드를 보내 검색한다.
# import subprocess
import webbrowser


def inlink_url(url):
    # url = "http://finance.naver.com/item/main.nhn?code="+stockcode
    if url is None or url == '':
        url ='http://www.naver.com'
    # import webbrowser
    webbrowser.open_new_tab(url)