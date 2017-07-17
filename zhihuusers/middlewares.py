# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import logging
from scrapy import signals
import redis

logger = logging.getLogger(__name__)

class ZhihuusersSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class MyProxyMiddleware(object):
    def __init__(self,redis_host,redis_port,redis_password,redis_db,redis_listname):
        if redis_password:
            self.client = redis.Redis(redis_host,redis_port,redis_db,redis_password)
        else:
            self.client = redis.Redis(redis_host,redis_port,redis_db)
        self.redis_listname = redis_listname
        self.proxy = self._get_proxy()
        self.count = 0

    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            redis_host= crawler.settings.get('REDIS_HOST'),
            redis_port= crawler.settings.get('REDIS_PORT'),
            redis_password= crawler.settings.get('REDIS_PASSWORD'),
            redis_db= crawler.settings.get('REDIS_DB'),
            redis_listname= crawler.settings.get('REDIS_LISTNAME')
        )

    def _get_proxy(self):
        try:
            return self.client.rpop(self.redis_listname).decode('utf-8')
        except:
            logger.warn('代理池为空')

    def _put_back(self):
        try:
            self.client.lpush(self.redis_listname, self.proxy)
        except:
            logger.warn('IP放回代理池错误')

    def process_request(self,request,spider):
        """添加代理"""
        if not self.proxy:
            return
        request.meta['proxy'] = 'http://' + self.proxy
        self.count += 1
        if self.count >=200:
            logger.info('%s 爬起超200，更换IP' %self.proxy)
            self._put_back()
            self.proxy = self._get_proxy()
            self.count = 0

    def process_response(self,request,response,spider):
        """检测状态码"""
        if response.status > 302:
            now_proxy = request.meta['proxy']
            if self.proxy in now_proxy:
                logger.info('%s 请求失败，结果为：%s' %(self.proxy,response.status))
                self.proxy = self._get_proxy()
                self.count = 0
            new_request = request.copy()
            new_request.dont_filter = True
            return new_request
        else:
            return response

    def process_exception(self,request,exception,spider):
        now_proxy = request.meta['proxy']
        if self.proxy in now_proxy:
            logger.info('%s 连接超时，IP不可用，更换IP重新请求...' %self.proxy)
            self.proxy = self._get_proxy()
            self.count = 0
        new_request = request.copy()
        new_request.dont_filter = True
        return new_request


