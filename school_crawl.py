# -*- coding: utf-8 -*-
import requests
import time
import sys
import re
import os
import mistune
try:
    import ConfigParser
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    import configparser as ConfigParser
import smtplib
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

parser = ConfigParser.ConfigParser()
parser.read('./crawl.conf')


def get_timestamp_from_string(time_string):
    tt = time.strptime(time_string, "%Y-%m-%d")
    return time.mktime(tt)


def is_new_for_today(timestr, delta_time=1.0):
    '''
        to check the news is new for today
    '''
    str2timestamp = get_timestamp_from_string(timestr)
    today = time.time()
    if (today - str2timestamp) / (24 * 3600) < delta_time:
        return True
    else:
        return False


def enter2space(title):
    result = re.sub('[\n]', '', title)
    result = re.sub('\s+', ' ', result)
    return result


def get_req(url):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
    }
    req = requests.get(url, headers=headers)
    content = req.content
    #  tree = etree.HTML(content)
    soup = BeautifulSoup(content, 'html.parser')
    #  return tree
    return soup


def send_mail(receiver, content, name):
    host_server = parser.get('DEFAULT', 'host_server')
    sender_qq = parser.get('DEFAULT', 'send_id')
    sender_qq_mail = parser.get('DEFAULT', 'send_mail')
    pwd = os.environ['PASSWORD']
    mail_title = parser.get('DEFAULT', 'title') + u'\t'  +  name.decode('utf-8')
    smtp = SMTP_SSL(host_server)
    smtp.login(sender_qq, pwd)
    msg = MIMEText(content, "html", 'utf-8')
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg["From"] = sender_qq_mail
    msg["To"] = receiver
    smtp.sendmail(sender_qq_mail, receiver, msg.as_string())
    smtp.quit()


content = u''
# 研究生院通知
content += u'## 研究生院通知\n'
url_notifications = 'http://gschool.ecust.edu.cn/tzgg1/list.htm'
soup_notifications = get_req(url_notifications)
for node in soup_notifications.find_all(attrs={'class': re.compile('list_item i\d+')}):
    note_ = node.find(attrs={'class': 'Article_Title'})
    note_title = note_.a.text
    note_link = 'http://gschool.ecust.edu.cn' + note_.a['href']
    note_date = node.find(attrs={'class': 'Article_PublishDate'}).text
    # print note_title, note_link, note_date
    if is_new_for_today(note_date):
        line = u"{}\t[{}]({})\n".format(note_date, note_title, note_link)
        content += line
        # print line
content += '\n\n\n\n---\n'
#####################################################################
# 校园要闻
# print(u'校园要闻')
content += u'## 校园新闻\n'
news_url = 'https://news.ecust.edu.cn/news?important=0'
soup_news = get_req(news_url)
newscontent = soup_news.find(class_='content').ul
for node in newscontent.find_all('a'):
    news_link = "https://news.ecust.edu.cn" + node['href']
    news_time = node.find(class_='time').text.strip()
    news_title = node.find_all('span')[-1].text.strip()
    if is_new_for_today(news_time):
        line = u"{}\t[{}]({})\n".format(news_time, news_title, news_link)
        content += line
        # print line
content += '\n\n\n\n---\n'

# 校园快讯
# print('##################################################################')
# print(u'校园快讯')
content += u'## 校园快讯\n'
fast_url = 'https://news.ecust.edu.cn/news?important=1'
soup_fast = get_req(fast_url)
fastcontent = soup_fast.find(class_='content').ul
for node in fastcontent.find_all('a'):
    fast_link = "https://news.ecust.edu.cn" + node['href']
    fast_time = node.find(class_='time').text.strip()
    fast_title = node.find_all('span')[-1].text.strip()
    if is_new_for_today(fast_time):
        line = u"{}\t[{}]({})\n".format(fast_time, fast_title, fast_link)
        content += line
        # print line

##################################################################
# 学术报告
content += '\n\n\n\n---\n'
content += u'## 学术报告\n'
# print('##################################################################')
# print(u'学术报告')
reports_url = 'https://news.ecust.edu.cn/reports'
soup_reports = get_req(reports_url)
reportcontent = soup_reports.find(class_='content').ul
for node in reportcontent.find_all('a'):
    report_link = "https://news.ecust.edu.cn" + node['href']
    report_time = node.find(class_='time').text.strip().split(u'：')[-1].strip()
    report_title = node.find_all('span')[-1].text.strip()
    report_title = enter2space(report_title)

    if is_new_for_today(report_time):
        line = u"{}\t[{}]({})\n".format(report_time, report_title, report_link)
        content += line
        # print line

# content convert to html format
html = mistune.markdown(content, escape=True, hard_wrap=True)

# send mail
for user in parser.sections():
    name = parser.get(user, 'name')
    receiver = parser.get(user, 'receiver')
    send_mail(receiver, html, name)

print('Sending Successfully')
