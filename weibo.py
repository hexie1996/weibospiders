# -*- coding: utf-8 -*-
""" Created on Thu Aug 3 20:59:53 2017 @author: Administrator """

import requests
import json
import time
import random
import sqlite3


def initial(url):
    #读取初始的信息
    req = requests.get(url)
    inidata = req.text
    data1 = json.loads(inidata)

    content = data1['data']['cards']
    k=1
    for i in content:
        followingId = i['user']['id']
        try:
            is_verified= i['user']['verified']
        except:
            continue
        type=i['user']['verified_type']
        #通过观察得出type为2的时候为企业号，可以初步排除掉一些数据
        if type != 2:
            continue
        print("用户关注的第"+str(k)+"个人的关注列表")
        k=k+1
        for j in range(1, 11):
            print("正在获取第{}页的关注列表:".format(j))
            print("用户ID为:{}".format(followingId))
            OriginalId=followingId
            # 微博用户关注列表JSON链接
            url = "https://m.weibo.cn/api/container/getSecond?containerid=100505{}_-_FOLLOWERS&page=".format(followingId) + str(j)
            try:
                crawlDetailPage(url, j, OriginalId)
            except:
                print("用户信息已搜索完毕")
                break
             #设置休眠时间
            t = random.randint(10, 13)
            print("休眠时间为:{}s".format(t))
            time.sleep(t)



def crawlDetailPage(url,page,OriginalId):
    #读取微博网页的JSON信息
    req = requests.get(url)
    jsondata = req.text
    data = json.loads(jsondata)

    #获取每一条页的数据
    content = data['data']['cards']
    #print(content)
    #循环输出每一页的关注者各项信息
    for i in content:
        followingId = i['user']['id']
        followingName = i['user']['screen_name']
        followingUrl = i['user']['profile_url']
        followersCount = i['user']['followers_count']
        followCount = i['user']['follow_count']
        description = i['user']['description']
        image = i['user']['profile_image_url']
        verified = i['user']['verified']
        try:
            verified_reason=i['user']['verified_reason']
            verified_type=i['user']['verified_type']
        except:
            verified_reason=""
            verified_type=""
        gender = i['user']['gender']

        if verified_type is 2:
            print("---------------------------------")
            print("用户ID为:{}".format(followingId))
            print("用户昵称为:{}".format(followingName))
            print("用户详情链接为:{}".format(followingUrl))
            print("用户粉丝数:{}".format(followersCount))
            print("用户关注数:{}".format(followCount))
            print("简介:{}".format(description))
            print("头像链接：{}".format(image))
            print("是否是认证用户：{}".format(verified))
            print("认证原因：{}".format(verified_reason))
            print("认证类别：{}".format(verified_type))
            print("性别{}".format(gender))
            conn = sqlite3.connect('weibo.db')
            c = conn.cursor()
            print("Opened database successfully")
            try:
                c.execute("insert into users (id,name,url,fans,following,description,image,verified,verified_reason,gender,verified_type) values (?,?,?,?,?,?,?,?,?,?,?);"
                          ,(format(followingId),format(followingName),format(followingUrl),
                            format(followersCount),format(followCount),format(description),format(image),format(verified),format(verified_reason),format(gender),format(verified_type)))
                c.execute("insert into relationship_table (follower_id,following_id) values (?,?);",(format(OriginalId),format(followingId)))
            except:
                print("database mistake")

            conn.commit()
            print("recorded database successfully")
            conn.close()
        else:
            print("this record is not satisfied")
for i in range(1,11):
    #初始账号@新浪科技
    url = "https://m.weibo.cn/api/container/getSecond?containerid=1005052002148123_-_FOLLOWERS&page=" + str(i)
    initial(url)