# -*- encoding: utf-8 -*-
'''
@File    :   BaiduOcr.py    
@Contact :   yizhong120110@gmail.com
@Descrip :   调用百度云OCR识别验证码

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/5/15 16:18   qiuy      1.0         None
'''

from aip import AipOcr

# 百度OCR_APP_ID
APP_ID = '16967045'
# 百度OCR_API_KEY
API_KEY = 'wf1OYxYICG6XPbUdhSjhetzQ'
# 百度OCR_SECRET_KEY
SECRET_KEY = 'iAo0V5MshEPzGZ6qeeXqaWAdB7RVoOhd '

# 读取图片
def getFileContent(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

# 识别图片
def recImage(image):
    result = []
    # 调用baidu-aip开始识别图片
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    options = {}
    options["language_type"] = "CHN_ENG"
    options["detect_direction"] = "true"
    options["detect_language"] = "true"
    options["probability"] = "true"
    imageInof = client.basicAccurate(image, options)
    return imageInof

if __name__ == "__main__":
    #image = getFileContent("verify.png")
    image = getFileContent("nonId2.png")
    imageDict = recImage(image)
    words_result_num = imageDict.get("words_result_num"  )
    if words_result_num > 0:
        print("解析成功")
        words_result = imageDict.get("words_result")[0]
        print(words_result)
