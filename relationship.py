import requests
import json
import time
import random
import sqlite3

def readId():
    conn = sqlite3.connect('weibo.db')
    c = conn.cursor()

    c.execute("select id from users")
    rows=c.fetchall()
    conn.close()
    return rows

def findFollowing(rows,start):

    for i in range(start,1800):  #关机之前一定要注意这个数字⬇用于断点重跑数据
        print('''
            ****************************
            *                          * 
            * 当前在获取第{}个账号的关注  *
            *                          *
            ****************************
            '''.format(i))
        for j in range(1,100):
            real_id=rows[i][0] #取出来是元组
            url = "https://m.weibo.cn/api/container/getSecond?containerid=100505{}_-_FOLLOWERS&page=".format(real_id)+str(j)
            try:
                crawlFollowing(url,real_id)
            except:
                print("搜索完毕")
                break

def crawlFollowing(url,originalId):
    req = requests.get(url)
    inidata = req.text
    data = json.loads(inidata)

    contents=data['data']['cards']

    for content in contents:
        is_verified=content['user']['verified']
        verified_type=content['user']['verified_type']
        id=content['user']['id']
        if is_verified is True and verified_type is 2:
            print("关系：%s->%s 已确定",format(originalId),format(id))
            conn=sqlite3.connect('weibo.db')
            c=conn.cursor()
            c.execute("insert into relationship_table (follower_id,following_id) values(?,?)",(format(originalId),format(id)))
            conn.commit()
            print("recorded database successful")
            conn.close()
        else:
            print("非符合要求关注关系")
    t=random.random()*3
    print("休眠时间为:{}s".format(t))
    time.sleep(t)

rows=readId()
findFollowing(rows,1) #手动断点，将上次跑过得行数放到这里，预计整个工程需要的时间为32w秒 orz
