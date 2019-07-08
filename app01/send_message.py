import requests


def send(mobile, captcha):
    url = 'http://v.juhe.cn/sms/send'
    params ={
        "mobile": str(mobile), #手机号  必须传
        "tpl_id": "167820", #模板的id
        "tpl_value": "#code#="+str(captcha),
        "key": "4561fb48ad6b20cdc14e17f117debe29",
    }
    response = requests.get(url, params=params)
    result = response.json()
    if result['error_code'] == 0:
        return True
    else:
        return False