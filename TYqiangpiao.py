from selenium import webdriver
from urllib.parse import quote_plus
from test import *
import time
from PIL import Image
from chaojiying import *
from selenium.webdriver.common.action_chains import ActionChains
from email.mime.text import MIMEText
from email.utils import formataddr
import smtplib
# 确认始发站和时间

#出发点目的地，车次，时间
def s_e():
    from_station = input('出发地：')

    to_station = input('目的地：')

    time_ = input('出发日期(xxxx-xx-xx)：')
    S = name_dict.get(from_station,'')
    E = name_dict.get(to_station,'')
    car_list = []
    while True:
        car_num = input('请输入车次(完整车次)：')
        new_num = car_num.upper()
        car_list.append(new_num)
        chieco = input('是否再次输入车次(y/n):')
        if chieco != 'y':
            break
    return quote_plus(from_station), quote_plus(to_station), time_,S,E,car_list

#首次访问，构建服务器
def s_eCar(s, e, t,S,E):

    web = webdriver.Chrome()
    # url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs={}&ts={}&date={}&flag=N,Y,Y'.format(s,e,t)
    url ='https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs={},{}&ts={},{}&date={}&flag=N,Y,Y'.format(s,S,e,E,t)
    web.get(url)
    web.implicitly_wait(10)
    web.maximize_window()
    return web

#判断要求的车次号车票
def check_car(web,car_list=[]):
    id_list = []
    while True:
        try:
            for car in car_list:
                #火车几等座编号
                car_n = re.search(r'<a title="点击查看停靠站信息" href="javascript:" id="(.*)" class="number" onclick="myStopStation.open\((.+),(.+),(.+),(.+),(.+),(.+);">{}</a>'.format(car),web.page_source).group(1)
                _index = car_n.index('_')
                #二等座id
                ze_id = car_n[:_index]
                id_list.append(ze_id)
            return id_list,web
        except:
            web.refresh()
            time.sleep(1)
#邮件发送
def email_():
    msg = MIMEText('抢票成功', 'plain', 'utf-8')
    msg['From'] = formataddr(["管理员", '17600679010@163.cn'])  # 显示发件人信息
    msg['To'] = formataddr(["s", '18612018884@163.com'])  # 显示收件人信息
    msg['Subject'] = "抢票成功"  # 定义邮件主题  # 创建SMTP对象
    server = smtplib.SMTP("smtp.163.com", 25)
    # set_debuglevel(1)可以打印出和SMTP服务器交互的所有信息
    # server.set_debuglevel(1)
    # login()方法用来登录SMTP服务器
    server.login("17600679010@163.com", "z5487693.")
    # sendmail()方法就是发邮件，由于可以一次发给多个人，所以传入一个list，邮件正文是一个str，as_string()把MIMEText对象变成str
    server.sendmail('17600679010@163.com', ['18612018884@163.com', ], msg.as_string())
    print(u"邮件发送成功!")
    server.quit()
#进行登录下单操作
def xiadan(web,acct,pwd,name_list=[]):
    time.sleep(1)
    web.find_element_by_class_name('login-hd-account').click()
    time.sleep(1)
    web.save_screenshot('yanzhengma.png')
    obj_ = Image.open('yanzhengma.png')
    img = web.find_element_by_id('J-loginImg')
    # location = img.location
    x = 763
    y = 360
    # size = img.size
    right = 374
    bottm = 225
    # print(x)
    # print(y)
    # print(size['width'])
    # print(size['height'])
    obj_.crop((x, y, x+right, y+bottm )).save('yanzm.png')
    yzm = Chaojiying_Client('z5487693', 'z5487693.', '898147')
    with open('yanzm.png', 'rb') as f:
        img_b = f.read()
    zuobiao = yzm.PostPic(img_b, 9004)
    zuobiao_list = zuobiao['pic_str'].split('|')
    for i in zuobiao_list:
        x_ = int(i.split(',')[0])
        y_ = int(i.split(',')[1])

        if x_ < 90:
            x_ = 40
        elif 90 <= x_ < 170:
            x_ = 115
        elif 170 <= x_ < 275:
            x_ = 185
        else:
            x_ = 260
        if y_ < 136:
            y_ = 80
        else:
            y_ = 140
        ActionChains(web).move_to_element_with_offset(img,x_,y_).click().perform()
        time.sleep(1)
    web.find_element_by_id('J-userName').send_keys(acct)
    time.sleep(1)
    web.find_element_by_id('J-password').send_keys(pwd)
    time.sleep(1)
    web.find_element_by_id('J-login').click()
    time.sleep(2)
    for name in name_list:
        name_id = re.search('<label for="(.*)" class="" style="cursor: pointer">{}</label>'.format(name),web.page_source).group(1)
        web.find_element_by_id(name_id).click()
        time.sleep(1)
    web.find_element_by_id('submitOrder_id').click()
    time.sleep(2)
    web.find_element_by_id('qr_submit_id').click()
    time.sleep(1)
    while True:
        email_()
        break
    web.quit()
#进行判断是否有票然后进行预订
def yuding(web,acct,pwd,id_list,t_num=1,name_list=[]):
    count = 0
    while True:
        for id in id_list:
            id_car = web.find_element_by_id('ZE_{}'.format(id)).text
            if id_car == '有' or id_car!='无' and int(id_car) >= t_num :
                time.sleep(1)
                while True:
                    web.find_element_by_xpath(
                        '//tbody[@id="queryLeftTable"]/tr[@id="ticket_{}"]/td[@class="no-br"]'.format(id)).click()
                    web.implicitly_wait(3)
                    if web.find_element_by_class_name('login-hd-account'):
                        xiadan(web,acct,pwd,name_list)
                        break
                break
            else:
                web.refresh()
                count +=1
                print('第%s次刷新'%count)
                time.sleep(1)

#调用main函数传入12306账号和密码，预订几个人订票(int类型)，预订人的姓名(list类型放字符串)，账号里面不要有重名的，
def main(acct,pwd,t_num,name_list=[]):
    s, e, t, S, E, car_list = s_e()
    web = s_eCar(s, e, t, S, E)
    id_list, new_web = check_car(web, car_list)
    yuding(new_web, acct, pwd, id_list,t_num,name_list)
if __name__ == '__main__':
    """
    调用main函数传入12306账号和密码(str)，预订几个人订票(int类型)，
    预订人的姓名(list类型放字符串)，账号里面不要有重名的，
    """
    # print(S,E)
    # print(s,e,t,S,E,car_list)
    # s = '%E5%8C%97%E4%BA%AC'
    # e = '%E4%B8%8A%E6%B5%B7'
    # t = '2019-01-10'
    # S = 'BJP'
    # E = 'SHH'
    s, e, t, S, E, car_list = s_e()
    web = s_eCar(s,e,t,S,E)
    id_list,new_web = check_car(web,car_list)
    yuding(new_web,'523917455@qq.com','Zj5487693',id_list,2)
    