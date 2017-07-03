# -*- coding: utf-8 -*-
import json
import scrapy
from zhihuusers.items import UsermsgItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    start_user = 'excited-vczh'

    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,avatar_hue,answer_count,articles_count,pins_count,question_count,columns_count,commercial_question_count,favorite_count,favorited_count,logs_count,marked_answers_count,marked_answers_text,message_thread_token,account_status,is_active,is_force_renamed,is_bind_sina,sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,badge[?(type=best_answerer)].topics'
    followee_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset=0&limit=20'
    follower_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset=0&limit=20'
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