import sqlite3
import random
import uuid
import pprint

from flask import Flask, render_template,request,session,make_response

app = Flask(__name__)

# シークレットキーの設定
app.secret_key = 'wkhrjkwe3fej'  # ここに安全なランダムな文字列を設定


#def generate_user_target_list():

def db_insert(sql):
    conn = sqlite3.connect('words.db')
    c = conn.cursor()
    print(sql)
    c.execute(sql)
    conn.commit()
    conn.close()

def db_select_all(sql):
    conn = sqlite3.connect('words.db')
    c = conn.cursor()
    print(sql)
    c.execute(sql)
    result = c.fetchall()
    print("select all \n")
    print(result)
    conn.close()
    return result

def db_select(sql):
    conn = sqlite3.connect('words.db')
    c = conn.cursor()
    print(sql)
    c.execute(sql)
    result = c.fetchone()[0]
    print("db select \n")
    pprint.pprint(result)
    conn.close()
    return result
    
def generate_randam_id():
    return str(uuid.uuid4())

def get_user_count(device_id):
    result = db_select("SELECT COUNT(*) FROM user where userid='"+device_id+"'")
    if result:
        print(device_id+"is ari.")
        return
    
    db_insert("insert into  user (userid) values  ('"+device_id+"')")
    return result

def get_target_word(device_id,lang):

    sql="select count(*) from know where userid ='"+device_id+"' and lang = '"+lang+"' and status=3"

    #知っている数
    result = db_select(sql)
    #知っている数のリスト
    ret_exclude_numbers =db_select_all("select wordid from know where userid ='"+device_id+"' and  lang = '"+lang+"' and status=3")
    #配列
    #result_str = ', '.join(value)
    #print("know value:"+result_str)
    print("\n know:")
    exclude_numbers=[]

    for row in ret_exclude_numbers:
        col1 = row[0]
        exclude_numbers.append(col1)
        #print(col1)

    print(exclude_numbers)

    nokori_num = 597 - int(result)
    numbers = list(range(1, nokori_num))
    # ランダムに10個選択
    random_numbers = random.sample(numbers, 10)

    #ここで、本当の値を入れていく。
    all_numbers = list(range(1, 598))
    nokori_numbers=list(set(all_numbers) - set(exclude_numbers))
    #print("\n nokori:")
    #print(nokori_numbers)
    
    target_words=[]
    #今回の対象は？
    for num in random_numbers:
        target_words.append(nokori_numbers[num])

    #print("\n randam_numbers:")
    #print(random_numbers)
    
    print(target_words)
    return target_words


def get_random_word(lang):
    random_number = random.randint(1, 596)
    sql="select w.num ,lang , forei, japanese , katakana from words as w,base_words as bw where  w.lang ='"+lang+"' and w.num="+str(random_number)+" and w.num=bw.num"
    print(sql)
    #c.execute('SELECT image, japanese, foreign, katakana FROM words WHERE lang=? ORDER BY RANDOM() LIMIT 1', (lang,))
    row=db_select_all(sql)
    return row


def get_myself_random_word(device_id,lang,test):

    str_status="status=1"

    if test == True:
        str_status="status=2"
    
    sql ="select wordid from know where userid ='"+device_id+"' and lang ='"+lang+"' and "+str_status
    list = db_select_all(sql)

    target_nums=[]
    #今回の対象は？
    for num in list:
        target_nums.append(num[0])

    random_number = random.randint(0, len(target_nums)-1)

    print(random_number)
    targetnum= target_nums[random_number]

    sql="select w.num ,lang , forei, japanese , katakana from words as w,base_words as bw where  w.lang ='"+lang+"' and w.num="+str(targetnum)+" and w.num=bw.num"
    print(sql)
    row=db_select_all(sql)

    #print("get myself\n")
    #print(type(row))
    return row


#取組中のものがどれだけあるか？
def get_uw_count(device_id,lang,test):

    str_status="status=1"

    if test == True:
        str_status="status=2"

    sql="select count(*) from know where lang='"+lang+"' and userid='"+device_id+"' and "+str_status
    row=db_select(sql)
    return row

#取組中を追加する。
def add_target_word(device_id,lang,add_list):
    for add_value in add_list:
        sql="insert into know (userid,wordid,lang,status) values ('"+device_id+"',"+str(add_value)+",'"+lang+"',1)"
        print(sql)
        db_insert(sql)


#OKなので、このnumはstatus=2にする。
def  update_konw(device_id,lang,num,status):
    print(type(num))
    sql="update know set status="+str(status)+" where userid='"+device_id+"' and wordid="+num+" and lang='"+lang+"'" 
    print(sql)
    db_insert(sql)


@app.route('/selected')
def selected():
    #langが選択されて対象を決める。
    device_id = request.cookies['device_id']
    lang = request.args.get('lang')
    
    wordid=request.args.get('num')
    okng = request.args.get('ok')

    if wordid is not None and okng is not None :
        update_konw(device_id,lang,wordid,2)    

    #今取組中のものがどれだけあるか？
    uw_num=get_uw_count(device_id,lang,False)

    #もし０だったら、
    if uw_num == 0 :
        target_list=get_target_word(device_id,lang)
        #このユーザーのターゲットリストに紐付ける。
        add_target_word(device_id,lang,target_list)
    
    ret=get_myself_random_word(device_id,lang,False)
    num, lang, forei, japanese, katakana =  ret[0]
    imgsrc="img//iamge_"+str(num)+".png"
    return render_template('question.html', lang=lang, word=forei,  num=num, katakana=katakana,japanese=japanese)

#テストの時間
@app.route('/quiz')
def question():
    lang = request.args.get('lang')
    
    if 'device_id' in request.cookies:
        device_id = request.cookies['device_id']

    uw_num=get_uw_count(device_id,lang,True)

    if uw_num == 0:
        return render_template('select.html')

    ret=get_myself_random_word(device_id,lang,True)
    num, lang, forei, japanese, katakana = ret[0]
    
    imgsrc="img//iamge_"+str(num)+".png"

    return render_template('test.html', lang=lang, word=forei,  num=num, katakana=katakana,japanese=japanese)

@app.route('/logged')
def test2():
    if 'userid' in session:
        suuid= session['userid']
    else:
        suuid="mada" 
    return render_template('test.html',uuid=suuid)


@app.route('/test')
def test():
    device_id = request.cookies['device_id']
    list=get_target_word(device_id,"cn")

    return render_template('test.html',uuid=device_id)

@app.route('/')
def index():
    if 'device_id' in request.cookies:
        device_id = request.cookies['device_id']
    else:
        device_id =generate_randam_id()
        #登録する。
        get_user_count(device_id)

    resp = make_response(render_template('select.html', name=device_id))
    resp.set_cookie("device_id", device_id)    

    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=True)