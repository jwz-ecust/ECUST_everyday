w# -*- coding: utf-8 -*-
import requests
import time
from lxml import etree
import sys
import re
import mistune
import smtplib
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.text import MIMEText
reload(sys)
sys.setdefaultencoding('utf-8')


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
    result = re.sub('\n', '\s', title)
    return result


def get_req(url):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
    }
    req = requests.get(url, headers=headers)
    content = req.content
    tree = etree.HTML(content)
    return tree

def send_mail(receiver, content):
    host_server = 'smtp.qq.com'
    sender_qq = "897978644"
    sender_qq_mail = "897978644@qq.com"
    pwd = 'ppnovemkpapebecf'
    mail_title = u'ECUST'
    smtp = SMTP_SSL(host_server)
    smtp.login(sender_qq, pwd)
    msg = MIMEText(content, "html", 'utf-8')
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg["From"] = sender_qq_mail
    msg["To"] = receiver
    smtp.sendmail(sender_qq_mail, receiver, msg.as_string())
    smtp.quit()


content = u''

# notifications
# daily_md = open('./schools.md', 'w')

content += u'## 研究生院通知\n'
# daily_md.write(u'## 研究生院通知\n')

url_notifications = 'http://gschool.ecust.edu.cn/tzgg1/list.htm'
tree_notifications = get_req(url_notifications)
for node in tree_notifications.xpath('//*[starts-with(@class, "list_item")]'):
    # http://gschool.ecust.edu.cn/2018/0604/c8139a76807/page.htm
    note_title = node.xpath('./div/span[2]/a/text()')[0].strip()
    note_title = enter2space(note_title)
    note_link = 'http://gschool.ecust.edu.cn' + node.xpath('./div[1]/span/a/@href')[0]
    note_date = node.xpath('./div[2]/span/text()')[0]
    if is_new_for_today(note_date):
        line = u"{}\t[{}]({})\n".format(note_date, note_title, note_link)
        daily_md.write(line)
        content += line
        # print line

# daily_md.write('\n\n\n\n---\n')
content += '\n\n\n\n---\n'

content += u'## 校园新闻\n'
# daily_md.write(u'## 校园新闻\n')
# news
news_url = 'https://news.ecust.edu.cn/news?important=0'
tree_news = get_req(news_url)
for node in tree_news.xpath('//div[@class="content"]/ul/li/a'):
    news_time = node.xpath('./span[1]/text()')[0].strip()
    news_title = node.xpath('./span[3]/text()')[0].strip()
    news_title = enter2space(news_title)
    news_link = "https://news.ecust.edu.cn" + node.xpath('./@href')[0]
    if is_new_for_today(news_time):
        line = u"{}\t[{}]({})\n".format(news_time, news_title, news_link)
        # daily_md.write(line)
        content += line
        # print line

# daily_md.write('\n\n\n\n---\n')
# daily_md.write(u'## 学术报告\n')
content += '\n\n\n\n---\n'
content += u'## 学术报告\n'
# reports
reports_url = 'https://news.ecust.edu.cn/reports'
tree_reports = get_req(reports_url)
for node in tree_reports.xpath('//div[@class="content"]/ul/li/a'):
    report_time = node.xpath('./span[1]/text()')[0].strip().split(u'：')[-1].strip()
    report_title = node.xpath('./span[3]/text()')[0].strip()
    report_title = enter2space(report_title)
    report_link = "https://news.ecust.edu.cn" + node.xpath('./@href')[0]
    if is_new_for_today(report_time):
        line = u"{}\t[{}]({})\n".format(report_time, report_title, report_link)
        # daily_md.write(line)
        content += line
        # print line

# daily_md.close()

# content convert to html format
html = mistune.markdown(content, escape=True, hard_wrap=True)
# html = open('zjw.html', 'w').write(html)

# send mail
send_mail('aaronzjw6@gmail.com', html)
