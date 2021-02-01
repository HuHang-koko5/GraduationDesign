# -*- coding: utf-8 -*-

# Scrapy settings for graduationProject project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'graduationProject'

SPIDER_MODULES = ['graduationProject.spiders']
NEWSPIDER_MODULE = 'graduationProject.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'graduationProject (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
    'Cookie':'SINAGLOBAL=6521108525349.997.1521360929792; login_sid_t=00e6062b28b41562a66cb23bc3acb1e5; cross_origin_proto=SSL; _s_tentry=passport.weibo.com; Apache=9011125451801.15.1555492634277; ULV=1555492634284:28:3:1:9011125451801.15.1555492634277:1554799036436; appkey=; UOR=,,login.sina.com.cn; SSOLoginState=1555682559; un=ojqupmkokk6d@game.weibo.com; wvr=6; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5WVl03Z12mjrvCCAHnNPON5JpX5KMhUgL.FoqNehMXehMcS0n2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMcS05NSh5NSoMR; ALF=1587454914; SCF=AijDwpvAA24o8kfh0yPv0i0v4vi6L_1xtD2ntDzP-vpFibVDnofxl4dWJnvH1seGGmK9wVUjmvY14RSFPCQsHhk.; SUB=_2A25xuQATDeRhGeBJ61UV8CnKzDSIHXVSz3bbrDV8PUNbmtAKLXGhkW9NRnSo_16OSGFvcvHyhWcatIG6H4HfC54t; SUHB=02M__qlV_M2y_1'
}
# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'graduationProject.middlewares.GraduationprojectSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'graduationProject.middlewares.GraduationprojectDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'graduationProject.pipelines.GraduationprojectPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
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
CONCURRENT_REQUESTS = 8

DOWNLOAD_DELAY = 8

DOWNLOADER_MIDDLEWARES = {
    'weibo.middlewares.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None
}

ITEM_PIPELINES = {
    'graduationProject.pipelines.MongoDBPipeline': 300,

}
# MongoDb 配置
LOCAL_MONGO_HOST = 'localhost'
LOCAL_MONGO_PORT = 27017
DB_NAME = 'earthquake'