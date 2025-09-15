from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///barber.db'
app.config['SECRET_KEY'] = 'sua_chave_secreta'
db = SQLAlchemy(app)

# ----------------- MODELOS -----------------
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(100), nullable=False)


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20))

class Servico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id'))
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)

    cliente = db.relationship('Cliente')
    servico = db.relationship('Servico')

class Financeiro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200))
    tipo = db.Column(db.String(10))  # entrada ou saida
    valor = db.Column(db.Float)
    data = db.Column(db.Date, default=datetime.utcnow)

# ----------------- AUTENTICAÇÃO -----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['senha']
        user = Usuario.query.filter_by(username=username, senha=senha).first()
        if user:
            session['usuario'] = user.username
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

# Decorador para proteger rotas
def login_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_view

# ----------------- ROTAS PRINCIPAIS -----------------
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# ----------------- USUÁRIOS -----------------
@app.route('/usuarios', methods=['GET', 'POST'])
@login_required
def usuarios():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['senha']

        if Usuario.query.filter_by(username=username).first():
            flash('Usuário já existe!')
        else:
            novo = Usuario(username=username, senha=senha)
            db.session.add(novo)
            db.session.commit()
            flash('Usuário cadastrado com sucesso!')
        return redirect(url_for('usuarios'))

    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    if request.method == 'POST':
        usuario.username = request.form['username']
        usuario.senha = request.form['senha']
        db.session.commit()
        flash('Usuário atualizado!')
        return redirect(url_for('usuarios'))
    return render_template('editar_usuario.html', usuario=usuario)

@app.route('/usuarios/excluir/<int:id>')
@login_required
def excluir_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuário excluído!')
    return redirect(url_for('usuarios'))

# ----------------- CLIENTES -----------------
@app.route('/clientes', methods=['GET', 'POST'])
@login_required
def clientes():
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        novo_cliente = Cliente(nome=nome, telefone=telefone)
        db.session.add(novo_cliente)
        db.session.commit()
        return redirect(url_for('clientes'))

    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)



@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == 'POST':
        cliente.nome = request.form['nome']
        cliente.telefone = request.form['telefone']
        db.session.commit()
        return redirect(url_for('clientes'))
    return render_template('editar_cliente.html', cliente=cliente)

@app.route('/clientes/excluir/<int:id>')
@login_required
def excluir_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    return redirect(url_for('clientes'))


# ----------------- SERVIÇOS -----------------
@app.route('/servicos', methods=['GET', 'POST'])
@login_required
def servicos():
    if request.method == 'POST':
        nome = request.form['nome']
        preco = float(request.form['preco'])
        novo = Servico(nome=nome, preco=preco)
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for('servicos'))
    servicos = Servico.query.all()
    return render_template('servicos.html', servicos=servicos)

