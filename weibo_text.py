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
        print('''
                    ****************************
                    *                          * 
                    * 当前在获取第{}个账号的信息  *
                    *                          *
                    ****************************
                    '''.format(i))
        now_id=rows[i][0]
        url="https://m.weibo.cn/api/container/getIndex?type=uid&value="+str(now_id)+"&containerid=107603"+str(now_id)+"&page=1"
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
        if content['card_type'] is 9:
            real_content = content['mblog']
            tackle_text(real_content)


def tackle_text(real_content):
    time = real_content['created_at']
    if '昨天' in time:
        created_date = yesterday
    elif '分钟前' in time or '小时前' in time:
        created_date = today
    else:
        created_date = time
    weibo_id = real_content['id']
    user_id = real_content['user']['id']
    user_name = real_content['user']['screen_name']
    text = real_content['text']
    raw_text = get_raw_text(text)
    reposts_count = real_content['reposts_count']
    comments_count = real_content['comments_count']
    try:  # 转发信息处理
        forward = real_content['retweeted_status']
        tackle_forward(forward, weibo_id,user_id)
        is_forward = 1
        forward_id = forward['id']
    except Exception as e:
        print(e)
        is_forward = 0
        forward_id = ""

    try:  # 图片url提取
        pics = real_content['pics']
        tackle_pics(pics, weibo_id)
        is_pics = 1
    except Exception as e:
        print("no pics")
        print("reason:",e)
        is_pics = 0
        # at信息
    is_at = find_at(text,weibo_id,user_id)
    is_topic = find_topic(text,weibo_id,user_id)
    is_video = 0
    try:
        next_info = real_content['page_info']
        result = tackle_video_and_topic(next_info, weibo_id,user_id)
        if result is 0:
            is_topic = 0
            is_video = 0
        elif result is 1:
            is_topic = 0
            is_video = 1
        elif result is 2:
            is_topic = 1
            is_video = 0
        elif result is 3:
            is_topic = 1
            is_video = 1
    except:
        print('no videos or topics')

    # database
    conn = sqlite3.connect('weibo.db')
    c = conn.cursor()
    c.execute("insert into weibo_text (weibo_id,user_id,user_name,text,raw_text,time,reposts_count," \
          "comments_count,pic_exist,at_exist,video_exist,topic_exist,is_forward,forward_weibo_id" \
          ") values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (format(weibo_id), format(user_id), format(user_name), format(text)
                                                    , format(raw_text), format(created_date), format(reposts_count),
                                                    format(comments_count),
                                                    format(is_pics), format(is_at), format(is_video), format(is_topic),
                                                    format(is_forward), format(forward_id)))
    conn.commit()
    print("successfully recorded !")
    conn.close()

def tackle_forward(forward,weibo_id,user_id):
    tackle_text(forward)
    forward_weibo_id=forward['id']
    forward_user_id=forward['user']['id']

    conn=sqlite3.connect('weibo.db')
    c=conn.cursor()
    c.execute("insert into forwards (origin_weibo_id,forward_weibo_id,origin_user_id,"
              "forward_user_id) values (?,?,?,?)",(format(weibo_id),format(forward_weibo_id),format(user_id),format(forward_user_id)))
    conn.commit()
    conn.close()


def tackle_pics(pics,weibo_id):
    for pic in pics:
        url=pic['url']
        conn=sqlite3.connect('weibo.db')
     #   c=conn.cursor
        conn.execute("insert into pics(weibo_id,pic_url) values (?,?)",(format(weibo_id),format(url)))
        conn.commit()
        conn.close()

def tackle_video_and_topic(next_info,weibo_id,user_id):
    is_topic = 0
    is_video = 0
    result=0
    type=next_info['page_type']
    if type is 'topic':
        is_topic = 1
        conn = sqlite3.connect('weibo.db')
        conn.execute("insert into topics (weibo_id,user_id,topic_content) values (?,?,?)",
                  (format(weibo_id), format(user_id),format(next_info['page_title'])))
        conn.commit()
        conn.close()
    elif type is 'video':
        is_video = 1
        conn = sqlite3.connect('weibo.db')
    #    c = conn.cursor
        conn.execute("insert into videos (weibo_id,video_url) values (?,?)",
                  (format(weibo_id), format(next_info['stream_url'])))
        conn.commit()
        conn.close()

    if is_topic is 0 and is_video is 0:
        result=0
    elif is_topic is 0 and is_video is 1:
        result=1
    elif is_topic is 1 and is_video is 0:
        result=2
    elif is_topic is 1 and is_video is 1:
        result=3
    return result

def get_raw_text(text):
    raw_text = re.sub(r'</?\w+[^>]*>', '', text)
    return raw_text

def find_at(text,weibo_id,user_id):
    ats=""
    ats=re.findall(r">@(.+?)<",text)
    if len(ats):
        is_at = 1
        for at in ats:
            conn = sqlite3.connect('weibo.db')
            #  c = conn.cursor
            conn.execute("insert into ats (weibo_id,at_name,ori_id) values (?,?,?)",
                         (format(weibo_id), format(at), format(user_id)))
            conn.commit()
            conn.close()
    else:
        is_at = 0

    return is_at

def find_topic(text,weibo_id,user_id):
    topics=re.findall(r"#(.+?)#",text)
    if len(topics):
        is_topic=1
        for topic in topics:
            conn = sqlite3.connect('weibo.db')
            conn.execute("insert into topics (weibo_id,user_id,topic_content) values (?,?,?)",
                         (format(weibo_id), format(user_id), format(topic)))
            conn.commit()
            conn.close()
    else:
        is_topic=0
    return is_topic

rows=readId()
findText(rows,1605)

