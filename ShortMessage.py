# -*- coding:utf8 -*-
import random,time
from urllib.parse import urljoin
from ShowapiRequest import ShowapiRequest
from CaptchaRequest import CaptchaRequest
'''
    https://www.showapi.com/apiGateway/view/?apiCode=28&pointCode=2
    易源返回标志showapi_res_code：
    -0，成功
    -1，系统调用错误
    -2，可调用次数或金额为0
    -3，读取超时
    -4，服务端返回数据解析错误
    -5，后端服务器DNS解析错误
    -6，服务不存在或未上线
    -7, API创建者的网关资源不足
    -1000，系统维护
    -1002，showapi_appid字段必传
    -1003，showapi_sign字段必传
    -1004，签名sign验证有误
    -1005，showapi_timestamp无效
    -1006，app无权限调用接口 
    -1007，没有订购套餐
    -1008，服务商关闭对您的调用权限
    -1009，调用频率受限
    -1010，找不到您的应用
    -1011，子授权app_child_id无效
    -1012，子授权已过期或失效
    -1013，子授权ip受限
    -1014，token权限无效
    
    koko科技接口调用说明 http://dkh.hfsxf.com:81/httphelp.htm
'''

# 生成6位验证码
def genVerCode():
    verCode = ""
    for i in range(6):
        ch = chr(random.randrange(ord('0'), ord('9') + 1))
        verCode += ch
    return verCode


# 创建自定义短信模板
def createTemplates(preUrl,appid, appsecret,content,title,notiPhone,userIp,funcNo = "28-2"):
    """
    :param appid: 系统级参数
    :param appsecret: 系统级参数
    :param content: 应用级参数，短信模板，必要 示例： "您好,[name],验证码是[code], 本次登录密码有效时间为[minute]分钟"
    :param title: 应用级参数，公司名称，必要
    :param notiPhone: 应用级参数，联系人信息，以便审核模板后通知审核结果，必要
    :param userIp: 应用级参数，调用发送短信接口IP白名单，多个用英文;隔开，非必要
    :return showapi_res_code：系统级参数，易源返回标志，详见上方文件注释
    :return showapi_res_id：系统级参数，本次请求ID
    :return showapi_res_error：系统级参数，错误信息
    :return showapi_res_body：系统级参数，返回的应用级参数的JSON封装
    :return ret_code：应用级参数，0为提交到队列成功，其他失败
    :return remark：描述信息
    :return taskID：任务ID
    :return successCounts：计费长度
    """
    url = urljoin(preUrl,funcNo)
    r = ShowapiRequest(url, appid, appsecret)
    r.addBodyPara("content",content)
    r.addBodyPara("title", title)
    r.addBodyPara("notiPhone", notiPhone)
    r.addBodyPara("userIp", userIp)
    res = r.post()
    return res.text


# 获取创建的短信模板
def getTemplates(preUrl,appid, appsecret,page,funcNo = "28-3"):
    """
    :param page: 应用级参数，页码，非必要  示例："1"
    :return ret_code：应用级参数，0为提交到队列成功，其他失败
    :return remark：描述信息
    :return templates：模板列表
                -content：模板内容
                -title：模板标题
                -status：模板状态（0、待审核，1、审核通过，2、审核驳回）
                -tNum：模板ID T170317000714
                -ct：创建时间 2017-03-21 15:04:50
                -sendContentSample：发送内容的示例jsonstring
    """
    url = urljoin(preUrl, funcNo)
    r = ShowapiRequest(url, appid, appsecret)
    r.addBodyPara("page",page)
    res = r.post()
    return res.text


# 发送短信 限制条件:同一号码,30s不超过1条,10分钟不超过10条
def sendMessage(preUrl,appid, appsecret, mobile, content, tNum, bigMsg,funcNo = "28-1"):
    """
    :param mobile: 手机号码，必要
    :param content: string类型，使用json格式对应模板的键值对，动态内容使用,使用UTF-8编码强调下,json中的key和value如果不是数字,则必须用双引号包裹,不要用单引号，非必要
    :param tNum: 短信模板ID，必要
    :param big_msg: 70字符含自定义签名,超过70，请传big_msg=1参数,超过70字符按67个字符算一条短信，最多400个字符，非必要
    :return ret_code：0为提交到队列成功，其他失败
    :return successCounts：计费长度
    :return remark：描述信息
    :return taskID：任务ID
    """
    url = urljoin(preUrl, funcNo)
    r = ShowapiRequest(url, appid, appsecret)
    r.addBodyPara("mobile", mobile)
    r.addBodyPara("content", content)
    r.addBodyPara("tNum", tNum)
    r.addBodyPara("big_msg", bigMsg)
    res = r.post()
    return res.text


