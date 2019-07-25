from flask import Flask, render_template,redirect,url_for,session,g
import sqlite3

from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
bootstrap = Bootstrap(app)

class RegistrationForm(FlaskForm):
    login = StringField('Ваш логин', validators=[DataRequired()])
    password = StringField('Ваш пароль',validators=[DataRequired()])
    email = StringField('Ваша почта', validators=[DataRequired()])
    regsubmit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    log = StringField('Ваш логин', validators=[DataRequired()])
    pas = StringField('Ваш пароль', validators=[DataRequired()])
    logsubmit = SubmitField('Войти')

class ChatForm(FlaskForm):
    message = StringField('Введите сообщение', validators=[DataRequired()])
    chatsubmit = SubmitField('Отправить сообщение')

class Submits(FlaskForm):
    navbarreg = SubmitField('Регистрация')
    navbarlog = SubmitField('Войти')
    navbarchat = SubmitField('Чат')


@app.before_request
def before():
    g.log=None
    if 'log' in session:
        g.log=session['log']


@app.route('/', methods = ['GET', 'POST'])
def main():
    form_navbar = Submits()
    return render_template('main_for_chat.html', form_navbar = form_navbar)

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    login = None
    password = None
    email = None
    form_navbar = Submits()
    form_reg = RegistrationForm()
    if form_reg.validate_on_submit():
        conn = sqlite3.connect('regbd.db')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS REG_IN(number integer PRIMARY KEY, user_login text, user_password text, user_email text)')
        login = form_reg.login.data
        password = form_reg.password.data
        email = form_reg.email.data
        cursor.execute('INSERT INTO REG_IN(user_login,user_password,user_email) VALUES(?,?,?)', (login, password, email))
        conn.commit()
        cursor.execute('SELECT* FROM REG_IN')
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        cursor.close()
        conn.close()
    return render_template('reg.html', form_reg = form_reg, form_navbar = form_navbar, login = login, password = password, email = email)


@app.route('/login', methods=['GET', 'POST'])
def login():
    log = None
    pas = None
    form_log = LoginForm()
    form_navbar = Submits()
    if form_log.validate_on_submit():
        log = form_log.log.data
        pas = form_log.pas.data
        conn = sqlite3.connect('regbd.db')
        cursor = conn.cursor()
        z = cursor.execute('SELECT user_password FROM REG_IN WHERE user_login=?', (log,))
        z = z.fetchone()
        if z[0] == pas:
            session['log'] = log
            cursor.close()
            conn.close()
            return render_template('success.html', log = session.get('log'))
        cursor.close()
        conn.close()
    return render_template('login.html', form_log = form_log, log = log, pas = pas, form_navbar = form_navbar)

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/chatpage', methods=['GET', 'POST'])
def chatpage():
    user = ''
    form_chat = ChatForm()
    form_navbar = Submits()
    if form_chat.validate_on_submit():
        all_messages = form_chat.message.data
        all_users = session.get('log')
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO MESSAGES(user_login, user_message) VALUES(?,?)', (all_users, all_messages))
        conn.commit()
        cursor.close()
        conn.close()
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS MESSAGES(number integer PRIMARY KEY, user_login text, user_message text)')
    cursor.execute('SELECT* FROM MESSAGES')
    rows = cursor.fetchall()
    print(rows)
    return render_template('chatpage.html', rows = rows, form_chat = form_chat, form_navbar = form_navbar)

if __name__ == '__main__':
    app.run()