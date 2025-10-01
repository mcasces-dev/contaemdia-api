from flask import Flask, render_template_string, request, redirect, jsonify, session, flash
import json
import os
from datetime import datetime
from auth import AuthService

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_muito_segura_aqui'  # Em produção, use variável de ambiente

# Serviços
auth_service = AuthService()

# HTML template - Página de Login/Cadastro
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Conta em Dia - Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            overflow: hidden;
            width: 100%;
            max-width: 400px;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .tab-container {
            display: flex;
            background: #f8f9fa;
        }
        
        .tab {
            flex: 1;
            padding: 15px;
            text-align: center;
            background: none;
            border: none;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .tab.active {
            background: white;
            color: #3498db;
            border-bottom: 3px solid #3498db;
        }
        
        .form-container {
            padding: 30px;
        }
        
        .form {
            display: none;
        }
        
        .form.active {
            display: block;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #2c3e50;
        }
        
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        input:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }
        
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .alert {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .alert-error {
            background: #ffeaa7;
            color: #d63031;
            border: 1px solid #fab1a0;
        }
        
        .alert-success {
            background: #55efc4;
            color: #00b894;
            border: 1px solid #00b894;
        }
        
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 Conta em Dia</h1>
            <p>Controle suas finanças com facilidade</p>
        </div>
        
        <div class="tab-container">
            <button class="tab active" onclick="showTab('login')">Entrar</button>
            <button class="tab" onclick="showTab('cadastro')">Cadastrar</button>
        </div>
        
        <div class="form-container">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST" action="/login" class="form active" id="loginForm">
                <div class="form-group">
                    <label for="loginEmail">Email</label>
                    <input type="email" id="loginEmail" name="email" placeholder="seu@email.com" required>
                </div>
                
                <div class="form-group">
                    <label for="loginSenha">Senha</label>
                    <input type="password" id="loginSenha" name="senha" placeholder="Sua senha" required>
                </div>
                
                <button type="submit">Entrar</button>
            </form>
            
            <form method="POST" action="/cadastrar" class="form" id="cadastroForm">
                <div class="form-group">
                    <label for="cadastroNome">Nome Completo</label>
                    <input type="text" id="cadastroNome" name="nome" placeholder="Seu nome completo" required>
                </div>
                
                <div class="form-group">
                    <label for="cadastroEmail">Email</label>
                    <input type="email" id="cadastroEmail" name="email" placeholder="seu@email.com" required>
                </div>
                
                <div class="form-group">
                    <label for="cadastroSenha">Senha</label>
                    <input type="password" id="cadastroSenha" name="senha" placeholder="Mínimo 6 caracteres" minlength="6" required>
                </div>
                
                <button type="submit">Criar Conta</button>
            </form>
            
            <div class="footer">
                <p>💡 Suas finanças organizadas em um só lugar</p>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            // Atualizar tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Mostrar form correspondente
            document.getElementById('loginForm').classList.remove('active');
            document.getElementById('cadastroForm').classList.remove('active');
            document.getElementById(tabName + 'Form').classList.add('active');
        }
        
        // Limpar mensagens de erro após 5 segundos
        setTimeout(() => {
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(alert => {
                alert.style.display = 'none';
            });
        }, 5000);
    </script>
