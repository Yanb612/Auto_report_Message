import click
from dgut_requests.dgut import dgutIllness
from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError
import datetime
import pytz



@click.command()
@click.option('-U', '--username', required=True, help="中央认证账号用户名", type=str)
@click.option('-P', '--password', required=True, help="中央认证账号密码", type=str)
@click.option('-L', '--location', help="经纬度")
@click.option('-M', '--message', help="接收短信号码")
@click.option('-I', '--app', help="短信发送AppID及Appkey", default=None, type=str)
def main(username, password,location,message,app):
    users = username.split(",")
    pwds = password.split(",")
    message = message.split(",")
    locations = {int(item.split(',')[0]): (float(item.split(',')[1]), float(item.split(
        ',')[2])) for item in location.strip('[]').split('],[')} if location else {}

    if app:
        app = app.split(",")
    if len(users) != len(pwds) != len(message):
        exit("账号和密码及短信发送号码个数不一致")
    for usr in enumerate(zip(users,pwds,message), 1):
        print(usr)
        u = dgutIllness(usr[1][0], usr[1][1])
        if locations.get(usr[0]):
            report = u.report(locations.get(usr[0])[0], locations.get(usr[0])[1])
        else:
            report = u.report()
        print(report)
        tzchina = pytz.timezone('Asia/Shanghai')
        utc = pytz.timezone('UTC')
        localtime = datetime.datetime.utcnow().replace(tzinfo = utc).astimezone(tzchina).strftime("%H:%M:%S")
        localtime = str(localtime)
        if(usr[1][2]!=0 and app!=None):
            sendMassage(app,usr[1][2],report,localtime)


def sendMassage(app,message,report,localtime):

    appid = int(app[0])
    appkey = app[1]
    phone_num = message
    sign = '煙與霧'
    sender = SmsSingleSender(appid,appkey)
    if report['code'] == 200:
        template_param_list = [localtime]
        try:
            response  = sender.send_with_param(86,phone_num,1033208,template_param_list,sign=sign)
        except HTTPError as e:
            response = {'result': 1000, 'errmsg': "网络异常发送失败"}
        return response
    else:
        report_message = report['message'];
        template_param_list = [report['message'],localtime]
        try:
            if(report_message != "今日已提交，请勿重复操作")：
                response = sender.send_with_param(86, phone_num, 1033210, template_param_list, sign=sign)
        except HTTPError as e:
            response = {'result': 1000, 'errmsg': "网络异常发送失败"}
        return response

if __name__ == '__main__':
    main()
