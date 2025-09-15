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

# ----------------- NOVO MODELO ESTOQUE -----------------
class Estoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, default=0)
    data_entrada = db.Column(db.Date, default=datetime.utcnow)

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
def index():
    return render_template('index.html')

# ----------------- ROTAS ESTOQUE -----------------
@app.route('/estoque', methods=['GET', 'POST'])
@login_required
def estoque():
    if request.method == 'POST':
        nome = request.form['nome']
        quantidade = int(request.form['quantidade'])
        novo_item = Estoque(nome=nome, quantidade=quantidade)
        db.session.add(novo_item)
        db.session.commit()
        flash('Item adicionado ao estoque!')
        return redirect(url_for('estoque'))

    itens = Estoque.query.all()
    return render_template('estoque.html', itens=itens)

@app.route('/estoque/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_estoque(id):
    item = Estoque.query.get_or_404(id)
    if request.method == 'POST':
        item.nome = request.form['nome']
        item.quantidade = int(request.form['quantidade'])
        db.session.commit()
        flash('Item atualizado!')
        return redirect(url_for('estoque'))
    return render_template('editar_estoque.html', item=item)

@app.route('/estoque/excluir/<int:id>')
@login_required
def excluir_estoque(id):
    item = Estoque.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Item excluído!')
    return redirect(url_for('estoque'))

@app.route('/estoque/remover/<int:id>', methods=['POST'])
@login_required
def remover_estoque(id):
    item = Estoque.query.get_or_404(id)
    quantidade_remover = int(request.form['quantidade'])
    if quantidade_remover > item.quantidade:
        flash('Quantidade inválida!')
    else:
        item.quantidade -= quantidade_remover
        db.session.commit()
        flash('Quantidade removida do estoque!')
    return redirect(url_for('estoque'))

# ----------------- RESTANTE DO SEU CÓDIGO ORIGINAL -----------------
# Aqui entram todas as rotas de usuários, clientes, serviços, agendamentos, financeiro, relatórios
# Copie e cole seu código original abaixo dessas funções de estoque, sem alterações.

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Usuario.query.filter_by(username='admin').first():
            admin = Usuario(username='admin', senha='1234')
            db.session.add(admin)
            db.session.commit()
            print('Usuário admin criado: admin / 1234')
        app.run(debug=True)
