from flask import Flask, render_template_string, request, redirect, jsonify, session, flash, url_for
import json
import os
from datetime import datetime
from auth import AuthService

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'chave_secreta_padrao_mudar_em_producao')

# Configurações Google OAuth (simplificado)
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_ENABLED = bool(GOOGLE_CLIENT_ID)

# Serviços
auth_service = AuthService()
transacao_service = None

# Categorias fixas
CATEGORIAS_FIXAS = {
    'receita': [
        'Salário', 'Freelance', 'Investimentos', 'Bonificação', 
        'Vendas', 'Aluguel Recebido', 'Dividendos', 'Outros'
    ],
    'despesa': [
        'Alimentação', 'Transporte', 'Moradia', 'Lazer', 
        'Saúde', 'Educação', 'Compras', 'Serviços',
        'Impostos', 'Seguros', 'Viagens', 'Outros'
    ]
}

# Inicializar serviço de transações
class TransacaoService:
    def __init__(self):
        self._criar_estrutura_dados()
        self.categorias = CATEGORIAS_FIXAS
    
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
        # Validar categoria
        if categoria not in self.categorias[tipo]:
            categoria = 'Outros'
            
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
    
    def gerar_relatorio_categorias(self, user_id):
        """Gera relatório agrupado por categoria"""
        transacoes = self.listar_transacoes(user_id)
        relatorio = {'receita': {}, 'despesa': {}}
        
        # Inicializar todas as categorias com 0
        for categoria in self.categorias['receita']:
            relatorio['receita'][categoria] = 0
        for categoria in self.categorias['despesa']:
            relatorio['despesa'][categoria] = 0
        
        # Somar valores por categoria
        for transacao in transacoes:
            categoria = transacao['categoria']
            if categoria in relatorio[transacao['tipo']]:
                relatorio[transacao['tipo']][categoria] += transacao['valor']
            else:
                # Se categoria não existir na lista fixa, agrupa em "Outros"
                relatorio[transacao['tipo']]['Outros'] += transacao['valor']
        
        # Remover categorias com valor 0
        relatorio['receita'] = {k: v for k, v in relatorio['receita'].items() if v > 0}
        relatorio['despesa'] = {k: v for k, v in relatorio['despesa'].items() if v > 0}
        
        return relatorio
    
    def obter_dados_grafico_pizza(self, user_id):
        """Obtém dados para gráfico de pizza por categoria"""
        relatorio = self.gerar_relatorio_categorias(user_id)
        
        dados_receitas = {
            'labels': list(relatorio['receita'].keys()),
            'valores': list(relatorio['receita'].values()),
            'cores': ['#2ecc71', '#27ae60', '#1abc9c', '#16a085', '#3498db', '#2980b9', '#8e44ad', '#9b59b6']
        }
        
        dados_despesas = {
            'labels': list(relatorio['despesa'].keys()),
            'valores': list(relatorio['despesa'].values()),
            'cores': ['#e74c3c', '#c0392b', '#d35400', '#e67e22', '#f39c12', '#f1c40f', '#34495e', '#2c3e50']
        }
        
        return {
            'receitas': dados_receitas,
            'despesas': dados_despesas
        }
    
    def obter_dados_grafico_barras(self, user_id):
        """Obtém dados para gráfico de barras mensal"""
        transacoes = self.listar_transacoes(user_id)
        
        # Agrupar por mês
        meses = {}
        for transacao in transacoes:
            data = datetime.strptime(transacao['data'], "%d/%m/%Y %H:%M")
            mes_ano = data.strftime("%m/%Y")
            
            if mes_ano not in meses:
                meses[mes_ano] = {'receita': 0, 'despesa': 0}
            
            meses[mes_ano][transacao['tipo']] += transacao['valor']
        
        # Ordenar por data
        meses_ordenados = sorted(meses.items(), key=lambda x: datetime.strptime(x[0], "%m/%Y"))
        
        labels = [f"{datetime.strptime(mes, '%m/%Y').strftime('%b/%Y')}" for mes, _ in meses_ordenados[-6:]]  # Últimos 6 meses
        receitas = [dados['receita'] for _, dados in meses_ordenados[-6:]]
        despesas = [dados['despesa'] for _, dados in meses_ordenados[-6:]]
        
        return {
            'labels': labels,
            'receitas': receitas,
            'despesas': despesas
        }

