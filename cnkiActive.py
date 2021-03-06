# -*- encoding: utf-8 -*-
'''
@File    :   CnkiActive.py
@Contact :   yizhong120110@gmail.com
@Descrip :   模拟登录中国知网并激活账号

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/5/15 11:30   qiuy      1.0         None
'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import requests
import base64
import re
import time, datetime
import os
from PIL import Image
from BaiduOcr import recImage
from ShortMessage import userLogin, getPhoneNum, getCaptcha, getTaskNo, releaseSingleNo, releaseAllNo

KOKOUSERID = "zhouliang333"
KOKOPASSWORD = "535785"
KOKOSUBJID = "56311"
KOKOCNT = "1"
KOKOOPTYPE = "0"
# 获取token
#TOKEN = userLogin(KOKOUSERID, KOKOPASSWORD)


def openCnki():
    login_url = "http://check7.cnki.net/user/"
    driver = webdriver.Chrome()
    driver.set_window_size(1200, 900)
    driver.get(login_url)
    return driver


def login(driver, university, user, password):
    # 选择学校并点击
    universityObj = driver.find_element_by_id("University_xuexiaoTxt")
    universityObj.click()
    time.sleep(1)
    # 抓取学校名称域并填写内容
    schoolName = driver.find_element_by_id("school_name")
    schoolName.send_keys(university)
    time.sleep(1)
    # 点击“检索”按钮
    button = driver.find_element_by_id("LinkButton41")
    button.click()
    time.sleep(1)
    # 点击选中的学校
    bigButton = driver.find_element_by_id("DataList1_ctl00_LinkButton6")
    bigButton.click()
    time.sleep(1)
    # 输入用户名
    userName = driver.find_element_by_id("University_UserName")
    userName.send_keys(user)
    time.sleep(1)

    # 选择身份，默认是“学生”，不需要处理
    # iden = driver.find_element_by_id("University_DDL_Log")
    # iden.send_keys("学生")
    # time.sleep(1)

    while True:
        # 输入密码
        pwd = driver.find_element_by_id("University_UserPwd")
        pwd.send_keys(password)
        time.sleep(1)
        # 输入登录图片验证码
        image = getVerifyImage(driver, "loginPage.png", "loginCode.png", "imgCheckCode")
        if image == False:
            print("登录界面截取验证码失败，重新截取")
            time.sleep(1)
            continue
        # 调用百度OCR识别验证码
        imageDict = recImage(image)
        words_result_num = imageDict.get("words_result_num")
        print(words_result_num)
        if words_result_num > 0:
            print("验证码解析成功")
            words_result = imageDict.get("words_result")[0]
            veriCode = words_result.get("words", "").replace(" ", "")
            # break
        else:
            print("解析失败，点击验证码重新解析")
            photo = driver.find_element_by_id("imgCheckCode")
            photo.click()
            time.sleep(1)
            continue
        # 输入验证码
        captcha = driver.find_element_by_id("University_TextBox_Check")
        # 先清空当前域
        captcha.clear()
        captcha.send_keys(veriCode)
        time.sleep(1)
        # 点击登录按钮
        loginButton = driver.find_element_by_id("d")
        loginButton.click()
        time.sleep(1)
        # 判断是否有弹窗
        alt = EC.alert_is_present()(driver)
        if alt:
            print(alt.text)
            if alt.text == "验证码不正确！":
                print("验证码不匹配，重新输入密码，刷新验证码重新解析")
                alt.accept()
                #photo = driver.find_element_by_id("imgCheckCode")
                #photo.click()
                time.sleep(1)
                continue
            if alt.text == "用户名或者密码错误，请重新输入！":
                print("用户名或者密码错误，任务退出")
                return
        else:
            print("登录验证码匹配成功，继续下一步")
            return True


def getVerifyImage(driver, mainImg, subImg, element):
    print("截取当前页面，绘制验证码图片")
    try:
        # 截取当前页面
        driver.save_screenshot(mainImg)
        # 获取验证码位置，截图起点(x,y)，验证码大小(width,height)
        photo = driver.find_element_by_id(element)
        x = photo.location["x"]
        y = photo.location["y"]
        width = photo.size["width"]
        height = photo.size["height"]
        # 通过pillow裤绘制图片
        im = Image.open(mainImg)
        im = im.crop((x, y, x + width, y + height))
        im.save(subImg)
        print("验证码图片绘制完毕，读取图片内容")
        with open(subImg, "rb") as file:
            return file.read()
    except Exception as e:
        print(e)
        return False


def activeUser(driver):
    # 定位当前页面
    driver.current_window_handle
    while True:
        # 调用koko科技获取手机号码并填充
        time.sleep(1)
        phoneNo = genPhoneNo(KOKOSUBJID, KOKOCNT, KOKOOPTYPE)
        if not phoneNo:
            return None
        txtPhoneNum = driver.find_element_by_id("txtPhoneNum")
        # 清空该域
        txtPhoneNum.clear()
        txtPhoneNum.send_keys(phoneNo)
        time.sleep(1)
        # 有时候在登录保护界面需要输入图片验证码
        # 这里有点问题，应该是进入页面后先判断是否需要输入图片验证码
        txtImgCode = driver.find_element_by_id("txtImgCode")
        # 判断元素是否display
        if txtImgCode.is_displayed():
            print("登录保护界面需要输入图片验证码")
            # 截取页面中的验证码部分
            while True:
                image = getVerifyImage(driver, "loginProtectionPage.png", "loginProtectionCode.png", "imgCheckCode")
                if image == False:
                    print("登录保护界面截取图片验证码失败，重新截取")
                    time.sleep(1)
                    continue
                # 调用百度OCR识别验证码
                imageDict = recImage(image)
                words_result_num = imageDict.get("words_result_num")
                if words_result_num > 0:
                    print("验证码解析成功")
                    words_result = imageDict.get("words_result")[0]
                    veriCode = words_result.get("words", "").replace(" ", "")
                else:
                    print("解析失败，点击验证码重新解析")
                    #photo = driver.find_element_by_id("imgCheckCode")
                    #photo.click()
                    time.sleep(1)
                    continue
                # 输入图片验证码
                captcha = driver.find_element_by_id("txtImgCode")
                # 先清空当前域
                captcha.clear()
                captcha.send_keys(veriCode)
                time.sleep(1)
                # 点击获取短信验证码按钮
                btnCode = driver.find_element_by_id("btnCode")
                btnCode.click()
                print("[%s]点击获取短信验证码按钮" % (datetime.datetime.now().strftime("%Y-%m-%d:%H:%M:%S.%f")))
                time.sleep(1)

                # 判断是否有弹窗
                alt = EC.alert_is_present()(driver)
                if alt:
                    print(alt.text)
                    if alt.text[:4] == "发送成功":
                        print("短信验证码发送成功")
                        alt.accept()
                        # 调用koko科技监听短信，并解析短信验证码
                        veryCode = parseVerifyCode(phoneNo)
                        # 60秒内未获取到验证码，退出
                        if not veryCode:
                            return None
                        txtMobileCode = driver.find_element_by_id("txtMobileCode")
                        txtMobileCode.send_keys(veryCode)
                        time.sleep(1)
                        btnCheck = driver.find_element_by_id("btnCheck")
                        btnCheck.click()
                        return phoneNo
                    if alt.text == "验证码不正确！":
                        print("验证码不匹配，刷新验证码重新解析")
                        alt.accept()
                        photo = driver.find_element_by_id("imgCheckCode")
                        photo.click()
                        time.sleep(1)
                        continue
                    if alt.text == "该手机号码已被绑定，如确有需要，请联系学校管理员修改本账号关联的手机号码！":
                        print("手机号码[%s]已绑定其他知网用户，释放该号码，更换手机号重新激活" % phoneNo)
                        releaseSingleNo(TOKEN, phoneNo)
                        alt.accept()
                        # 释放该号码

                        break
                else:
                    print("没有弹窗，登录保护图片验证码匹配成功，继续下一步")
                    # 调用koko科技监听短信，并解析短信验证码
                    veryCode = parseVerifyCode(phoneNo)
                    # 60秒内未获取到验证码，退出
                    if not veryCode:
                        return None
                    txtMobileCode = driver.find_element_by_id("txtMobileCode")
                    txtMobileCode.send_keys(veryCode)
                    time.sleep(1)
                    btnCheck = driver.find_element_by_id("btnCheck")
                    btnCheck.click()
                    return phoneNo

            continue
        else:
            print("登录保护界面不需要输入图片验证码，进行短信验证码验证")
            # 点击获取短信验证码按钮
            btnCode = driver.find_element_by_id("btnCode")
            btnCode.click()
            print("[%s]点击获取短信验证码按钮" % (datetime.datetime.now().strftime("%Y-%m-%d:%H:%M:%S.%f")))
            time.sleep(1)
            # 判断是否有弹窗
            alt = EC.alert_is_present()(driver)
            if alt:
                print(alt.text)
                if alt.text == "该手机号码已被绑定，如确有需要，请联系学校管理员修改本账号关联的手机号码！":
                    print("手机号码[%s]已绑定其他知网用户，释放该号码，更换手机号重新激活" % phoneNo)
                    releaseSingleNo(TOKEN, phoneNo)
                    alt.accept()
                    continue
            else:
                print("没有弹窗，获取的手机号码有效，监听短信验证码并输入")
                # 调用koko科技监听短信，并解析短信验证码
                veryCode = parseVerifyCode(phoneNo)
                # 60秒内未获取到验证码，退出
                if not veryCode:
                    return None
                txtMobileCode = driver.find_element_by_id("txtMobileCode")
                txtMobileCode.send_keys(veryCode)
                time.sleep(1)
                btnCheck = driver.find_element_by_id("btnCheck")
                btnCheck.click()
                return phoneNo


def genPhoneNo(subjId, cnt, opType):
    # 获取token
    r = getPhoneNum(TOKEN, subjId, cnt, opType)
    print("获取到的手机号信息：%s" % r)
    if len(r[3:]) > 1 and len(r[3:]) < 10:
        print("获取手机号码有误，递归调用，重新获取")
        return genPhoneNo(subjId, cnt, opType)
    if len(r[3:]) < 11:
        if r in ("-3", "-8"):
            print("获取手机号失败，任务结束，继续下一个任务")
            return None
        print("获取到的是生成手机号的任务ID，等待5秒后调用getTaskNo获取手机号")
        while True:
            taskId = r[3:]
            print(taskId)
            time.sleep(5)
            res = getTaskNo(TOKEN, taskId)
            if res == "1":
                continue
            if len(res) > 8:
                phoneNo = res
                break
    else:
        phoneNo = r[3:]
    return phoneNo


# 修改密码
def modifyPwd(driver, oldPwd, newPwd):
    # 定位当前页面
    driver.current_window_handle
    oldPwdTxt = driver.find_element_by_id("oldPwdTxt")
    oldPwdTxt.send_keys(oldPwd)
    time.sleep(1)
    newPwdTxt = driver.find_element_by_id("newPwdTxt")
    newPwdTxt.send_keys(newPwd)
    time.sleep(1)
    againnewPwdTxt = driver.find_element_by_id("againnewPwdTxt")
    againnewPwdTxt.send_keys(newPwd)
    time.sleep(1)
    changeImgBtn = driver.find_element_by_id("changeImgBtn")
    changeImgBtn.click()
    time.sleep(1)
    driver.quit()


def parseVerifyCode(phoneNo):
    print("[%s]监听号码[%s]，解析验证码" % (datetime.datetime.now().strftime("%Y-%m-%d:%H:%M:%S.%f"), phoneNo))
    ct_begin = time.time()
    while True:
        res = getCaptcha(TOKEN, KOKOSUBJID, phoneNo, "1")
        print(res)
        if res in ("0", "-1", "-2", "-3", "-8", "-9") or len(res) > 4:
            if len(res) > 4:
                # 使用正则解析验证码
                pattern = re.compile("([0-9]{6})")
                mobj = pattern.search(res)
                veryCode = mobj.group()
            break
        print("卡商还没接收到验证信息，继续等待返回验证码信息")
        time.sleep(5)
        ct_end = time.time()
        if ct_end - ct_begin > 60:
            print("60秒内未获取到验证码，该账号的自动激活即将退出，处理下一个任务")
            # 释放号码
            releaseSingleNo(TOKEN, phoneNo)
            return None
    return veryCode


def timing(func):
    def wrapper():
        print("[%s]开始执行[%s]" % (datetime.datetime.now().strftime("%Y-%m-%d:%H:%M:%S.%f"), func.__name__))
        return func()

    return wrapper


if __name__ == "__main__":
    for root, dir, files in os.walk("cnki"):
        for file in files:
            begin = datetime.datetime.now()
            print("[%s] 正在处理文件[%s]" % (begin.strftime("%Y-%m-%d %H:%M:%S"), file))
            filePath = os.path.join(root, file)
            university = os.path.splitext(file)[0]
            with open(filePath) as fileObj:
                fileContent = fileObj.read()
            succStdList = []
            errStdList = []
            succFile = os.path.join("newCnki", "SUCC_" + file)
            errFile = os.path.join("newCnki", "ERR_" + file)
            cnt = 0
            for stdNo in fileContent.split("\n"):
                print("获取本地存储的token")
                with open("token.txt","r") as fileObj:
                    TOKEN = fileObj.read()
                cnt += 1
                try:
                    # 打开浏览器，进入登录页面
                    print("正在激活用户[%s]" % stdNo)
                    ct1 = time.time()
                    driver = openCnki()
                    time.sleep(1)
                    user = stdNo.strip()
                    password = "a123456"
                    newPwd = "123456a"
                    # 完成登录操作：选择学校-输入用户名-输入密码-解析验证码并输入-点击登录按钮
                    res = login(driver, university, user, password)
                    if not res:
                        print("用户[%s]自动激活失败，继续下一个任务" % stdNo)
                        with open(errFile, 'a') as fileObj:
                            fileObj.write(user + '\n')
                        time.sleep(1)
                        driver.quit()
                        continue
                    # 登录保护
                    phoneNo = activeUser(driver)
                    if not phoneNo:
                        print("用户[%s]自动激活超时，继续下一个任务" % stdNo)
                        with open(errFile, 'a') as fileObj:
                            fileObj.write(user + '\n')
                        time.sleep(1)
                        driver.quit()
                        continue
                    time.sleep(2)
                    # 修改密码
                    modifyPwd(driver, password, newPwd)
                    # 释放手机号
                    releaseAllNo(TOKEN)
                    ct2 = time.time()
                    print("用户[%s]密码已修改，绑定的手机号码为[%s]，用时[%s]秒" % (user, phoneNo, int(ct2 - ct1)))
                    with open(succFile, 'a') as fileObj:
                        fileObj.write("\t".join([user, phoneNo]) + "\n")

                except  Exception as e:
                    print(e)
                    print("用户[%s]自动激活失败，继续下一个任务" % stdNo)
                    with open(errFile, 'a') as fileObj:
                        fileObj.write(user + '\n')
                    driver.quit()
            end = datetime.datetime.now()
            interval = (end - begin).seconds
            print("[%s] 文件[%s]处理完成，共计处理[%d]用户，共计耗时[%s]秒" % (end.strftime("%Y-%m-%d %H:%M:%S"), file, cnt, interval))
            time.sleep(3)