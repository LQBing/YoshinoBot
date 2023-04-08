# 订阅推主

import asyncio
import itertools
import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, Set

import peony
from peony import PeonyClient
from peony.exceptions import PeonyException

from hoshino import Service, priv
from hoshino.config import twitter as cfg
from hoshino.typing import MessageSegment as ms

from . import sv
from .util import format_tweet, cut_list

# import logging
# sv.logger.setLevel(logging.DEBUG)

service_collection = [
    Service("twitter-stream-test", enable_on_default=False, manage_priv=priv.SUPERUSER, visible=False),
    Service("kc-twitter", help_="艦これ推特转发", enable_on_default=False, bundle="kancolle"),
    Service("pcr-twitter", help_="日服Twitter转发", enable_on_default=True, bundle="pcr订阅"),
    # Service("uma-twitter", help_="ウマ娘推特转发", enable_on_default=False, bundle="umamusume"),
    # Service("pripri-twitter", help_="番剧《公主代理人》官推转发", enable_on_default=False),
    # Service("coffee-favorite-twitter", help_="咖啡精选画师推特转发", enable_on_default=False, bundle="artist"),
    Service("moe-artist-twitter", help_="萌系画师推特转发", enable_on_default=False, bundle="artist"),
    # Service("depress-artist-twitter", help_="致郁系画师推特转发", enable_on_default=False, bundle="artist"),
]

'''
class UserIdCache:
    _cache_file = os.path.expanduser("~/.hoshino/twitter_uid_cache.json")

    def __init__(self) -> None:
        self.cache = {}
        if os.path.isfile(self._cache_file):
            try:
                with open(self._cache_file, "r", encoding="utf8") as f:
                    self.cache = json.load(f)
            except Exception as e:
                sv.logger.exception(e)
                sv.logger.error(f"{type(e)} occured when loading `~/.hoshino/twitter_uid_cache.json`, using empty cache.")

    def get(self, screen_name):
        return self.cache.get(screen_name)

    async def convert(self, client: PeonyClient, screen_names: Iterable[str], cached=True):

        if not cached:
            self.cache = {}

        ids = []
        for x in screen_names:
            if x not in self.cache:
                client = peony.BasePeonyClient(
                                   consumer_key=cfg.consumer_key,
                                   consumer_secret=cfg.consumer_secret,
                                   access_token=cfg.access_token_key,
                                   access_token_secret=cfg.access_token_secret,
                                   auth=peony.oauth.OAuth2Headers,
                                   api_version="2",
                                   proxy=cfg.proxy,
                                   suffix="")
                async with client:
                    try:
                        user = await client.api.users.by.username[x].get()
                        self.cache[x] = user.id
                    except PeonyException as e:
                        sv.logger.error(f"{e} occurred when getting id of `{x}`")

            id_ = self.cache.get(x)
            if id_:
                ids.append(id_)

        with open(self._cache_file, "w", encoding="utf8") as f:
            json.dump(self.cache, f)

        return ids


_id_cache = UserIdCache()
'''

@dataclass
class FollowEntry:
    services: Set[Service] = field(default_factory=set)
    profile_image: str = None
    media_only: bool = False
    forward_retweet: bool = False


class TweetRouter:
    def __init__(self):
        self.follows: Dict[str, FollowEntry] = defaultdict(FollowEntry)

    def add(self, service: Service, follow_names: Iterable[str]):
        for name in follow_names:
            self.follows[name].services.add(service)

    def set_media_only(self, screen_name, media_only=True):
        if screen_name in self.follows:
            self.follows[screen_name].media_only = media_only
        else:
            sv.logger.warning(f"No user named `{screen_name}` or `{screen_name}` not in follows. Ignore media_only set.")

    def set_forward_retweet(self, screen_name, forward_retweet=True):
        if screen_name in self.follows:
            self.follows[screen_name].forward_retweet = forward_retweet
        else:
            sv.logger.warning(f"No user named `{screen_name}` or `{screen_name}` not in follows. Ignore forward_retweet set.")

    def load(self, service_follow_dict, media_only_users, forward_retweet_users):
        for s in service_collection:
            self.add(s, service_follow_dict[s.name])
        for x in media_only_users:
            self.set_media_only(x)
        for x in forward_retweet_users:
            self.set_forward_retweet(x)


