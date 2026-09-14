#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import base64
import math
import json
import urllib
from urllib import request, parse
import urllib.request
import re
# import ssl
class Spider(Spider):
	hostUrl='https://www.yinhuadm.cc'
	def getName(self):
		return "樱花动漫"
	def init(self,extend=""):
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		result = {}
		cateManual = {
			"国产动漫": "9",
			"日本动漫": "10",
			"欧美动漫": "11",
			"新片上线":"new",
			"热门动漫":"hot",
			"全部": "1"
		}
		classes = []
		for k in cateManual:
			classes.append({
				'type_name': k,
				'type_id': cateManual[k]
			})

		result['class'] = classes
		if (filter):
			result['filters'] = self.config['filter']
		return result
	def homeVideoContent(self):
		htmlTxt = self.custom_webReadFile(urlStr=self.hostUrl)
		root = self.html(htmlTxt)
		temporary=root.xpath('//a[@class="module-poster-item module-item"]')
		videos = self.get_list(aTerm=temporary)
		result = {
			'list': videos
		}
		return result

	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		if len(tid)==3:
			patternTxt=r'//a[@class="module-card-item-poster"]'
		else:
			patternTxt=r'//a[@class="module-poster-item module-item"]'
		if len(tid)==3:
			url = self.hostUrl+'/label/{0}.html'.format(tid)
		else:
			url = self.hostUrl+'/w/{0}/page/{1}.html'.format(tid,pg)
		htmlTxt = self.custom_webReadFile(urlStr=url)
		root = self.html(htmlTxt)
		temporary=root.xpath(patternTxt)
		videos = self.get_list(aTerm=temporary)
		pag=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'<a href="/w/\d+?/page/(\d+?)\.html" class="page-link page-next" title="尾页">尾页</a>',Index=1)
		if pag=="":
			pag=999

		numvL = len(videos)
		result['list'] = videos
		result['page'] = pg
		result['pagecount'] = pag
		result['limit'] = numvL
		result['total'] = numvL
		return result

	def detailContent(self,array):
		aid = array[0].split('###')
		idUrl=aid[1]
		title=aid[0]
		pic=aid[2]
		htmlTxt =  self.custom_webReadFile(urlStr=idUrl,codeName='utf-8')
		# htmlTxt=self.readFile(filePath=r'D:\1.txt')
		
		line=self.get_RegexGetTextLine(Text=htmlTxt,RegexText=r'<div class="module-tab-item tab-item" data-dropdown-value="(.{3,10})">\s*\r*\n*\t*\s*<span>(.{3,10})</span><small>\d+?</small>',Index=1)
		
		if len(line)<1:
			return  {'list': []}
		playFrom = []
		videoList=[]
		vodItems = []
		circuit=self.custom_lineList(Txt=htmlTxt,mark=r'<div class="module-play-list-content',after='</div>')
		playFrom=[t[1] for t in line]
		pattern = re.compile(r'<a class="module-play-list-link" href="(.+?)" title=".+?"><span>(.+?)</span></a>')
		for v in circuit:
			ListRe=pattern.findall(v)
			vodItems = []
			for value in ListRe:
				vodItems.append(value[1]+"$"+value[0])
			joinStr = "#".join(vodItems)
			videoList.append(joinStr)

		vod_play_from='$$$'.join(playFrom)
		vod_play_url = "$$$".join(videoList)
		typeName=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'<a href="/w/9/class/.+?.html">(.+?)</a><span class="slash">',Index=1)
		year=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'<a title="(\d{4})" href="/w/9/year/\d{4}.html">',Index=1)
		area=typeName
		act=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'<a href="/vch/actor/.+?.html" target="_blank">(.+?)</a>',Index=1)
		dir=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'<a href="/vch/director/.+?.html" target="_blank">(.+?)</a><span class="slash">',Index=1)
		cont=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'<div class="module-info-introduction-content">(\s*\r*\n*\t*\s*.+?\s*\r*\n*\t*\s*)</div>',Index=1)
		vod = {
			"vod_id": array[0],
			"vod_name": title,
			"vod_pic": pic,
			"type_name":self.removeHtml(txt=typeName),
			"vod_year": self.removeHtml(txt=year),
			"vod_area": area,
			"vod_remarks": '',
			"vod_actor":  self.removeHtml(txt=act),
			"vod_director": self.removeHtml(txt=dir),
			"vod_content": self.removeHtml(txt=cont)
		}
		vod['vod_play_from'] = vod_play_from
		vod['vod_play_url'] = vod_play_url

		result = {
			'list': [
				vod
			]
		}
		return result

	# def verifyCode(self):
	# 	pass
	searchpage=1
	def searchContent(self,key,quick,pg='1'):
		if int(pg)>self.searchpage:
			return {'list':[]}
		Url='{1}/vch/{0}/page/{2}.html'.format(urllib.parse.quote(key),self.hostUrl,pg)
		htmlTxt = self.custom_webReadFile(urlStr=Url,codeName='utf-8')
		root = self.html(htmlTxt)
		temporary=root.xpath('//a[@class="module-card-item-poster"]')
		videos = self.get_list(aTerm=temporary)
		result = {
				'list': videos
			}
		return result

	def playerContent(self,flag,id,vipFlags):
		result = {}
		parse=1
		Url='{1}{0}'.format(id,self.hostUrl)	
		result["parse"] = parse
		result["playUrl"] = ''
		result["url"] = Url
		result["header"] = self.header
		return result

	config = {
		"player": {},
		"filter": {}
	}
	header = {
		 "User-Agent": 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
	}

	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]
	#-----------------------------------------------自定义函数-----------------------------------------------
	def custom_RegexGetText(self,Text,RegexText,Index):
		returnTxt=""
		Regex=re.search(RegexText, Text, re.M|re.I)
		if Regex is None:
			returnTxt=""
		else:
			returnTxt=Regex.group(Index)
		return returnTxt	
	def get_RegexGetTextLine(self,Text,RegexText,Index):
		returnTxt=[]
		pattern = re.compile(RegexText)
		ListRe=pattern.findall(Text)
		if len(ListRe)<1:
			return returnTxt
		for value in ListRe:
			returnTxt.append(value)	
		return returnTxt
	def get_playlist(self,Text,headStr,endStr):
		circuit=""
		origin=Text.find(headStr)
		if origin>8:
			end=Text.find(endStr,origin)
			circuit=Text[origin:end]
		return circuit
	def removeHtml(self,txt):
		soup = re.compile(r'<[^>]+>',re.S)
		txt =soup.sub('', txt)
		return txt.replace("&nbsp;"," ")
	def custom_webReadFile(self,urlStr,header=None,codeName='utf-8'):
		html=''
		if header==None:
			header={
				"Referer":urlStr,
				'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36',
				"Host":self.custom_RegexGetText(Text=urlStr,RegexText='https*://(.*?)(/|$)',Index=1)
			}
		# ssl._create_default_https_context = ssl._create_unverified_context#全局取消证书验证
		req=urllib.request.Request(url=urlStr,headers=header)#,headers=header
		with  urllib.request.urlopen(req)  as response:
			html = response.read().decode(codeName)
		return html
	def get_list(self,aTerm):
		videos = []
		for a in aTerm:
			try:
				title=a.xpath('./div/div[@class="module-item-pic"]/img/@alt')[0]
				img=a.xpath('./div/div[@class="module-item-pic"]/img/@data-original')[0]
				url=a.xpath("./@href")[0]
				if url.find('://')<1:
					url=self.hostUrl+url
				if img.find('://')<1:
					img=self.hostUrl+img
				vod_id="{0}###{1}###{2}".format(title,url,img)
				videos.append({
					"vod_id":vod_id,
					"vod_name":title,
					"vod_pic":img,
					"vod_remarks":''
				})
			except:
				# print(a.xpath("./@href")[0])
				pass
		return videos
	def custom_lineList(self,Txt,mark,after):
		circuit=[]
		origin=Txt.find(mark)
		while origin>8:
			end=Txt.find(after,origin)
			circuit.append(Txt[origin:end])
			origin=Txt.find(mark,end)
		return circuit
	# def html(self,html):
	# 	from lxml import etree
	# 	root=etree.HTML(html)
	# 	return root
# T=Spider()
# l=T.searchContent(key='柯南',quick='',pg='1')
# l=T.homeVideoContent()
# l=T.categoryContent(tid='1',pg='1',filter=False,extend='')
# for x in l['list']:
# 	print(x['vod_id'])
# mubiao= l['list'][0]['vod_id']
# print(mubiao)
# playTabulation=T.detailContent(array=[mubiao,])
# vod_play_from=playTabulation['list'][0]['vod_play_from']
# vod_play_url=playTabulation['list'][0]['vod_play_url']
# print(vod_play_url)
# url=vod_play_url.split('$$$')
# vod_play_from=vod_play_from.split('$$$')[0]
# print(url[0])
# url=url[0].split('$')
# url=url[1].split('#')[0]
# print(url)
# m3u8=T.playerContent(flag='',id='/p/21946-1-1.html',vipFlags=True)
# print(m3u8)