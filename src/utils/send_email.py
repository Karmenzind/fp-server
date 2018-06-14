# -*- coding:utf-8 -*-

"""
发送邮件
"""

import email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class MailSender(object):

    def __init__(self, host, username, password, to_emails, subject, content):
        """ 初始化
        @param  host        邮件服务端host
        @param  username    用户名
        @param  password    密码
        @param  to_emails   发送到邮箱列表
        @param  title       标题
        @param  content     内容
        """
        self.host = host
        self.username = username
        self.password = password
        self.to_emails = to_emails
        self.subject = subject
        self.content = content

    def send_mail(self):
        """ 发送邮件
        """
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = self.subject
        msgRoot['From'] = self.username
        msgRoot['To'] = ",".join(self.to_emails)
        msgRoot['Date'] = email.utils.formatdate()
        msgRoot.preamble = 'This is a multi-part message in MIME format.'
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        msgText = MIMEText(self.content, 'plain', 'GB2312')
        msgAlternative.attach(msgText)
        # msgText = MIMEText(self.content, 'html', 'GB2312')
        # msgAlternative.attach(msgText)

        # sending mail
        svr = smtplib.SMTP(self.host, 25)
        # svr = smtplib.SMTP(self.host)
        svr.set_debuglevel(0)
        svr.ehlo()
        svr.starttls()
        svr.login(self.username, self.password)
        svr.sendmail(self.username, self.to_emails, msgRoot.as_string())
        svr.quit()


def test():
    host = 'smtp.xxx.com'
    username = 'test@xxxx.com'
    password = '123456'
    to_emails = ['valesail7@gmail.com']
    subject = 'Test Send Email'
    content = "Just a test."

    sender = MailSender(host, username, password, to_emails, subject, content)
    sender.send_mail()


if __name__ == "__main__":
    test()
