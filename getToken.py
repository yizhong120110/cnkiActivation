# -*- encoding: utf-8 -*-
'''
@File    :   getToken.py    
@Contact :   yizhong120110@gmail.com
@Descrip :   定时获取Token

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/5/18 18:45   qiuy      1.0         None
'''
from ShortMessage import userLogin
import time

USERID = "zhouliang333"
PASSWORD = "535785"


if __name__ == "__main__":
    while True:
        token = userLogin(USERID,PASSWORD)
        print(token)
        if token in ("0","-1","-2","-3","-4","-30"):
            print("获取token失败")
            break
        with open("token.txt","w") as fileObj:
            fileObj.write(token)
        time.sleep(3600)