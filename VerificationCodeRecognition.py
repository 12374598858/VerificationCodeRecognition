from PIL import Image
from aip import AipOcr, AipImageClassify
import requests
import ssl
from urllib import request
import re


if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context
headers = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36"

'''
获取12306的验证码图片并保存
'''
def get_org_img():
	pic_url = "https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=login&rand=sjrand&0.21191171556711197"
	resp = request.urlopen(pic_url)
	raw = resp.read()
	with open("./tmp.jpg", 'wb') as fp:
		fp.write(raw)

'''
利用百度ocr识别图片内容(比如这是花还是树这类)
'''
def baidu_img_realize(filepath):
	APP_ID ='15286086'  
	API_KEY ='XQGvq71U1KFCWmjbmiIop0Gf'  
	SECRET_KEY ='GpMt0AgUWqT1TG6BWWmPYRPIuoD1FCuD '
	aipimg = AipImageClassify(APP_ID, API_KEY, SECRET_KEY)
	options = {}
	image = get_file_content(filepath)
	aipimg.advancedGeneral(image)
	result = aipimg.advancedGeneral(image, options)
	return result

'''
获取图片内容
'''
def get_file_content(filePath):  
	with open(filePath,'rb') as fp: 
		return fp.read() 

'''
截取问题图片
'''
def make_question_img():
	
	img = Image.open("tmp.jpg");
	cut_img = img.crop((120, 0, 190, 28))
	cut_img.save(r'new_img.jpg')
	filePath ="new_img.jpg" 
	return filePath

'''
截取答案图片
识别答案图片内容
对比问题，输出结果像素位置
'''
def make_answer_img(question):
	img = Image.open("tmp.jpg");
	w, h = img.size
	code = []
	for x in range(2):
		for y in range(4):
			left = int(0.25 * y * w)
			top = int((0.2 + (0.4 * x)) * h)
			right = int(0.25 * (y + 1) * w)
			buttom = int((0.2 + (0.4 * (x + 1))) * h )
			cut_img = img.crop((left, top, right, buttom))
			print(left, top)
			filepath = '{}-{}.jpg'.format(x,y)
			cut_img.save(filepath)
			result = baidu_img_realize(filepath)
#			print(result)
			for list in result['result']:
				for item in question:
					if item in list['keyword']:
#						print('{}-{},ok'.format(x,y))
						code.append(int((left+right)/2))
						code.append(int((top+buttom)/2))
						break
	return code

'''
利用百度ocr识别图片中的文字获取验证问题
'''
def baidu_img_tostring(filePath):
	APP_ID ='15283829'  
	API_KEY ='Qm1aV5830r5ZMn7T1joucuPN'  
	SECRET_KEY ='GCvUxaNLfYR6AG69GSVM2L4fVeuR401j'
	aipOcr = AipOcr(APP_ID, API_KEY, SECRET_KEY)
	options = {  
	'detect_direction': 'true',  
	'language_type': 'CHN_ENG',  
	}
	result = aipOcr.basicGeneral(get_file_content(filePath), options) 
	question = result['words_result'][0]['words']
	return question
	

'''
提交验证码结果
'''
def check_captcha(code):
	url = 'https://kyfw.12306.cn/passport/captcha/captcha-check'
	data = {
		'answer':code,
		'login_site':'E',
		'rand':'sjrand'
	}
#	response = requests.post(url, headers=headers, data=data)
	
	print('ok')

if __name__ == '__main__':
	get_org_img()
	filePath = make_question_img()
	print(filePath)
	question = baidu_img_tostring(filePath)
	print(question)
	code = make_answer_img(question)
	print(code)
	check_captcha(code)