# 查询发送历史及结果
def queryDetails(preUrl,appid, appsecret,mobile,page,taskID,date,funcNo = "28-7"):
    """
    :param mobile: 发送的号码(每次查询一个号码)，非必要
    :param page：页码，非必要
    :param taskID：任务ID（与其他参数互斥,如果输入taskID,其他参数则不需要输入）
    :param date：发送日期（yyyy-MM-dd），非必要
    :return ret_code：0为提交到队列成功，其他失败
    :return remark：描述信息
    :return allNum：总条数
    :return allPages：总页数
    :return currentPage：当前页数
    :return maxResult：每页最大条数（固定值20）
    :return datas：list型，历史数据条目
                -statusCode：运营商返回的状态码，有DELIVRD或0:0字样是成功
                -content：短信正文
                -successCounts：扣费次数
                -remark：备注
                -receiveTime：短信状态确定时间（状态由0变为10或20的时间）
                -sendStatus：状态，0为待发送，10发送成功，20发送失败
                -ct：短信发送时间
                -mobile：机主号码
    """
    url = urljoin(preUrl, funcNo)
    r = ShowapiRequest(url, appid, appsecret)
    r.addBodyPara("mobile", mobile)
    r.addBodyPara("page", page)
    r.addBodyPara("taskID", taskID)
    r.addBodyPara("date", date)
    res = r.post()
    return res.text

# 发送定时短信
def sendCronMessage(preUrl,appid, appsecret, mobile, content, tNum, bigMsg,sendTime,funcNo = "28-11"):
    """
    :param mobile: 手机号码，必要
    :param content: string类型，使用json格式对应模板的键值对，动态内容使用,使用UTF-8编码强调下,json中的key和value如果不是数字,则必须用双引号包裹,不要用单引号，非必要
    :param tNum: 短信模板ID，必要
    :param big_msg: 70字符含自定义签名,超过70，请传big_msg=1参数,超过70字符按67个字符算一条短信，最多400个字符，非必要
    :param sendTime：短信发送的时间,必须是当前时间的3小时之后,格式是:yyyyMMddHHmmss，必要
    :return ret_code：0为提交到队列成功，其他失败
    :return remark：描述信息
    :return taskID：任务ID
    """
    url = urljoin(preUrl, funcNo)
    r = ShowapiRequest(url, appid, appsecret)
    r.addBodyPara("mobile", mobile)
    r.addBodyPara("content", content)
    r.addBodyPara("tNum", tNum)
    r.addBodyPara("big_msg", bigMsg)
    r.addBodyPara("sendTime", sendTime)
    res = r.post()
    return res.text

# 修改自定义模板
def modifyTemplates(preUrl,appid,appsecret,content,title,tNum,notiPhone,funcNo = "28-10"):
    """
    :param content: 新模板内容,规则与新建模板一致,不填写表示不修改,非必要
    :param title: 新的签名,不填写表示不修改签名，非必要
    :param tNum: 模板编号，必要
    :param notiPhone: 联系人信息，以便审核模板后通知审核结果，必要
    :return ret_code：应用级参数，0为提交到队列成功，其他失败
    :return remark：描述信息
    """
    url = urljoin(preUrl, funcNo)
    r = ShowapiRequest(url, appid,appsecret)
    r.addBodyPara("content", content)
    r.addBodyPara("title", title)
    r.addBodyPara("tNum", tNum)
    r.addBodyPara("notiPhone", notiPhone)
    res = r.post()
    return res.text

# 删除自定义模板
def deleteTemplates(preUrl,appid,appsecret,tNum,funcNo = "28-9"):
    """
    :param tNum：模板id，必要
    :return ret_code：0成功  其他失败
    :return remark：备注
    """
    url = urljoin(preUrl, funcNo)
    r = ShowapiRequest(url, appid,appsecret)
    r.addBodyPara("tNum", tNum)
    res = r.post()
    return res.text

