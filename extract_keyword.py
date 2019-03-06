import sqlite3
import re
from jieba import analyse

textrank = analyse.textrank
analyse.set_stop_words("stopwords")

def fetch_text():
    conn=sqlite3.connect('weibo.db')
    c=conn.cursor()
    c.execute("select * from weibo_text")
    raw_text=c.fetchall()
    conn.close()
    return raw_text

def extract_raw_text(raw_text):
    for text in raw_text:
        weibo_id=text[0]
        user_id=text[1]
        real_text=text[4]
        real_text = re.sub(r'@(.+?)：', '', real_text)
        real_text = re.sub(r'@(.+?):', '', real_text)
        real_text = re.sub(r'@(.+?) ', '', real_text)
        real_text = re.sub(r'@(.+?) ', '', real_text)
        real_text = re.sub(r'#(.+?)#', '', real_text)
        print(str(real_text))
        keywords=textrank(real_text,allowPOS=('n','nr','ns'))
        for keyword in keywords:
            conn = sqlite3.connect('weibo.db')
            conn.execute("insert into keywords (weibo_id,user_id,keyword) values (?,?,?)",
                         (format(weibo_id), format(user_id), format(keyword)))
            conn.commit()
            conn.close()
            print(str(weibo_id)+"关键字为"+str(keyword))

extract_raw_text(fetch_text())