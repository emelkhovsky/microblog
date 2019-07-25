from collections import namedtuple

from flask import Flask, render_template,redirect,url_for,request,session,g
import os, sqlite3


app = Flask(__name__)
app.secret_key=os.urandom(24)

message = namedtuple('message', ['sms','n'])
messagemas = []


@app.before_request
def before():
    g.login=None
    if 'login' in session:
        g.login=session['login']


@app.route('/log',methods=['POST'])
def log(name_function):
    session.pop('login', None)
    login = request.form['login']
    password = request.form['password']
    conn = sqlite3.connect('regbd.db')
    cursor = conn.cursor()
    z= cursor.execute('SELECT user_password FROM REG_IN WHERE user_login=?',(login,))
    z=z.fetchone()
    if z[0]==password:
        session['login']=login

    return redirect(url_for(name_function))

@app.route('/', methods=['POST','GET'])
def main():
    name_function='main'
    if request.method == 'POST':
        log(name_function)
        before()
    return render_template('main.html', globlog=g.login)

@app.route('/reg', methods=['POST','GET'])
def reg():
    name_function = 'reg'
    if request.method == 'POST':
        log(name_function)
        before()
    return render_template('registration.html',globlog=g.login)

@app.route('/regbd', methods=['POST'])
def regbd():
    conn=sqlite3.connect('regbd.db')
    cursor=conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS REG_IN(number integer PRIMARY KEY, user_login text, user_password text, user_email text)')
    user_login=request.form['user_login']
    user_password=request.form['user_password']
    user_email=request.form['user_email']
    cursor.execute('INSERT INTO REG_IN(user_login,user_password,user_email) VALUES(?,?,?)', (user_login, user_password, user_email))
    conn.commit()
    cursor.execute('SELECT* FROM REG_IN')
    rows=cursor.fetchall()
    for row in rows:
        print(row)
    cursor.close()
    conn.close()
    return redirect(url_for('reg'))

@app.route('/chat', methods=['POST','GET'])
def chat():
    name_function='chat'
    if request.method == 'POST':
        log(name_function)
        before()
    return render_template('chat.html', messagemas=messagemas,globlog=g.login)

@app.route('/add_message', methods=['POST'])
def add_message():
    f = open('Files/log.txt', 'a')
    sms = request.form['sms']
    n = request.form['n']
    f.write('{} | {}\n'.format(sms, n))
    f.close()
    messagemas.append(message(sms, n))
    return redirect(url_for('chat'))



@app.route('/logout')
def logout():
    session.pop('login', None)
    return redirect(url_for('main'))



app.run(host='127.0.0.1', port=80, debug=True)