@app.route('/servicos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_servico(id):
    servico = Servico.query.get_or_404(id)
    if request.method == 'POST':
        servico.nome = request.form['nome']
        servico.preco = float(request.form['preco'])
        db.session.commit()
        return redirect(url_for('servicos'))
    return render_template('editar_servico.html', servico=servico)

@app.route('/servicos/excluir/<int:id>')
@login_required
def excluir_servico(id):
    servico = Servico.query.get_or_404(id)
    db.session.delete(servico)
    db.session.commit()
    return redirect(url_for('servicos'))

# ----------------- AGENDAMENTOS -----------------
@app.route('/agendamentos', methods=['GET', 'POST'])
@login_required
def agendamentos():
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        servico_id = request.form['servico_id']
        data = request.form['data']
        hora = request.form['hora']

        hora_obj = datetime.strptime(hora, '%H:%M').time()
        data_obj = datetime.strptime(data, '%Y-%m-%d')

        if hora_obj < datetime.strptime('09:00', '%H:%M').time() or hora_obj > datetime.strptime('19:00', '%H:%M').time():
            return "<h3 style='color:red;'>Erro: Fora do horário de funcionamento (09:00 - 19:00)</h3><a href='/agendamentos'>Voltar</a>"

        conflito = Agendamento.query.filter_by(data=data_obj, hora=hora_obj).first()
        if conflito:
            return "<h3 style='color:red;'>Erro: Já existe um agendamento para esse horário!</h3><a href='/agendamentos'>Voltar</a>"

        agendamento = Agendamento(
            cliente_id=cliente_id,
            servico_id=servico_id,
            data=data_obj,
            hora=hora_obj
        )
        db.session.add(agendamento)
        db.session.commit()
        return redirect(url_for('agendamentos'))

    agendamentos = Agendamento.query.all()
    clientes = Cliente.query.all()
    servicos = Servico.query.all()
    return render_template('agendamentos.html', agendamentos=agendamentos, clientes=clientes, servicos=servicos)

# ----------------- EDITAR AGENDAMENTO -----------------
@app.route('/agendamentos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_agendamento(id):
    agendamento = Agendamento.query.get_or_404(id)
    clientes = Cliente.query.all()
    servicos = Servico.query.all()

    if request.method == 'POST':
        agendamento.cliente_id = request.form['cliente_id']
        agendamento.servico_id = request.form['servico_id']
        agendamento.data = datetime.strptime(request.form['data'], '%Y-%m-%d')
        agendamento.hora = datetime.strptime(request.form['hora'], '%H:%M').time()

        db.session.commit()
        flash('Agendamento atualizado com sucesso!')
        return redirect(url_for('agendamentos'))

    return render_template('editar_agendamento.html', agendamento=agendamento, clientes=clientes, servicos=servicos)

# ----------------- EXCLUIR AGENDAMENTO -----------------
@app.route('/agendamentos/excluir/<int:id>')
@login_required
def excluir_agendamento(id):
    agendamento = Agendamento.query.get_or_404(id)
    db.session.delete(agendamento)
    db.session.commit()
    flash('Agendamento excluído com sucesso!')
    return redirect(url_for('agendamentos'))


# ----------------- FINANCEIRO -----------------
@app.route('/financeiro', methods=['GET', 'POST'])
@login_required
def financeiro():
    if request.method == 'POST':
        descricao = request.form['descricao']
        tipo = request.form['tipo']
        valor = float(request.form['valor'])
        data = request.form['data']
        lancamento = Financeiro(
            descricao=descricao,
            tipo=tipo,
            valor=valor,
            data=datetime.strptime(data, '%Y-%m-%d')
        )
        db.session.add(lancamento)
        db.session.commit()
        return redirect(url_for('financeiro'))
    financeiro = Financeiro.query.all()
    return render_template('financeiro.html', financeiro=financeiro)

@app.route('/financeiro/excluir/<int:id>')
@login_required
def excluir_financeiro(id):
    lancamento = Financeiro.query.get_or_404(id)
    db.session.delete(lancamento)
    db.session.commit()
    return redirect(url_for('financeiro'))

# ----------------- RELATÓRIOS -----------------
@app.route('/relatorios')
@login_required
def relatorios():
    entradas = db.session.query(db.func.sum(Financeiro.valor)).filter_by(tipo='entrada').scalar() or 0
    saidas = db.session.query(db.func.sum(Financeiro.valor)).filter_by(tipo='saida').scalar() or 0
    saldo = entradas - saidas
    return render_template('relatorios.html', entradas=entradas, saidas=saidas, saldo=saldo)

@app.route('/relatorios/financeiro', methods=['GET', 'POST'])
@login_required
def relatorio_financeiro():
    entradas = 0
    saidas = 0
    saldo = 0
    registros = []

    if request.method == 'POST':
        data_inicio = request.form['data_inicio']
        data_fim = request.form['data_fim']

        registros = Financeiro.query.filter(
            Financeiro.data >= datetime.strptime(data_inicio, '%Y-%m-%d'),
            Financeiro.data <= datetime.strptime(data_fim, '%Y-%m-%d')
        ).all()

        entradas = sum(r.valor for r in registros if r.tipo == 'entrada')
        saidas = sum(r.valor for r in registros if r.tipo == 'saida')
        saldo = entradas - saidas

    return render_template(
        'relatorio_financeiro.html',
        registros=registros,
        entradas=entradas,
        saidas=saidas,
        saldo=saldo
    )import pandas as pd
import os

@app.route('/importar_financeiro', methods=['GET', 'POST'])
@login_required
def importar_financeiro():
    if request.method == 'POST':
        arquivo = request.files['arquivo']
        if arquivo and arquivo.filename.endswith('.xlsx'):
            caminho = os.path.join('uploads', arquivo.filename)
            arquivo.save(caminho)

            df = pd.read_excel(caminho)

            for _, row in df.iterrows():
                lancamento = Financeiro(
                    descricao=row['descricao'],
                    tipo=row['tipo'],
                    valor=float(row['valor']),
                    data=datetime.strptime(str(row['data']), '%Y-%m-%d')
                )
                db.session.add(lancamento)

            db.session.commit()
            os.remove(caminho)
            flash('Dados importados com sucesso!')
            return redirect(url_for('financeiro'))
        else:
            flash('Formato inválido. Envie um arquivo .xlsx')
            return redirect(url_for('importar_financeiro'))

    return render_template('importar_financeiro.html')


# ----------------- MAIN -----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if not Usuario.query.filter_by(username='admin').first():
            admin = Usuario(username='admin', senha='1234')
            db.session.add(admin)
            db.session.commit()
            print('Usuário admin criado: admin / 1234')

        app.run(debug=True)
