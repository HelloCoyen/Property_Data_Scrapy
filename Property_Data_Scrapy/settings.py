# -*- coding: utf-8 -*-

# Scrapy settings for Property_Data_Scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#	  https://doc.scrapy.org/en/latest/topics/settings.html
#	  https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#	  https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import datetime

BOT_NAME = 'Property_Data_Scrapy'

SPIDER_MODULES = ['Property_Data_Scrapy.spiders']
NEWSPIDER_MODULE = 'Property_Data_Scrapy.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 50

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_IP = 10

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#	'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#	 'Property_Data_Scrapy.middlewares.PropertyDataScrapySpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
	'Property_Data_Scrapy.middlewares.PropertyDataScrapyDownloaderMiddleware': 100,
	'Property_Data_Scrapy.middlewares.UserAgentMiddleware': 200,
	'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 201,
	'Property_Data_Scrapy.middlewares.IpPoolMiddleware': 100,
	'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 101,
	#'Property_Data_Scrapy.middlewares.UrlFilter':1#待开发bekery数据库
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#	 'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
	'Property_Data_Scrapy.pipelines.DataBasePipeline': 200,
	'Property_Data_Scrapy.pipelines.PropertyDataScrapyCSVPipeline': 300,
	'Property_Data_Scrapy.pipelines.PriceCSVPipeline': 600,
	'Property_Data_Scrapy.pipelines.CoordinateCSVPipeline': 400,
	'Property_Data_Scrapy.pipelines.ElevatorCSVPipeline': 500,
	#'scrapy_redis.pipelines.RedisPipeline': 100
	#'Property_Data_Scrapy.pipelines.CiytUrlPipeline':201
	}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

DOWNLOAD_TIMEOUT = 5

# 数据库配置
MONGODB_HOST = "127.0.0.1"
MONGODB_PORT = 27017
MONGODB_DBNAME = "Property_Information_Database"
MONGODB_DOCNAME = ["Information", "Coordinate", "Price", "Elevator"]

# 分布式配置
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"
SCHEDULER_PERSIST = True
REDIS_HOST = "0.0.0.0"
REDIS_PORT = 6000
REDIS_PARAMS ={
	'password': '111',
	}
SCHEDULER_FLUSH_ON_START = False

RETRY_TIMES = 6

# 日志
today= datetime.datetime.now()
log_file_path = "./log/property-{}-{}-{}.log".format(today.year, today.month, today.day)
LOG_LEVEL = "INFO"
LOG_FILE = log_file_path
