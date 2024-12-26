#이부분을 브라우즈에 입력하면 code = 뒤부분을 받을 수 있다.
# """https://kauth.kakao.com/oauth/authorize?client_id=03dd1fd9d88e4d0321f2bb59f8a26a5f&redirect_uri=https://message_kakaotalk.com/oauth&response_type=code&scope=talk_message,friends"""
#"""https://kauth.kakao.com/oauth/authorize?client_id=984082585000d10bd571018672448492&redirect_uri=https://example.com/oauth&response_type=code&scope=profile_nickname,friends,talk_message"""

# "https://example.com/oauth?code=EawKKydv4I-fJIl10Zn6ODnWn1Qc21rQiTSAuNSelfhmkluKP7MCpq296IEKKcjaAAABjTqakNXmTYKY7N6ACw"
#코드 부분을 아래에서 쓴다

import requests
url = 'https://kauth.kakao.com/oauth/token'
rest_api_key = '984082585000d10bd571018672448492'#REST_API KEY 값 입력
redirect_uri = 'https://example.com/oauth' #Redirect_URI 입력
authorize_code = '7Z2tUViQqoBLzWl3aK6W4n-R9Ih_nDbxa60hmFWzR1PuoKRfpACzaK0xe70KKiVPAAABjU1aQUy37mS5Kc-sjw' #code = 부분

data = {
    'grant_type' : 'authorization_code',
    'client_id' : rest_api_key,
    'redirect_uri' : redirect_uri,
    'code' : authorize_code,
}

response = requests.post(url, data=data)
tokens = response.json()
print(tokens)

#json 파일 저장
import json
# with open(r".\kakao_code.json","w") as fp:
with open(r"..\UiDir\jsonK.ui", "w") as fp:
    json.dump(tokens, fp)
