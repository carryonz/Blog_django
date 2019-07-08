import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable


def scrapy_library(username,pwd):
    response = requests.get(
        url='http://tsgweb.jxust.edu.cn/index.asp',
        headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
    )
    cookie_dict = response.cookies.get_dict()
    response = requests.post(
        url='http://tsgweb.jxust.edu.cn/dzjs/login.asp',
        headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        },
        data={
            'user': username,
            'pw': pwd,
            'imageField.x': '23',
            'imageField.y': '8'
        },
        cookies=cookie_dict
    )
    response = requests.get(
        url='http://tsgweb.jxust.edu.cn/dzjs/login_form.asp',
        headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        },
        cookies=cookie_dict
    )
    response.encoding=response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')
    name = soup.find(name='table', attrs={'class': 'pnavbox'}).find(name='td').text
    name.strip(' ')
    nam = name.split()
    name = nam[-1]
    print(name)
    return (cookie_dict, True if response.text.find("安全退出") >= 0 else False, response, name)


def get_borrow_table(_user_,_pwd_):
    (cookie, status, response, name) = scrapy_library(_user_, _pwd_)
    response = requests.post(
        url='http://tsgweb.jxust.edu.cn/dzjs/jhcx.asp',
        data={
            'nCxfs': '1'
        },
        headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        },
        cookies=cookie
    )
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')
    trs = soup.find(name='td', attrs={'valign': 'top', 'width': '626', 'class': 'pmain'}).find_all(name='table')
    if len(trs) == 1:
        return None
    trs = trs[1].find_all(name='tr')
    # lists = trs[0].find_all(name='td')
    return output(trs)


def get_back_table(_user_,_pwd_):
    (cookie, status, response, name) = scrapy_library(_user_, _pwd_)
    response = requests.post(
        url='http://tsgweb.jxust.edu.cn/dzjs/jhcx.asp',
        data={
            'nCxfs': '2'
        },
        headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        },
        cookies=cookie
    )
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')
    trs = soup.find(name='td', attrs={'valign': 'top', 'width': '626', 'class': 'pmain'}).find_all(name='table')
    if len(trs) == 1:
        return None
    trs = trs[1].find_all(name='tr')
    return output(trs)


def output(trs):
    list = []
    for it in trs:
        td_list = it.find_all('td')
        tmp = [td.text.strip() for td in td_list]
        list.append(tmp)
    print(len(list))
    return list

if __name__ == '__main__':
    get_back_table("1520163227",'1520163227')