# 屏蔽关键字查询
def queryIllegalKeyword(preUrl,appid,appsecret,content,funcNo = "28-13"):
    """
    :param content：要检测的短信内容
    :return ret_code：0成功  其他失败
    :return msg：检测结果说明(内容中有多个屏蔽词的时候,只返回最先检测到的屏蔽词)
    :return flag：检测结果是否通过
    """
    url = urljoin(preUrl, funcNo)
    r = ShowapiRequest(url, appid,appsecret)
    r.addBodyPara("content", content)
    res = r.post()
    return res.text

# 短信 语音验证码平台用户登录，获取token
def userLogin(preUrl,userId,pswd,funcNo = "UserLoginStr"):
    """
    :param userId: 注册用户名，必要
    :param pswd: 密码，必要
    :return:token
        异常返回：
            空值：调用接口超时异常
            0：账户处于禁止使用状态
            -1：调用接口失败
            -2：账户信息错误
            -3：用户名或密码错误
            -4：不是普通账户，该帐户不能用于Web Service或HTTP 等API接口模式(如：代理帐户,软件作者，客服，技术员，系统管理员等)
            -30：非绑定IP

    """
    url = urljoin(preUrl, funcNo)
    r = CaptchaRequest(url)
    r.addBodyPara("name",userId)
    r.addBodyPara("psw",pswd)
    res = r.get()
    return res.text

# 获取一个手机号码，号码来自koko科技的虚拟号码
def getPhoneNum(preUrl,token,subjId,cnt,opType,merchId = "0",a1 = "",a2 = "",pk = "",author = "",funcNo = "GetHM2Str"):
    """
    :param token:必要
    :param subjId:项目编号，传入koko科技为毕业之家创建的项目的项目编号，必要
    :param cnt:取号码数量，1~30，必要
    :param opType:运营商类型，0：不限，1：移动，2：联通，3：电信，4：国外，5：虚拟号码，6：非虚拟号码，130~189：指定号段，必要
    :param merchId:卡商ID编号，默认0，必要
    :param a1:省份，非必要
    :param a2:城市，非必要
    :param pk:专属对接key，非必要
    :param author:平台开发作者账户，用于计算提成，非必要
    :return:hm=获取到的号码：成功的返回，截取手机号码
            id=数值：当返回数据包含id=***时，说明服务器繁忙不能即时分配号码，已经生成获取号码任务id用来二次查询获取号码，可在延时5-20秒之后用这个
                任务id调用GetTaskStr接口函数获取分配的号码。
            空值：调用接口超时异常
            0：没登陆或token过期
            -1：当前没有符合条件号码
            -2：提交取号任务超量，请释放占用号码
            -3：获取号码数量超量，请释放已经做完任务不使用的号码，以便获取新号码
            -4：该项目已经被禁用，暂停取号做业务
            -8：帐户余额不足
            -11：端口繁忙被占用，请稍后再试
            -12：该项目不能以获取号码方式工作
            -15：查找不到该专属对应KEY
    """
    url = urljoin(preUrl, funcNo)
    #r = CaptchaRequest("http://dkh.hfsxf.com:81/service.asmx/GetHM2Str")
    r = CaptchaRequest(url)
    r.addBodyPara("token",token)
    r.addBodyPara("xmid",subjId)
    r.addBodyPara("sl",cnt)
    r.addBodyPara("lx",opType)
    r.addBodyPara("a1", a1)
    r.addBodyPara("a2", a2)
    r.addBodyPara("pk", pk)
    r.addBodyPara("ks",merchId)
    r.addBodyPara("rj",author)
    res = r.get()
    return res.text

# 通过任务ID重新获取手机号
def getTaskNo(preUrl,token,taskId,funcNo = "GetTaskStr"):
    """
    :param taskId: 取号时返回的任务ID
    :return 字符长度大于10：获取到的手机号码，多号码时用逗号分隔
            空值：调用接口异常
            1：任务Id还在等待分配号码中，可延时1-30秒后再次调用该任务接口获取号码
            0：没登陆或token过期
            -1：任务已结束或被已被中止或当前没有合条件号码，该任务Id已经失效，可以重新通过GetHMStr接口获取号码
            -11：端口繁忙被占用，请稍后再试
    """
    url = urljoin(preUrl, funcNo)
    r = CaptchaRequest(url)
    r.addBodyPara("token", token)
    r.addBodyPara("id", taskId)
    res = r.get()
    return res.text

