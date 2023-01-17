"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
from datetime import timedelta
import os
from flask import render_template, request, url_for, redirect,Flask
import pymysql
import pandas as pd
import json

config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'remoteroot',
    'passwd': '123456',
    'charset': 'utf8mb4',
    'db':'newbird',
    'cursorclass': pymysql.cursors.DictCursor
}
app = Flask(__name__)
wsgi_app = app.wsgi_app
# 从数据库中读取数据并且转成相应格式传到前端
conn = pymysql.connect(**config)


def sql_result(sql,uplimit=None):
    # conn.autocommit(1)
    cursor = conn.cursor()
    cursor.execute(sql)
    # print('total records:', cursor.rowcount)
    result = cursor.fetchall()
    if uplimit:
        result = result[:uplimit]
    return result


def form_name(s):
    return pd.Series(
        {
            'mu': s['section'].unique()[0],
            'ke': s['species'].unique(),
            'zhong': s['bird'].unique()
        }
    )

def get_bird_name():
    sql = 'SELECT * FROM bird_name'
    bird_name = sql_result(sql)
    bird_name = pd.DataFrame(bird_name)
    gr = bird_name.groupby(['section']).apply(lambda s: form_name(s)).reset_index(drop=True)
    lis = []
    for row in gr.itertuples(index=False):
        line = {}
        line['mu'] = getattr(row, 'mu')
        line['ke'] = list(getattr(row, 'ke'))
        line['zhong'] = list(getattr(row, 'zhong'))
        lis.append(line)
    return lis

def get_hot_city():
    sql = 'SELECT * FROM city_record_cnt'
    hotCity = sql_result(sql, uplimit = 10)
    return hotCity

def get_hot_bird():
    sql = 'SELECT * FROM bird_record_cnt'
    birdRecord = sql_result(sql)
    birdRecord = pd.DataFrame(birdRecord)
    top3 =  birdRecord.sort_values(by='record_cnt_2021',axis=0,ascending=False).iloc[:3]
    lis = []
    for row in top3.itertuples(index=False):
        line = {}
        name =  line['bird'] = getattr(row, 'bird')
        picsql = "SELECT intro_pic FROM birdintro c WHERE c.中文名='%s'" % (name)
        ensql = "SELECT 英文名 FROM birdintro c WHERE c.中文名='%s'" % (name)
        line['bird'] = getattr(row, 'bird')
        line['num'] = getattr(row, 'record_cnt_2021')
        line['imgsrc'] = sql_result(picsql, 1)[0]['intro_pic']
        line['enName'] = sql_result(ensql, 1)[0]['英文名']
        lis.append(line)
    return lis


@app.route('/',methods=['GET','POST'])
def hello():

    if request.method == 'POST':
        return redirect(url_for('analysis'))

    birdType = get_bird_name()
    hotCity = get_hot_city()
    top3 = get_hot_bird()
    return render_template("index.html",birdType=birdType,HotCity=hotCity,top3=top3)

@app.route('/detail/<string:bird>',methods=['GET','POST'])
def detail(bird):
    # 返回上一页
    if request.method == 'POST':
        return redirect(url_for('hello'))

    # 名称 获取
    introsql = "SELECT * FROM birdintro c WHERE c.中文名='%s'"%(bird)
    intro = sql_result(introsql,1)
    if intro:
        intro = intro[0]
        # 图片链接 从两个数据库中取出来 一个list进行循环渲染
        picsql = "SELECT * FROM birdpic c WHERE c.bird='%s'" % (bird)
        img = sql_result(picsql)
        piclis = []
        piclis.append(intro['intro_pic'])
        for record in img:
            piclis.append(record['imgsrc'])

        prosql = "SELECT * FROM bird_pro_cnt c WHERE c.bird='%s'" % (bird)
        relis = sql_result(prosql)
        posts=[]
        for record in relis:
            line = []
            a={}
            b={}
            a['name'] = record['bird']
            line.append(a)
            b['name'] = record['province']
            b['value'] = record['pro_cnt']
            line.append(b)
            posts.append(line)
        return render_template("detail.html", intro=intro, piclis=piclis, posts=json.dumps(posts))
    else:
        return render_template('none.html')
    # 音频信息 -- 如有
    # audiosql = "SELECT * FROM birdaudio c WHERE c.bird='%s'" % (bird)


@app.route('/analysis',methods=['POST','GET'])
def analysis():
    if request.method == 'POST':
        return redirect(url_for('hello'))
    return render_template("home_page.html")

@app.route('/search/',methods=['GET','POST'])
def search():
    bird = request.form.get('textfield')
    return redirect(url_for('detail',bird=bird))



if __name__ == '__main__':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
    conn.close()

