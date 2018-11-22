# coding:utf-8
import requests
import time
import MySQLdb
import MySQLdb.cursors
from lxml import etree
from urllib import parse

name_url = "https://www.guazi.com/gz/buy/"
start_url = ["https://www.guazi.com/gz/buy/"]
filter_url = []
header = {
	'Host':'www.guazi.com',
	#'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
	'Accept-Encoding':'gzip, deflate, br',
	'Cookie':'antipas=094703B749B567s35A20579Y709c;', 
	#'Cookie':'antipas=5762035O8S689054651568416;',
}

session = requests.Session()

def start_request(url):
	response = session.get(url=url,headers=header)
	response.encoding = 'utf-8'
	text = response.text
	return text

def get_request(url):
	for j in url:
		if j in filter_url:
			pass
		else:
			filter_url.append(j)
			text = start_request(j)
			return text

def select_url(text):
	html = etree.HTML(text,etree.HTMLParser())
	next_nodes = html.xpath('//ul[contains(@class,"carlist")]//a[@class="car-a"]/@href')
	next_one = html.xpath('//div[@class="pageBox"]//a[@class="next"]/@href')
	for t in next_one:
		next_one = parse.urljoin(name_url,t)
		start_url.append(next_one)
	for next_node in next_nodes:
		next_url = parse.urljoin(name_url,next_node)
		yield next_url
	

def parse_detail(do_url):
	for i in do_url:
		time.sleep(3)
		text = start_request(i)
		html = etree.HTML(text,etree.HTMLParser())
		data = {}
		data['title'] = html.xpath("//h2[@class='titlebox']/text()")[0]
		data['register_time'] = html.xpath("//ul[contains(@class,'assort')]/li[@class='one']/span/text()")[0]
		data['miles'] = html.xpath("//ul[contains(@class,'assort')]/li[@class='two']/span/text()")[0]
		data['city'] = html.xpath("//ul[contains(@class,'assort')]/li[@class='three'][1]/span/text()")[0]
		data['oil_mount'] = html.xpath("//ul[contains(@class,'assort')]/li[@class='three'][2]/span/text()")[0]
		data['speed_box'] = html.xpath("//ul[contains(@class,'assort')]/li[@class='last']/span/text()")[0]
		data['price'] = html.xpath("//div[contains(@class,'pricebox')]/span[@class='pricestype']/text()")[0]

		yield data

def data_clean(datas):
	for data in datas:
		data['title'] = data['title'].strip()
		data['price'] = data['price'].strip() + '万'
		yield data

def insert_into_sql(data):
	conn = MySQLdb.connect('localhost','root','9901914846','guazi',charset='utf8',use_unicode=True)
	cursor = conn.cursor()
	insert_sql = """
		insert into guazi_data(title,register_time,miles,city,oil_mount,speed_box,price)
		VALUES(%s,%s,%s,%s,%s,%s,%s)
	"""
	params = (data['title'],data['register_time'],data['miles'],data['city'],data['oil_mount'],data['speed_box'],data['price'])

	cursor.execute(insert_sql,params)
	conn.commit()

def main():
	while filter_url != start_url:
		text = get_request(start_url)
		do_url = select_url(text)
		datas = parse_detail(do_url)
		for i in data_clean(datas):
			if i:
				insert_into_sql(i)
				print('插入成功')
			else:
				print('插入失败')
			
if __name__ == '__main__':
	main()