# 截获短信，解析验证码
def getCaptcha(preUrl,token,subjId,phoneNo,release = "0",funcNo = "GetYzm2Str"):
    """
    :param subjId: 项目ID
    :param phoneNo: 接收短信验证码的手机号
    :param release: 是否释放手机号，0：继续锁住不释放，1：获取到短信内容时，同时释放不再占用该号码
    :return 字符长度大于4：获取到验证码信息
            空值：接口调用超时异常
            1：卡商还没接收到验证信息，等待返回验证码信息，可延时间隔5-15秒后再次调用该任务接口再次获取验证码短信,直到获取到为止
            0：没登陆或token过期
            -1：该号码已经已经被卡商注销。
            -2：业务已被取消，可重试重新操作语音验证
            -3：业务异常中止
            -8：余额不足扣费
            -9：专属数据出错
    """
    url = urljoin(preUrl, funcNo)
    #r = CaptchaRequest("http://dkh.hfsxf.com:81/service.asmx/GetYzm2Str")
    r = CaptchaRequest(url)
    r.addBodyPara("token", token)
    r.addBodyPara("xmid", subjId)
    r.addBodyPara("hm", phoneNo)
    r.addBodyPara("sf", release)
    res = r.get()
    return res.text

# 释放单个号码
def releaseSingleNo(preUrl,token,phoneNo,funcNo = "sfHmStr"):
    """
    :param phoneNo: 要释放的手机号码
    :return 空值：调用接口超时异常
            1：释放成功
            0：没登陆或token过期
            -1：释放号码失败
    """
    url = urljoin(preUrl, funcNo)
    r = CaptchaRequest(url)
    r.addBodyPara("token", token)
    r.addBodyPara("hm", phoneNo)
    res = r.get()
    return res.text

# 注销释放帐户分配占用的全部号码
def releaseAllNo(preUrl,token,funcNo = "sfAllStr"):
    """
    :return 空值：调用接口超时异常
            1：释放成功
            0：没登陆或token过期
            -1：释放号码失败
    """
    url = urljoin(preUrl, funcNo)
    r = CaptchaRequest(url)
    r.addBodyPara("token", token)
    res = r.get()
    return res.text

def addBlackList(preUrl,token,subjId,phone,release = "0",funcNo = "Hmd2Str"):
    """
    :param subjId: 项目ID
    :param phone: 手机号
    :param release: 是否释放，0表示拖黑后不再做该项目，但可以做其他项目，1表示拖黑后释放号码
    :return 1：增加黑名单成功
            空值：调用接口超时异常
            0：没登陆或失败
            -1：增加失败
            -2：号码黑名单已经存在，不需要重复增加
    """
    url = urljoin(preUrl, funcNo)
    r = CaptchaRequest(url)
    r.addBodyPara("token", token)
    r.addBodyPara("xmid", subjId)
    r.addBodyPara("hm", phone)
    r.addBodyPara("sf", release)
    res = r.get()
    return res.text

# banma语音验证码平台用户登录，获取token
def loginByBanma(userId,pswd,action = "loginIn"):
    """
    :param userId: 注册用户名，必要
    :param pswd: 密码，必要
    :return:1|token
    """
    r = CaptchaRequest("http://to.banma1024.com/api/do.php")
    r.addBodyPara("action", action)
    r.addBodyPara("name",userId)
    r.addBodyPara("password",pswd)
    res = r.get()
    return res.text.split("|")

# 获取手机号
def getPhoneByBanma(subjId,token,action = "getPhone",qx = "1"):
    """
    :return 1|手机号
            0|系统暂时没有可用号码，请过3秒再重新取号
            0|余额不足，当前余额为0.00元，其中使用中的项目锁定0.40元。 存在余额不足的字眼，请停止软件运行
            0|超出频率，请延时3秒再请求
            返回 0| 请软件主动延时3秒再请求，对于没加任何延时的，平台监控到并发高的会封号处理
    """
    r = CaptchaRequest("http://to.banma1024.com/api/do.php")
    r.addBodyPara("action", action)
    r.addBodyPara("sid", subjId)
    r.addBodyPara("token", token)
    r.addBodyPara("qx", qx)
    res = r.get()
    return res.text.split("|")


