from lxml import etree
import urllib.request
from bs4 import BeautifulSoup
import ast


def skip_check():
    f = open("info.txt", "r")
    test = f.read().split('\n')
    f.close()
    return ast.literal_eval(test[1])


def get_staff(skip_flag=False):
    if skip_flag:
        return skip_check()

    web = urllib.request.urlopen("https://petrsu.ru/page/ptoday/svedenia/employees/pedagogitcheskii-nautchnopedagogitc")
    s = web.read()
    html = etree.HTML(s)

    # Get the date
    soup = BeautifulSoup(s, features="lxml")
    soup_date = soup.find("div", {"class": "page-content-dopinfo"}).get_text().replace('\n', '')

    f = open("info.txt", "a+")
    f.close()

    f = open("info.txt", "r")

    test = f.read().split('\n')

    if f.readable() and len(test) >= 2 and str(soup_date) == test[0]:
        web.close()
        f.close()
        print('Таблица не обновлялась')
        return ast.literal_eval(test[1])

    f.close()
    print('Таблицу пришлось обновить :(')

    # Get all 'tr'
    tr_nodes = html.xpath('//table[@class="table table-bordered ped-sostav"]/tr')

    web.close()

    # 'th' is inside first 'tr'
    # header = [i[0].text for i in tr_nodes[1].xpath("th")]

    # Get text from rest all 'tr'
    td_content = [[td.text for td in tr.xpath('td')] for tr in tr_nodes[1:]]

    info = {}

    for item in td_content:
        if len(item) <= 1:
            continue
        if item[1] in info:
            info[item[1]]['subjects taught'].append(item[3])
            continue
        info[item[1]] = {'job title': item[2], 'subjects taught': [item[3], ], 'education': item[4],
                         'academic degree': item[5], 'academic title': item[6], 'upgrade': item[7],
                         'work experience specialty': item[8], 'work experience': item[9]}

    f = open("info.txt", "w")
    f.write(soup_date + '\n' + str(info))
    f.close()

    return info