# Inicializar após definir a classe
transacao_service = TransacaoService()

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
            max-width: 450px;
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
        
        input, select {
            width: 100%;
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
        
        .btn {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            display: block;
            text-decoration: none;
            margin-bottom: 10px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
        }
        
        .btn-google {
            background: white;
            color: #333;
            border: 2px solid #e1e8ed;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .btn-google:hover {
            border-color: #db4437;
            background: #f8f9fa;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .divider {
            text-align: center;
            margin: 20px 0;
            position: relative;
            color: #7f8c8d;
        }
        
        .divider::before {
            content: "";
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 1px;
            background: #e1e8ed;
            z-index: 1;
        }
        
        .divider span {
            background: white;
            padding: 0 15px;
            position: relative;
            z-index: 2;
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
        
        .alert-info {
            background: #81ecec;
            color: #00cec9;
            border: 1px solid #00cec9;
        }
        
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #7f8c8d;
        }
        
        .google-icon {
            width: 18px;
            height: 18px;
        }
        
        .google-btn-container {
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 Conta em Dia</h1>
            <p>Controle suas finanças com facilidade</p>
        </div>
        
        <div class="form-container">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <!-- Botão Google -->
            {% if google_enabled %}
            <div class="google-btn-container">
                <a href="/login/google" class="btn btn-google">
                    <svg class="google-icon" viewBox="0 0 24 24">
                        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                    </svg>
                    Entrar com Google
                </a>
            </div>
            
            <div class="divider">
                <span>ou</span>
            </div>
            {% endif %}
            
            <div class="tab-container">
                <button class="tab active" onclick="showTab('login')">Entrar</button>
                <button class="tab" onclick="showTab('cadastro')">Cadastrar</button>
            </div>
            
            <form method="POST" action="/login" class="form active" id="loginForm">
                <div class="form-group">
                    <label for="loginEmail">Email</label>
                    <input type="email" id="loginEmail" name="email" placeholder="seu@email.com" required>
                </div>
                
                <div class="form-group">
                    <label for="loginSenha">Senha</label>
                    <input type="password" id="loginSenha" name="senha" placeholder="Sua senha" required>
                </div>
                
                <button type="submit" class="btn btn-primary">Entrar</button>
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
                
                <button type="submit" class="btn btn-primary">Criar Conta</button>
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

# HTML template - Dashboard atualizado com gráficos
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Conta em Dia - Dashboard</title>
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
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
        }
        
        .logout-btn:hover {
            background: #c0392b;
        }
        
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
        
        .nav-tabs {
            display: flex;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 5px;
            margin: 20px;
        }
        
        .nav-tab {
            flex: 1;
            padding: 12px;
            text-align: center;
            background: none;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .nav-tab.active {
            background: white;
            color: #3498db;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .tab-content {
            display: none;
            padding: 0 20px 20px;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .relatorio-categoria {
            margin: 15px 0;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .categoria-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .categoria-nome {
            font-weight: 600;
            color: #2c3e50;
        }
        
        .categoria-valor {
            font-weight: bold;
        }
        
        .barra-progresso {
            height: 8px;
            background: #ecf0f1;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .barra-progresso-inner {
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        
        .barra-receita { background: linear-gradient(90deg, #2ecc71, #27ae60); }
        .barra-despesa { background: linear-gradient(90deg, #e74c3c, #c0392b); }
        
        .categoria-vazia {
            text-align: center;
            padding: 20px;
            color: #7f8c8d;
        }
        
        /* Estilos para gráficos */
        .grafico-conteudo {
            display: none;
        }
        
        .grafico-conteudo.active {
            display: block;
        }
        
        canvas {
            max-width: 100%;
            height: auto;
        }
        
        .grafico-container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
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
                {% if usuario_picture %}
                <img src="{{ usuario_picture }}" alt="Foto" style="width: 40px; height: 40px; border-radius: 50%; margin-right: 10px;">
                {% endif %}
                <div class="user-name">{{ usuario_nome }}</div>
                <div class="user-email">{{ usuario_email }}</div>
                <a href="/logout" class="logout-btn" onclick="return confirm('Tem certeza que deseja sair?')">Sair</a>
            </div>
        </div>
        
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('dashboard')">Dashboard</button>
            <button class="nav-tab" onclick="showTab('relatorios')">Relatórios</button>
        </div>
        
        <!-- Tab Dashboard -->
        <div id="dashboard" class="tab-content active">
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
                            <select id="tipo" name="tipo" required onchange="atualizarCategorias()">
                                <option value="receita">💰 Receita</option>
                                <option value="despesa">💸 Despesa</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="categoria">Categoria</label>
                            <select id="categoria" name="categoria" required>
                                {% for categoria in categorias.receita %}
                                <option value="{{ categoria }}">{{ categoria }}</option>
                                {% endfor %}
                            </select>
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
        
        <!-- Tab Relatórios -->
        <div id="relatorios" class="tab-content">
            <h3 style="margin: 20px 0; color: #2c3e50;">📊 Relatórios e Gráficos</h3>
            
            <!-- Abas de gráficos -->
            <div class="nav-tabs" style="margin: 20px 0;">
                <button class="nav-tab active" onclick="mostrarGrafico('categorias')">Por Categorias</button>
                <button class="nav-tab" onclick="mostrarGrafico('mensal')">Evolução Mensal</button>
                <button class="nav-tab" onclick="mostrarGrafico('detalhes')">Detalhado</button>
            </div>
            
            <!-- Container dos gráficos -->
            <div id="grafico-container" style="background: white; border-radius: 10px; padding: 20px; margin: 20px 0;">
                <!-- Gráfico de Pizza por Categorias -->
                <div id="grafico-categorias" class="grafico-conteudo active">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div>
                            <h4 style="color: #27ae60; margin-bottom: 15px; text-align: center;">💰 Receitas por Categoria</h4>
                            <canvas id="pizzaReceitas" width="400" height="300"></canvas>
                        </div>
                        <div>
                            <h4 style="color: #e74c3c; margin-bottom: 15px; text-align: center;">💸 Despesas por Categoria</h4>
                            <canvas id="pizzaDespesas" width="400" height="300"></canvas>
                        </div>
                    </div>
                </div>
                
                <!-- Gráfico de Barras Mensal -->
                <div id="grafico-mensal" class="grafico-conteudo">
                    <h4 style="text-align: center; margin-bottom: 20px; color: #2c3e50;">📈 Evolução Mensal</h4>
                    <canvas id="barrasMensal" width="800" height="400"></canvas>
                </div>
                
                <!-- Relatório Detalhado -->
                <div id="grafico-detalhes" class="grafico-conteudo">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <!-- Receitas -->
                        <div>
                            <h4 style="color: #27ae60; margin-bottom: 15px;">💰 Receitas</h4>
                            {% if relatorio.receita %}
                                {% for categoria, valor in relatorio.receita.items() %}
                                <div class="relatorio-categoria">
                                    <div class="categoria-header">
                                        <span class="categoria-nome">{{ categoria }}</span>
                                        <span class="categoria-valor" style="color: #27ae60;">R$ {{ "%.2f"|format(valor) }}</span>
                                    </div>
                                    <div class="barra-progresso">
                                        <div class="barra-progresso-inner barra-receita" 
                                             style="width: {{ (valor / totais.receita * 100) if totais.receita > 0 else 0 }}%"></div>
                                    </div>
                                </div>
                                {% endfor %}
                            {% else %}
                                <div class="categoria-vazia">Nenhuma receita cadastrada</div>
                            {% endif %}
                        </div>
                        
                        <!-- Despesas -->
                        <div>
                            <h4 style="color: #e74c3c; margin-bottom: 15px;">💸 Despesas</h4>
                            {% if relatorio.despesa %}
                                {% for categoria, valor in relatorio.despesa.items() %}
                                <div class="relatorio-categoria">
                                    <div class="categoria-header">
                                        <span class="categoria-nome">{{ categoria }}</span>
                                        <span class="categoria-valor" style="color: #e74c3c;">R$ {{ "%.2f"|format(valor) }}</span>
                                    </div>
                                    <div class="barra-progresso">
                                        <div class="barra-progresso-inner barra-despesa" 
                                             style="width: {{ (valor / totais.despesa * 100) if totais.despesa > 0 else 0 }}%"></div>
                                    </div>
                                </div>
                                {% endfor %}
                            {% else %}
                                <div class="categoria-vazia">Nenhuma despesa cadastrada</div>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        let pizzaReceitasChart = null;
        let pizzaDespesasChart = null;
        let barrasMensalChart = null;

        function showTab(tabName) {
            // Atualizar tabs
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Mostrar conteúdo correspondente
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(tabName).classList.add('active');
        }

        function mostrarGrafico(tipo) {
            // Atualizar tabs
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Mostrar conteúdo correspondente
            document.querySelectorAll('.grafico-conteudo').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById('grafico-' + tipo).classList.add('active');
            
            // Carregar gráficos quando forem mostrados
            if (tipo === 'categorias' && !pizzaReceitasChart) {
                carregarGraficosPizza();
            } else if (tipo === 'mensal' && !barrasMensalChart) {
                carregarGraficoBarras();
            }
        }

        function carregarGraficosPizza() {
            fetch('/api/graficos/pizza')
                .then(response => response.json())
                .then(dados => {
                    // Gráfico de Pizza - Receitas
                    if (dados.receitas.labels.length > 0) {
                        const ctxReceitas = document.getElementById('pizzaReceitas').getContext('2d');
                        pizzaReceitasChart = new Chart(ctxReceitas, {
                            type: 'pie',
                            data: {
                                labels: dados.receitas.labels,
                                datasets: [{
                                    data: dados.receitas.valores,
                                    backgroundColor: dados.receitas.cores,
                                    borderWidth: 2,
                                    borderColor: '#fff'
                                }]
                            },
                            options: {
                                responsive: true,
                                plugins: {
                                    legend: {
                                        position: 'bottom',
                                        labels: {
                                            padding: 20,
                                            usePointStyle: true
                                        }
                                    },
                                    tooltip: {
                                        callbacks: {
                                            label: function(context) {
                                                const label = context.label || '';
                                                const value = context.raw || 0;
                                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                                const percentage = Math.round((value / total) * 100);
                                                return `${label}: R$ ${value.toFixed(2)} (${percentage}%)`;
                                            }
                                        }
                                    }
                                }
                            }
                        });
                    } else {
                        document.getElementById('pizzaReceitas').innerHTML = '<div class="categoria-vazia">Nenhuma receita para exibir</div>';
                    }

                    // Gráfico de Pizza - Despesas
                    if (dados.despesas.labels.length > 0) {
                        const ctxDespesas = document.getElementById('pizzaDespesas').getContext('2d');
                        pizzaDespesasChart = new Chart(ctxDespesas, {
                            type: 'pie',
                            data: {
                                labels: dados.despesas.labels,
                                datasets: [{
                                    data: dados.despesas.valores,
                                    backgroundColor: dados.despesas.cores,
                                    borderWidth: 2,
                                    borderColor: '#fff'
                                }]
                            },
                            options: {
                                responsive: true,
                                plugins: {
                                    legend: {
                                        position: 'bottom',
                                        labels: {
                                            padding: 20,
                                            usePointStyle: true
                                        }
                                    },
                                    tooltip: {
                                        callbacks: {
                                            label: function(context) {
                                                const label = context.label || '';
                                                const value = context.raw || 0;
                                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                                const percentage = Math.round((value / total) * 100);
                                                return `${label}: R$ ${value.toFixed(2)} (${percentage}%)`;
                                            }
                                        }
                                    }
                                }
                            }
                        });
                    } else {
                        document.getElementById('pizzaDespesas').innerHTML = '<div class="categoria-vazia">Nenhuma despesa para exibir</div>';
                    }
                })
                .catch(error => {
                    console.error('Erro ao carregar gráficos:', error);
                });
        }

        function carregarGraficoBarras() {
            fetch('/api/graficos/barras')
                .then(response => response.json())
                .then(dados => {
                    if (dados.labels.length > 0) {
                        const ctx = document.getElementById('barrasMensal').getContext('2d');
                        barrasMensalChart = new Chart(ctx, {
                            type: 'bar',
                            data: {
                                labels: dados.labels,
                                datasets: [
                                    {
                                        label: 'Receitas',
                                        data: dados.receitas,
                                        backgroundColor: '#2ecc71',
                                        borderColor: '#27ae60',
                                        borderWidth: 1
                                    },
                                    {
                                        label: 'Despesas',
                                        data: dados.despesas,
                                        backgroundColor: '#e74c3c',
                                        borderColor: '#c0392b',
                                        borderWidth: 1
                                    }
                                ]
                            },
                            options: {
                                responsive: true,
                                scales: {
                                    y: {
                                        beginAtZero: true,
                                        ticks: {
                                            callback: function(value) {
                                                return 'R$ ' + value.toFixed(2);
                                            }
                                        }
                                    }
                                },
                                plugins: {
                                    tooltip: {
                                        callbacks: {
                                            label: function(context) {
                                                return context.dataset.label + ': R$ ' + context.raw.toFixed(2);
                                            }
                                        }
                                    }
                                }
                            }
                        });
                    } else {
                        document.getElementById('barrasMensal').innerHTML = '<div class="categoria-vazia">Dados insuficientes para gráfico mensal</div>';
                    }
                })
                .catch(error => {
                    console.error('Erro ao carregar gráfico de barras:', error);
                });
        }

        function atualizarCategorias() {
            const tipo = document.getElementById('tipo').value;
            const categoriaSelect = document.getElementById('categoria');
            const categorias = {{ categorias|tojson }};
            
            // Limpar opções atuais
            categoriaSelect.innerHTML = '';
            
            // Adicionar novas opções baseadas no tipo
            categorias[tipo].forEach(cat => {
                const option = document.createElement('option');
                option.value = cat;
                option.textContent = cat;
                categoriaSelect.appendChild(option);
            });
        }
        
        // Inicializar categorias quando a página carregar
        document.addEventListener('DOMContentLoaded', function() {
            atualizarCategorias();
            
            // Carregar gráfico de pizza por padrão
            setTimeout(() => {
                if (document.getElementById('grafico-categorias').classList.contains('active')) {
                    carregarGraficosPizza();
                }
            }, 1000);
        });
    </script>
</body>
</html>
'''

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
    return render_template_string(LOGIN_TEMPLATE, google_enabled=GOOGLE_ENABLED)

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    senha = request.form['senha']
    
    sucesso, resultado = auth_service.autenticar_usuario(email, senha)
    
    if sucesso:
        session['user_id'] = resultado['id']
        session['user_email'] = resultado['email']
        session['user_nome'] = resultado['nome']
        session['user_picture'] = resultado.get('picture')
        return redirect('/dashboard')
    else:
        flash(resultado, 'error')
        return redirect('/')

@app.route('/login/google')
def login_google():
    if not GOOGLE_ENABLED:
        flash('Login com Google não configurado. Use o login tradicional.', 'info')
        return redirect('/')
    
    # URL de autorização do Google (simplificada)
    authorization_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        "scope=email%20profile&"
        f"response_type=code&"
        f"redirect_uri=https://contaemdia-api.onrender.com/login/google/callback&"
        f"client_id={GOOGLE_CLIENT_ID}"
    )
    
    return redirect(authorization_url)

@app.route('/login/google/callback')
def google_callback():
    flash('Login com Google em desenvolvimento. Use o login tradicional por enquanto.', 'info')
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
    relatorio = transacao_service.gerar_relatorio_categorias(user_id)
    
    # Ordenar por data (mais recentes primeiro)
    transacoes_ordenadas = sorted(transacoes, key=lambda x: datetime.strptime(x['data'], "%d/%m/%Y %H:%M"), reverse=True)
    
    return render_template_string(DASHBOARD_TEMPLATE, 
                                transacoes=transacoes_ordenadas[:10],
                                totais=totais,
                                saldo=saldo,
                                relatorio=relatorio,
                                categorias=CATEGORIAS_FIXAS,
                                usuario_nome=session['user_nome'],
                                usuario_email=session['user_email'],
                                usuario_picture=session.get('user_picture'))

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

@app.route('/api/graficos/<tipo>')
@login_required
def api_graficos(tipo):
    user_id = session['user_id']
    
    if tipo == 'pizza':
        dados = transacao_service.obter_dados_grafico_pizza(user_id)
    elif tipo == 'barras':
        dados = transacao_service.obter_dados_grafico_barras(user_id)
    else:
        return jsonify({'error': 'Tipo de gráfico inválido'}), 400
    
    return jsonify(dados)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('Você saiu da sua conta com sucesso!', 'info')
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