# 获取验证码
def getMessageByBanma(subjId,phoneNo,token,action = "getMessage"):
    """
    :return 1|短信内容
            0|还没有接收到短信，请过3秒再试，请软件主动3秒再重新取短信内容
            返回 0| 请软件主动延时3秒再请求，对于没加任何延时的，平台监控到并发高的会封号处理
            接收不到短信，拉黑该号码
    """
    r = CaptchaRequest("http://to.banma1024.com/api/do.php")
    r.addBodyPara("action", action)
    r.addBodyPara("sid", subjId)
    r.addBodyPara("phone", phoneNo)
    r.addBodyPara("token", token)
    res = r.get()
    return res.text.split("|")

# 手机号加黑名单
def addBlacklistByBanma(subjId,phoneNo,token,action = "addBlacklist"):
    """
    :return 1|操作成功
            如果是正常取到了短信，是不用操作加入黑名单和释放手机号的
    """
    r = CaptchaRequest("http://to.banma1024.com/api/do.php")
    r.addBodyPara("action", action)
    r.addBodyPara("sid", subjId)
    r.addBodyPara("phone", phoneNo)
    r.addBodyPara("token", token)
    res = r.get()
    return res.text.split("|")

# 释放单个手机号
def releasePhoneNoByBanma(subjId,phoneNo,token,action = "cancelRecv"):
    """
    :return 1|操作成功
            如果是正常取到了短信，是不用操作加入黑名单和释放手机号的
    """
    r = CaptchaRequest("http://to.banma1024.com/api/do.php")
    r.addBodyPara("action", action)
    r.addBodyPara("sid", subjId)
    r.addBodyPara("phone", phoneNo)
    r.addBodyPara("token", token)
    res = r.get()
    return res.text.split("|")

# 释放当前用户下所有手机号
def releaseAllPhoneNoByBanma(token,action = "cancelAllRecv"):
    """
    :return 1|操作成功
            如果是正常取到了短信，是不用操作加入黑名单和释放手机号的
    """
    r = CaptchaRequest("http://to.banma1024.com/api/do.php")
    r.addBodyPara("action", action)
    r.addBodyPara("token", token)
    res = r.get()
    return res.text.split("|")


if __name__ == "__main__":
    APPID = "87178"
    APPSECRET = "c9cac5c2af75460e9474feee07e084bd"
    mobile = "17388290442"
    verCode = genVerCode()
    content = '{"code":"%s","minute":"1"}' % verCode
    tNum = "T170317004100"
    big_msg = ""
    date = "2020-05-13"
    taskID = "2005141439256657783"
    page = ""
    sendTime = "20200514141700"
    #token = "A91CFA1118B7BC7E68A23BE156D22F46"
    subjId = "359701"
    cnt = "1"
    opType = "0"

    #print("短信已发送，短信内容：%s"%verCode)
    #r = sendCronMessage(APPID, APPSECRET, mobile, content, tNum, big_msg,sendTime)
    #r = queryDetails(APPID, APPSECRET,"",page,taskID,"")
    #r = userLogin("zhouliang3181215","zl535785")
    # 通过koko科技获取虚拟手机号码
    #r = getPhoneNum(token,subjId,cnt,opType)  # 17388290442
    #mobile = phoneNo = r[3:]
    #print(mobile)
    # 通过万维易源向目标手机号码发送短信，使用正则表达式解析验证码 ([0-9]{6})
    #r = sendMessage(APPID, APPSECRET, mobile, content, tNum, big_msg)
    #while True:
    #    r = getCaptcha(token,subjId,"16501244539")
    #    print(r)
    #    if r in ("0","-1","-2","-3","-8","-9") or len(r) > 4:
    #        break
    #    print("卡商还没接收到验证信息，继续等待返回验证码信息")
    #    time.sleep(5)
    #r = releaseAllNo(token)
    #print(r)
    subjId = "6649"
    token = "2d85498abf75dfb41c0fbbb723bd647f97554a62"
    import re
    r = getPhoneByBanma(subjId, token, action="getPhone", qx="1")
    print(r)
    phoneNo = r[1]
    #while True:
    #    res = getMessageByBanma(subjId, phoneNo,token)
    #    print(res)
    #    if res[0] == "1":
    #        # 使用正则解析验证码
    #        pattern = re.compile("([0-9]{6})")
    #        mobj = pattern.search(res[1])
    #        veryCode = mobj.group()
    #        break
    #    print("卡商还没接收到验证信息，继续等待返回验证码信息")
    #    time.sleep(5)
    #r = addBlacklistByBanma(subjId, phoneNo, token)
    #print("释放手机号")
    #r  = releasePhoneNoByBanma(subjId, phoneNo, token)
    #print(r)


