
from matplotlib import font_manager

class font_names():
    def __init__(self,pf_os):
        if pf_os == 'Windows':
            # 윈도우 사용시
            self.batang = font_manager.FontProperties(fname="c:/Windows/Fonts/batang.ttc").get_name()
        else :
            #리눅스 사용시
            self.batang = font_manager.FontProperties(fname="/usr/share/fonts/baekmuk-ttf-2.2/ttf/batang.ttf").get_name()