</body>
</html>
'''

# HTML template - Dashboard (mantém o template anterior, mas atualizado)
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Conta em Dia - Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        /* Mantém todo o CSS anterior do dashboard */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .user-info {
            text-align: right;
        }
        
        .user-name {
            font-size: 1.2em;
            margin-bottom: 5px;
        }
        
        .user-email {
            font-size: 0.9em;
            color: #bdc3c7;
        }
        
        .logout-btn {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
        }
        
        .logout-btn:hover {
            background: #c0392b;
        }
        
        /* Restante do CSS mantido igual... */
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            border-left: 5px solid;
        }
        
        .saldo-card { border-left-color: #27ae60; }
        .receita-card { border-left-color: #2ecc71; }
        .despesa-card { border-left-color: #e74c3c; }
        
        .card h3 {
            font-size: 0.9em;
            color: #7f8c8d;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .card .valor {
            font-size: 1.8em;
            font-weight: bold;
        }
        
        .saldo-positivo { color: #27ae60; }
        .saldo-negativo { color: #e74c3c; }
        
        .form-section {
            padding: 20px;
            background: #f8f9fa;
            margin: 20px;
            border-radius: 10px;
        }
        
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
        }
        
        .form-group.full-width {
            grid-column: 1 / -1;
        }
        
        label {
            margin-bottom: 5px;
            font-weight: 600;
            color: #2c3e50;
        }
        
        input, select, button {
            padding: 12px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }
        
        button {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border: none;
            cursor: pointer;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .transactions {
            padding: 20px;
        }
        
        .transaction-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            margin: 10px 0;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border-left: 4px solid;
        }
        
        .transaction-receita { border-left-color: #2ecc71; }
        .transaction-despesa { border-left-color: #e74c3c; }
        
        .transaction-info {
            flex: 1;
        }
        
        .transaction-desc {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .transaction-meta {
            font-size: 0.9em;
            color: #7f8c8d;
        }
        
        .transaction-valor {
            font-weight: bold;
            font-size: 1.1em;
        }
        
        .valor-receita { color: #2ecc71; }
        .valor-despesa { color: #e74c3c; }
        
        .delete-btn {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 5px;
            cursor: pointer;
            margin-left: 10px;
        }
        
        .delete-btn:hover {
            background: #c0392b;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
        }
        
        @media (max-width: 600px) {
            .form-grid {
                grid-template-columns: 1fr;
            }
            
            .cards {
                grid-template-columns: 1fr;
            }
            
            .transaction-item {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .transaction-valor {
                margin-top: 10px;
            }
            
            .header {
                flex-direction: column;
                text-align: center;
            }
            
            .user-info {
                text-align: center;
                margin-top: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>💰 Conta em Dia</h1>
                <p>Bem-vindo de volta, {{ usuario_nome }}!</p>
            </div>
            <div class="user-info">
                <div class="user-name">{{ usuario_nome }}</div>
                <div class="user-email">{{ usuario_email }}</div>
                <form method="POST" action="/logout" style="display: inline;">
                    <button type="submit" class="logout-btn">Sair</button>
                </form>
            </div>
        </div>
        
        <div class="cards">
            <div class="card saldo-card">
                <h3>Saldo Total</h3>
                <div class="valor {{ 'saldo-positivo' if saldo >= 0 else 'saldo-negativo' }}">
                    R$ {{ "%.2f"|format(saldo) }}
                </div>
            </div>
            <div class="card receita-card">
                <h3>Receitas</h3>
                <div class="valor" style="color: #2ecc71;">R$ {{ "%.2f"|format(totais.receita) }}</div>
            </div>
            <div class="card despesa-card">
                <h3>Despesas</h3>
                <div class="valor" style="color: #e74c3c;">R$ {{ "%.2f"|format(totais.despesa) }}</div>
            </div>
        </div>

        <div class="form-section">
            <h3 style="margin-bottom: 20px; color: #2c3e50;">➕ Nova Transação</h3>
            <form method="POST" action="/add">
                <div class="form-grid">
                    <div class="form-group full-width">
                        <label for="descricao">Descrição</label>
                        <input type="text" id="descricao" name="descricao" placeholder="Ex: Salário, Aluguel, Mercado..." required>
                    </div>
                    
                    <div class="form-group">
                        <label for="valor">Valor (R$)</label>
                        <input type="number" step="0.01" id="valor" name="valor" placeholder="0.00" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="tipo">Tipo</label>
                        <select id="tipo" name="tipo" required>
                            <option value="receita">💰 Receita</option>
                            <option value="despesa">💸 Despesa</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="categoria">Categoria</label>
                        <input type="text" id="categoria" name="categoria" placeholder="Ex: Salário, Alimentação..." required>
                    </div>
                    
                    <div class="form-group full-width">
                        <button type="submit">Adicionar Transação</button>
                    </div>
                </div>
            </form>
        </div>

        <div class="transactions">
            <h3 style="margin-bottom: 20px; color: #2c3e50;">📋 Últimas Transações</h3>
            
            {% if transacoes %}
                {% for transacao in transacoes %}
                <div class="transaction-item transaction-{{ transacao.tipo }}">
                    <div class="transaction-info">
                        <div class="transaction-desc">{{ transacao.descricao }}</div>
                        <div class="transaction-meta">
                            {{ transacao.categoria }} • {{ transacao.data }}
                        </div>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div class="transaction-valor valor-{{ transacao.tipo }}">
                            R$ {{ "%.2f"|format(transacao.valor) }}
                        </div>
                        <form method="POST" action="/delete/{{ transacao.id }}" style="display: inline;">
                            <button type="submit" class="delete-btn" onclick="return confirm('Tem certeza que deseja excluir esta transação?')">×</button>
                        </form>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty-state">
                    <p>📝 Nenhuma transação cadastrada ainda.</p>
                    <p>Adicione sua primeira transação acima!</p>
                </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

class TransacaoService:
    def __init__(self):
        self._criar_estrutura_dados()
    
    def _criar_estrutura_dados(self):
        os.makedirs('data', exist_ok=True)
    
    def _get_arquivo_usuario(self, user_id):
        return f'data/transacoes_{user_id}.json'
    
    def _carregar_transacoes(self, user_id):
        arquivo = self._get_arquivo_usuario(user_id)
        try:
            with open(arquivo, 'r') as f:
                return json.load(f)
        except:
            return {'transacoes': [], 'proximo_id': 1}
    
    def _salvar_transacoes(self, user_id, dados):
        arquivo = self._get_arquivo_usuario(user_id)
        with open(arquivo, 'w') as f:
            json.dump(dados, f, indent=2)
    
    def adicionar_transacao(self, user_id, descricao, valor, tipo, categoria):
        dados = self._carregar_transacoes(user_id)
        
        transacao = {
            'id': dados['proximo_id'],
            'descricao': descricao,
            'valor': float(valor),
            'tipo': tipo,
            'categoria': categoria,
            'data': datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        
        dados['proximo_id'] += 1
        dados['transacoes'].append(transacao)
        self._salvar_transacoes(user_id, dados)
        return transacao
    
    def listar_transacoes(self, user_id):
        dados = self._carregar_transacoes(user_id)
        return dados['transacoes']
    
    def excluir_transacao(self, user_id, transacao_id):
        dados = self._carregar_transacoes(user_id)
        dados['transacoes'] = [t for t in dados['transacoes'] if t['id'] != int(transacao_id)]
        self._salvar_transacoes(user_id, dados)
        return True
    
    def calcular_totais(self, user_id):
        transacoes = self.listar_transacoes(user_id)
        totais = type('Obj', (), {})()
        totais.receita = sum(t['valor'] for t in transacoes if t['tipo'] == 'receita')
        totais.despesa = sum(t['valor'] for t in transacoes if t['tipo'] == 'despesa')
        return totais

transacao_service = TransacaoService()

# Middleware para verificar autenticação
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    senha = request.form['senha']
    
    sucesso, resultado = auth_service.autenticar_usuario(email, senha)
    
    if sucesso:
        session['user_id'] = resultado['id']
        session['user_email'] = resultado['email']
        session['user_nome'] = resultado['nome']
        return redirect('/dashboard')
    else:
        flash(resultado, 'error')
        return redirect('/')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']
    
    sucesso, mensagem = auth_service.cadastrar_usuario(email, senha, nome)
    
    if sucesso:
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'error')
    
    return redirect('/')

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    transacoes = transacao_service.listar_transacoes(user_id)
    totais = transacao_service.calcular_totais(user_id)
    saldo = totais.receita - totais.despesa
    
    # Ordenar por data (mais recentes primeiro)
    transacoes_ordenadas = sorted(transacoes, key=lambda x: datetime.strptime(x['data'], "%d/%m/%Y %H:%M"), reverse=True)
    
    return render_template_string(DASHBOARD_TEMPLATE, 
                                transacoes=transacoes_ordenadas[:10],
                                totais=totais,
                                saldo=saldo,
                                usuario_nome=session['user_nome'],
                                usuario_email=session['user_email'])

@app.route('/add', methods=['POST'])
@login_required
def add_transacao():
    user_id = session['user_id']
    descricao = request.form['descricao']
    valor = request.form['valor']
    tipo = request.form['tipo']
    categoria = request.form['categoria']
    
    transacao_service.adicionar_transacao(user_id, descricao, valor, tipo, categoria)
    return redirect('/dashboard')

@app.route('/delete/<transacao_id>', methods=['POST'])
@login_required
def delete_transacao(transacao_id):
    user_id = session['user_id']
    transacao_service.excluir_transacao(user_id, transacao_id)
    return redirect('/dashboard')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
