# -*- coding: utf-8 -*-
import json
import scrapy
from zhihuusers.items import UsermsgItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    start_user = 'excited-vczh'

    user_url = 'http://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'locations%2Cemployments%2Cgender%2Ceducations%2Cbusiness%2Cvoteup_count%2Cthanked_Count%2Cfollower_count%2Cfollowing_count%2Ccover_url%2Cfollowing_topic_count%2Cfollowing_question_count%2Cfollowing_favlists_count%2Cfollowing_columns_count%2Cavatar_hue%2Canswer_count%2Carticles_count%2Cpins_count%2Cquestion_count%2Ccolumns_count%2Ccommercial_question_count%2Cfavorite_count%2Cfavorited_count%2Clogs_count%2Cmarked_answers_count%2Cmarked_answers_text%2Cmessage_thread_token%2Caccount_status%2Cis_active%2Cis_bind_phone%2Cis_force_renamed%2Cis_bind_sina%2Cis_privacy_protected%2Csina_weibo_url%2Csina_weibo_name%2Cshow_sina_weibo%2Cis_blocking%2Cis_blocked%2Cis_following%2Cis_followed%2Cmutual_followees_count%2Cvote_to_count%2Cvote_from_count%2Cthank_to_count%2Cthank_from_count%2Cthanked_count%2Cdescription%2Chosted_live_count%2Cparticipated_live_count%2Callow_message%2Cindustry_category%2Corg_name%2Corg_homepage%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'
    followee_url = 'http://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset=0&limit=20'
    follower_url = 'http://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset=0&limit=20'
    follower_query = 'data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'

    def start_requests(self):
        yield scrapy.Request(self.user_url.format(user=self.start_user,include=self.user_query),callback=self.parse_url)
        yield scrapy.Request(self.follower_url.format(user=self.start_user,include=self.follower_query),callback=self.parse_follower)
        yield scrapy.Request(self.followee_url.format(user=self.start_user,include=self.follower_query),callback=self.parse_followee)

    def parse_url(self, response):
        result = json.loads(response.text)
        item = UsermsgItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result[field]
        yield item
        yield scrapy.Request(self.follower_url.format(user=result.get('url_token'),include=self.follower_query),callback=self.parse_follower)
        yield scrapy.Request(self.followee_url.format(user=result.get('url_token'),include=self.follower_query),callback=self.parse_followee)

    def parse_follower(self,response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for one in results.get('data'):
                yield scrapy.Request(self.user_url.format(user=one.get('url_token'),include=self.user_query),callback=self.parse_url)

        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield scrapy.Request(next_page,callback=self.parse_follower)

    def parse_followee(self,response):
        res = json.loads(response.text)
        if 'data' in res.keys():
            for people in res.get('data'):
                yield scrapy.Request(self.user_url.format(user=people.get('url_token'),include=self.user_query),callback=self.parse_url)

        if 'paging' in res.keys() and res.get('paging').get('is_end') == False:
            next_page_url = res.get('paging').get('next')
            yield scrapy.Request(next_page_url,callback=self.parse_followee)