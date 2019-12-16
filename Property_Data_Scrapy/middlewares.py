# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import time
import hashlib
from scrapy.conf import settings
import pymongo
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy import signals
from scrapy import http
from fake_useragent import UserAgent

class PropertyDataScrapySpiderMiddleware(object):
	# Not all methods need to be defined. If a method is not defined,
	# scrapy acts as if the spider middleware does not modify the
	# passed objects.

	@classmethod
	def from_crawler(cls, crawler):
		# This method is used by Scrapy to create your spiders.
		s = cls()
		crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
		return s

	def process_spider_input(self, response, spider):
		# Called for each response that goes through the spider
		# middleware and into the spider.

		# Should return None or raise an exception.
		return None

	def process_spider_output(self, response, result, spider):
		# Called with the results returned from the Spider, after
		# it has processed the response.

		# Must return an iterable of Request, dict or Item objects.
		for i in result:
			yield i

	def process_spider_exception(self, response, exception, spider):
		# Called when a spider or process_spider_input() method
		# (from other spider middleware) raises an exception.

		# Should return either None or an iterable of Response, dict
		# or Item objects.
		pass

	def process_start_requests(self, start_requests, spider):
		# Called with the start requests of the spider, and works
		# similarly to the process_spider_output() method, except
		# that it doesn’t have a response associated.

		# Must return only requests (not items).
		for r in start_requests:
			yield r

	def spider_opened(self, spider):
		spider.logger.info('Spider opened: %s' % spider.name)


class PropertyDataScrapyDownloaderMiddleware(object):
	# Not all methods need to be defined. If a method is not defined,
	# scrapy acts as if the downloader middleware does not modify the
	# passed objects.

	@classmethod
	def from_crawler(cls, crawler):
		# This method is used by Scrapy to create your spiders.
		s = cls()
		crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
		return s

	def process_request(self, request, spider):
		# Called for each request that goes through the downloader
		# middleware.

		# Must either:
		# - return None: continue processing this request
		# - or return a Response object
		# - or return a Request object
		# - or raise IgnoreRequest: process_exception() methods of
		#	installed downloader middleware will be called
		return None

	def process_response(self, request, response, spider):
		# Called with the response returned from the downloader.

		# Must either;
		# - return a Response object
		# - return a Request object
		# - or raise IgnoreRequest
		return response

	def process_exception(self, request, exception, spider):
		# Called when a download handler or a process_request()
		# (from other downloader middleware) raises an exception.

		# Must either:
		# - return None: continue processing this exception
		# - return a Response object: stops process_exception() chain
		# - return a Request object: stops process_exception() chain
		pass

	def spider_opened(self, spider):
		spider.logger.info('Spider opened: %s' % spider.name)


class UserAgentMiddleware(UserAgentMiddleware):
	def process_request(self, request, spider):
		ua = UserAgent()
		request.headers["User-Agent"] = ua.random

class IpPoolMiddleware(HttpProxyMiddleware):
	# 讯代理
	def __init__(self, ip=''):
		self.ip=ip

	def process_request(self, request, spider):
		ip = "forward.xdaili.cn"
		port = "80"
		ip_port = ip + ":" + port
		proxy = "http://" + ip_port

		orderno = "ZF2019************"
		secret = "10680***************601691fe"

		timestamp = str(int(time.time()))

		string = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp
		string = string.encode()

		md5_string = hashlib.md5(string).hexdigest()
		sign = md5_string.upper()

		auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp
		request.headers['Proxy-Authorization'] = auth
		request.meta["proxy"] = proxy
		request.meta["verify"] = False
		request.meta["allow_redirects"] = False

class UrlFilter(object):
	#通过过滤url做到增量爬取
	def __init__(self):
		host = settings["MONGODB_HOST"]
		port = settings["MONGODB_PORT"]
		dbNAME = settings["MONGODB_DBNAME"]
		client = pymongo.MongoClient(host=host, port=port)
		self.db = client[dbNAME]
		self.infocoll = self.db["Information"]
		self.elecoll = self.db["Elevator"]
		self.coorcoll = self.db["Coordinate"]
		self.pricoll = self.db["Price"]

	def process_request(self, request, spider):
		if self.infocoll.count({"item_url":request.url}) > 0 or self.elecoll.count({"item_url": request.url}) > 0 or self.coorcoll.count({"item_url": request.url}) > 0 or self.pricoll.count({"item_url": request.url}) > 0:
			return http.Response(url=request.url, body=None)

