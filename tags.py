import sqlite3
import re
import jieba
from jieba import analyse

tfidf = analyse.extract_tags
analyse.set_stop_words("stopwords")

def fetch_users():
    conn=sqlite3.connect('weibo.db')
    c=conn.cursor()
    c.execute("select * from users")
    raw_text=c.fetchall()
    conn.close()
    return raw_text

def extract_raw_text(raw_text):
    for text in raw_text:
        user_id=text[0]
        real_text=text[10]
        real_text = re.sub(r'@(.+?)：', '', real_text)
        real_text = re.sub(r'@(.+?):', '', real_text)
        real_text = re.sub(r'@(.+?) ', '', real_text)
        real_text = re.sub(r'@(.+?) ', '', real_text)
        real_text = re.sub(r'#(.+?)#', '', real_text)
        print(str(real_text))
        keywords=tfidf(real_text)
        for keyword in keywords:
            conn = sqlite3.connect('weibo.db')
            conn.execute("insert into tags (user_id,tag) values (?,?)",
                         (format(user_id), format(keyword)))
            conn.commit()
            conn.close()
            print(str(user_id)+"关键字为"+str(keyword))

extract_raw_text(fetch_users())