#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import re
from urllib import request, parse
import urllib
import urllib.request
import json
from lxml import etree
import base64
import ssl
ssl._create_default_https_context = ssl._create_unverified_context#全局取消证书验证
import requests
class Spider(Spider):  # 元类 默认的元类 type
	def getName():
		return "策驰影视"
	def init(self,extend=""):
		print("============{0}============".format(extend))
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		result = {}
		cateManual = {
			"电影": "dianying",
			"电视剧":"dianshiju",
			"动漫":"dongmna",
			"综艺":"zongyi",
			"纪录片":"jilupian"
		}
		classes = []
		for k in cateManual:
			classes.append({
				'type_name':k,
				'type_id':cateManual[k]
			})
		result['class'] = classes
		if(filter):
			result['filters'] = self.config['filter']
		return result
	def homeVideoContent(self):
		req=requests.get('https://cechtv.com/')
		htmlTxt =req.text
		root = self.html(htmlTxt)
		nodes = root.xpath('//a[@class="stui-vodlist__thumb lazyload"]')
		videos = self.custom_list_search(liList=nodes)
		result = {
			'list':videos
		}
		return result
	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		videos=[]
		Url='https://www.cechtv.com/cctv/{0}/page/{1}.html'.format(tid,pg)
		req=requests.get(Url)
		htmlTxt =req.text
		root = self.html(htmlTxt)
		nodes = root.xpath("//a[@class='stui-vodlist__thumb lazyload']")		
		videos = self.custom_list_search(liList=nodes)
		pagecount=0 if len(videos)<30 else int(pg)+1
		result['list'] = videos
		result['page'] = pg
		result['pagecount'] =pagecount
		result['limit'] = 90
		result['total'] = 999999
		return result
	def detailContent(self,array):
		aid = array[0].split('###')
		idUrl=aid[1]
		title=aid[0]
		pic=aid[2]
		playFrom = []
		req=requests.get(idUrl)
		htmlTxt =req.text
		root = self.html(htmlTxt)
		nodes = root.xpath('//div[@class="stui-pannel-box b playlist mb"]/div[@class="stui-pannel_hd"]/div[@class="stui-pannel__head bottom-line active clearfix"]/h3[@class="title"]')
		if len(nodes)<1:
			return  {'list': []}
		playFrom=[v.xpath('./text()')[0] for v in nodes ]
		videoList=[]
		vodItems = []
		circuit=root.xpath('//ul[@class="stui-content__playlist clearfix"]')
		if len(nodes)<1:
			return  {'list': []}
		for v in circuit:
			vodItems=self.custom_EpisodesList(nodes=v)
			joinStr = "#".join(vodItems)
			videoList.append(joinStr)
		vod_play_from='$$$'.join(playFrom)
		vod_play_url = "$$$".join(videoList)
		typeName=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'类型：(.+?)地区：',Index=1)
		year=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'<span class="text-muted hidden-xs">年份：</span>(.+?)<',Index=1)
		area=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'<span class="text-muted hidden-xs">地区：</span>(.+?)<',Index=1)
		remarks=''
		act=''
		dir=''
		cont=''
		try:
			temporary= root.xpath('//p[1][@class="data"]/a/text()')
			if len(temporary)>0:
				act='/'.join(temporary)
			temporary=root.xpath('//p[2][@class="data"]/a/text()')
			if len(temporary)>0:
				dir='/'.join(temporary)
			temporary=root.xpath('//span[@class="detail-sketch"]/text()')
			if len(temporary)>1:
				cont=temporary[1]
		except Exception as e:
			raise e
		vod = {
			"vod_id": array[0],
			"vod_name": title,
			"vod_pic": pic,
			"type_name":self.custom_removeHtml(txt=typeName),
			"vod_year": self.custom_removeHtml(txt=year),
			"vod_area": area,
			"vod_remarks": remarks,
			"vod_actor":  self.custom_removeHtml(txt=act),
			"vod_director": self.custom_removeHtml(txt=dir),
			"vod_content": self.custom_removeHtml(txt=cont)
		}
		vod['vod_play_from'] = vod_play_from
		vod['vod_play_url'] = vod_play_url

		result = {
			'list': [
				vod
			]
		}
		return result

	def searchContent(self,key,quick):
		key=urllib.parse.quote(key)
		Url='https://www.cechtv.com/ccso.html?wd={0}&submit='.format(key)
		htmlTxt=self.custom_webReadFile(urlStr=Url)
		root = self.html(htmlTxt)
		nodes = root.xpath('//a[@class="v-thumb stui-vodlist__thumb lazyload"]')
		videos = self.custom_list_search(liList=nodes)
		result = {
			'list':videos
		}
		return result
	def playerContent(self,flag,id,vipFlags):
		result = {}
		Url=id
		parse=1
		req=requests.get(Url)
		htmlTxt =req.text
		temporary=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'player_aaaa=(.+?)</script>',Index=1)
		if temporary!='':
			jRoot=json.loads(temporary)
			Url=jRoot['url']
			if len(Url)<5:
				Url=id		
			else:
				parse=0
				Url=base64.b64decode(Url).decode('utf-8')
				Url=urllib.parse.unquote(Url)
				if Url.find('m3u8')<3:
					Url=id
					parse=1
		result["parse"] = parse#0=直接播放、1=嗅探
		result["playUrl"] =''
		result["url"] = Url
		# result['jx'] = jx#VIP解析,0=不解析、1=解析
		result["header"] = ''	
		return result
	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]

	config = {
		"player": {},
		"filter": {}
		}
	header = {
		"Referer": 'http://www.884707.com/',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36',
		"Host":'www.884707.com'
		}
	#-----------------------------------------------自定义函数-----------------------------------------------
		#正则取文本
	def custom_RegexGetText(self,Text,RegexText,Index):
		returnTxt=""
		Regex=re.search(RegexText, Text, re.M|re.S)
		if Regex is None:
			returnTxt=""
		else:
			returnTxt=Regex.group(Index)
		return returnTxt	
	
	#分类取结果
	def custom_list_search(self,liList):
		videos = []
		head="https://www.cechtv.com"
		for v in liList:
			title=v.xpath('./@title')[0]
			img=v.xpath('./@data-original')[0]
			url=v.xpath("./@href")[0]
			remarks=v.xpath('./span[@class="pic-text text-right"]/text()')[0]
			if url.find('://')<1:
				url=head+url
			if img.find('://')<1:
				img=head+img
			vod_id="{0}###{1}###{2}".format(title,url,img)
			if self.ifSkip(classText=vod_id)==True:
				continue
			videos.append({
				"vod_id":vod_id,
				"vod_name":title,
				"vod_pic":img,
				"vod_remarks":remarks
			})
		return videos
	
		#访问网页
	def custom_webReadFile(self,urlStr,header=None,codeName='utf-8'):
		html=''
		if header==None:
			header={
				"Referer":urlStr,
				'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36',
				"Host":self.custom_RegexGetText(Text=urlStr,RegexText='https*://(.*?)(/|$)',Index=1),
				'cookie':''
			}
		req=requests.get(urlStr)
		cookie=req.headers.get("Set-Cookie")
		if cookie=='':
			return ''
		header['cookie']=self.custom_RegexGetText(Text=cookie,RegexText='^(.*?;)',Index=1)
		req=requests.get(urlStr,header)
		html =req.text
		return html
	#取集数
	def custom_EpisodesList(self,nodes):
		videos = []
		ListLi=nodes.xpath('.//a')
		for vod in ListLi:
			title =vod.xpath("./text()")[0]
			url = vod.xpath("./@href")[0]
			if len(url) == 0:
				continue
			videos.append(title+"$"+url)
		# print('共:'+str(len(videos)))
		return videos
	#取剧集区
	def custom_lineList(self,Txt,mark,after):
		circuit=[]
		origin=Txt.find(mark)
		while origin>8:
			end=Txt.find(after,origin)
			circuit.append(Txt[origin:end])
			origin=Txt.find(mark,end)
		return circuit	
	#正则取文本,返回数组	
	def custom_RegexGetTextLine(self,Text,RegexText,Index):
		returnTxt=[]
		pattern = re.compile(RegexText, re.M|re.S)
		ListRe=pattern.findall(Text)
		if len(ListRe)<1:
			return returnTxt
		for value in ListRe:
			returnTxt.append(value)	
		return returnTxt
	def custom_mid(self,txt,startStr,endStr):
		start=txt.find(startStr)
		end=txt.find(endStr,start)
		if start<0 or end>len(txt) or end<start:
			return ''
		str=txt[start+len(startStr):end]
		return str
	#删除html标签
	def custom_removeHtml(self,txt):
		soup = re.compile(r'<[^>]+>',re.S)
		txt =soup.sub('', txt)
		return txt.replace("&nbsp;"," ")
	def custom_list_xpath(self,liList):
		videos = []
		head="https://www.fmeiju.com"
		for vod in liList:
			a=vod.xpath('./a[@class="link"]')
			for v in a:
				title=v.xpath('./@title')[0]
				img=v.xpath('./div[@class="pic"]/div[@class="img"]/img/@data-original')[0]
				url=v.xpath("./@href")[0]
				# renew=v.xpath('./div[@class="pic"]/div[@class="info"]/p[@class="zt"]')[0].text
				videos.append({
					"vod_id":"{0}###{1}###{2}".format(title,head+url,head+img),
					"vod_name":title,
					"vod_pic":img,
					"vod_remarks":''
				})
		return [i for n, i in enumerate(videos) if i not in videos[:n]]
	FilterWords=urllib.parse.unquote('%28%E4%BC%A6%E7%90%86%7C%E5%80%AB%E7%90%86%7C%E7%A6%8F%E5%88%A9%7C%E5%BC%BA%E5%A5%B8%29')
	def ifSkip(self,classText):
		b=True if self.custom_RegexGetText(Text=classText,RegexText=self.FilterWords,Index=1)!='' else False
		return b