async def follow_stream():
    client = peony.BasePeonyClient(
        consumer_key=cfg.consumer_key,
        consumer_secret=cfg.consumer_secret,
        access_token=cfg.access_token_key,
        access_token_secret=cfg.access_token_secret,
        auth=peony.oauth.OAuth2Headers,
        api_version="2",
        proxy=cfg.proxy,
        suffix="",
    )
    async with client:
        follow_screen_names = set(itertools.chain(*cfg.follows.values()))
        # follow_ids = await _id_cache.convert(client, follow_screen_names)

        router = TweetRouter()
        router.load(cfg.follows, cfg.media_only_users, cfg.forward_retweet_users)

        sv.logger.info(f"订阅推主{len(follow_screen_names)}个帐号: {follow_screen_names}")

        resp = await client.api.tweets.search.stream.rules.get()                                    #先获取上一次的规则
        data = resp.get('data')
        if resp.get('data'):                                                                       #然后删除上一次的规则
            ids = list(map(lambda rule: rule["id"], data))
            payload = {"delete": {"ids": ids}}
            resp = await client.api.tweets.search.stream.rules.post(_json=payload)
        
        users = cut_list(follow_screen_names)                                                      #处理数据，准备将config里follow所有人写入规则
        userqueue=""
        for user in users:
            user = " OR from:".join(user)
            user="\"from:"+user+"\""
            userqueue+="{{'value': {},}},".format(user)
        data = eval("{{'add': [{}]}}".format(userqueue))                                            
        resp = await client.api.tweets.search.stream.rules.post(_json=data)                         #写入新规则
        #sv.logger.info(resp)                                                                       #如果stream流启动失败请查看规则是否已经写入  
        fields = {
            "tweet.fields": [
                "created_at",
                "entities",
                "referenced_tweets",
                "text",
                "author_id",
                "in_reply_to_user_id",
                "attachments",

            ],
            "expansions":["author_id", "attachments.media_keys"],                                    #不要删media_keys，否则下行不生效
            "media.fields":["url", "preview_image_url"],                                             
        }
        stream = client.api.tweets.search.stream.get.stream(**fields)                               #启动stream流
        async for tweet in stream:                                                                  #当stream流收到信息：
            sv.logger.info("Got twitter event.")
            
            if tweet.get('data'):
                sv.logger.debug(tweet)
                username = tweet.get('includes')['users'][0]['username']
                entry = router.follows[username]
                
                sv.logger.debug(entry)

                if username not in router.follows:                                                       # 推主不在订阅列表
                    sv.logger.debug(f"推主{username}不在订阅列表")
                    continue   
                if "referenced_tweets" in tweet.get('data'):                                                             
                    if 'retweeted' in tweet.get('data').referenced_tweets[0].type and not entry.forward_retweet:
                        sv.logger.debug("纯转推，已忽略")
                        continue                                                                        # 除非配置制定，忽略纯转推
                if 'in_reply_to_user_id'in tweet.get('data'):                          
                   if  tweet.get('data').in_reply_to_user_id != username:
                       sv.logger.debug("回复他人，已忽略")
                       continue                                                                     # 忽略对他人的评论，保留自评论
                if 'media' not in tweet.get('includes') and entry.media_only:
                    sv.logger.debug("无附带媒体，订阅选项media_only=True，已忽略")
                    continue                                                                        # 无附带媒体，订阅选项media_only=True时忽略
                msg = await format_tweet(tweet, client)
                sv.logger.info(f"推送推文：\n{msg}")
                for s in entry.services:
                    asyncio.get_event_loop().create_task(s.broadcast(msg, f" @{username} 推文", 0.2))

            else:
                sv.logger.debug("Ignore non-tweet event.")
