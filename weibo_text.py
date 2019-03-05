import requests
import json
import time
import random
import sqlite3
import datetime
import re

today_raw=datetime.date.today()
today=today_raw.strftime('%m-%d')
yesterday = (datetime.date.today() + datetime.timedelta(days=-1)).strftime('%m-%d')

def readId():
    conn = sqlite3.connect('weibo.db')
    c = conn.cursor()

    c.execute("select id from users")
    rows=c.fetchall()
    conn.close()
    return rows

def findText(rows,start):
    for i in range (start,1800): #应该从0开始
        now_id=rows[i][0]
        url="https://m.weibo.cn/api/container/getIndex?type=uid&value="+str(now_id)+"&containerid=1076031"+str(now_id)+"&page=1"
        crawl_text(url,now_id)
        t=random.randint(5,8)
        print("sleep for "+str(t)+" seconds.")
        time.sleep(t)

def crawl_text(url,user_id):
    req=requests.get(url)
    inidata=req.text
    data=json.loads(inidata)

    contents=data['data']['cards']
    for content in contents:
        if content['card_type'] is '9':
            real_content=content['mblog']
            time=real_content['created_at']
            if '昨天' in time :
                created_date=yesterday
            if '分钟前' in time or '小时前' in time :
                created_date=today
            else:
                created_date=time
            weibo_id=real_content['id']
            user_id=real_content['user']['id']
            user_name=real_content['user']['screen_name']
            raw_text=real_content['raw_text']
            text=real_content['text']
            reposts_count=real_content['reposts_count']
            comments_count=real_content['comments_count']
            try:  #转发信息处理
                forward=real_content['retweeted_status']
                tackle_forward(forward,weibo_id)
                is_forward="yes"
                forward_id=forward['id']
            except:
                print("original weibo")
                is_forward="no"

            try:  #图片url提取
                pics=real_content['pics']
                tackle_pics(pics,weibo_id)
                is_pics='yes'
            except:
                print("no pics")
                is_pics='no'
                   #at信息
            is_at=find_at(text)
            try:
                next_info=real_content['page_info']
                is_topic , is_video =tackle_forward(next_info,weibo_id)
            except:
                print('no videos or topics')







def tackle_forward(forward,weibo_id):
    time.sleep(1)

def tackle_pics(pics,weibo_id):
    time.sleep(1)

def tackle_video_and_topic(next_info,weibo_id):
    is_topic = 'no'
    is_video = 'no'
    for i in range(1, 10):
        try:
            info = next_info['content{}'.format(i)]
        except:
            print('no more information')
            info = ""
            continue
        if '#' in info:
            is_topic = 'yes'
        elif '视频' in info:
            is_video = 'yes'
    return is_topic,is_video

def get_raw_text(text):
    raw_text = re.sub(r'</?\w+[^>]*>', '', text)
    return raw_text

def find_at(text):
    return