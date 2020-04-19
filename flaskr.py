#  coding: utf-8

#  todos os imports
import sqlite3
from contextlib import closing

from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash


# configuração
DATABASE = './tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development Key'
USERNAME = 'admin'
PASSWORD = 'default'

# criar nossa pequena aplicação :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('CONFIG_FLASK', silent=True)


def conectar_bd():
    return sqlite3.connect(app.config['DATABASE'])


if __name__ == '__main__':
    app.run()


def criar_bd():
    with closing(conectar_bd()) as bd:
        with app.open_instance_resource('esquema.sql') as sql:
            bd.cursor().executescript(sql.read().decode('utf-8'))
        bd.commit()


# from flaskr import criar_bd()
# criar_bd()

@app.before_request
def pre_requisicao():
    g.bd = conectar_bd()


@app.teardown_request
def encerrar_requisicao(exception):
    g.bd.close()

# passo 5


@app.route('/')
def exibir_entradas():
    sql = '''select titulo, texto from entradas order by id desc'''
    cur = g.bd.execute(sql)
    entradas = [dict(titulo=titulo, texto=texto)
                for titulo, texto in cur.fetchall()]
    return render_template('exibir_entradas.html', entradas=entradas)


@app.route('/inserir', methods=['POST'])
def inserir_entrada():
    if not session.get('logado'):
        abort(401)
    sql = '''insert into entradas (titulo, texto) values (?, ?)'''
    g.bd.execute(sql, [request.form['titulo'], request.form['texto']])
    g.bd.commit()
    flash('Nova entrada registrada com sucesso')
    return redirect(url_for('exibir_entradas'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            erro = 'Usuário inválido'
        else:
            session['logado'] = True
            flash('Login OK')
            return redirect(url_for('exibir_entradas'))

    return render_template('login.html', erro=erro)


@app.route('/logout')
def logout():
    session.pop('logado', None)
    flash('Logout OK')
    return redirect(url_for('exibir_entradas'))
