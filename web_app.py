from flask import Flask, render_template_string, request, redirect, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# HTML template moderno
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Controle Financeiro</title>
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
            max-width: 800px;
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
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
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
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 Controle Financeiro</h1>
            <p>Gerencie suas finanças de forma simples e eficiente</p>
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

    <script>
        // Efeitos visuais simples
        document.addEventListener('DOMContentLoaded', function() {
            const inputs = document.querySelectorAll('input, select');
            inputs.forEach(input => {
                input.addEventListener('focus', function() {
                    this.style.transform = 'scale(1.02)';
                });
                input.addEventListener('blur', function() {
                    this.style.transform = 'scale(1)';
                });
            });
        });
    </script>
</body>
</html>
'''

class TransacaoService:
    def __init__(self, arquivo_dados='data/financas.json'):
        self.arquivo_dados = arquivo_dados
        self._criar_estrutura_dados()
    
    def _criar_estrutura_dados(self):
        os.makedirs(os.path.dirname(self.arquivo_dados), exist_ok=True)
        if not os.path.exists(self.arquivo_dados):
            with open(self.arquivo_dados, 'w') as f:
                json.dump({'transacoes': [], 'proximo_id': 1}, f)
    
    def _carregar_dados(self):
        try:
            with open(self.arquivo_dados, 'r') as f:
                return json.load(f)
        except:
            return {'transacoes': [], 'proximo_id': 1}
    
    def _salvar_dados(self, dados):
        with open(self.arquivo_dados, 'w') as f:
            json.dump(dados, f, indent=2)
    
    def adicionar_transacao(self, descricao, valor, tipo, categoria):
        dados = self._carregar_dados()
        
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
        self._salvar_dados(dados)
        return transacao
    
    def listar_transacoes(self):
        dados = self._carregar_dados()
        return dados['transacoes']
    
    def excluir_transacao(self, id):
        dados = self._carregar_dados()
        dados['transacoes'] = [t for t in dados['transacoes'] if t['id'] != int(id)]
        self._salvar_dados(dados)
        return True
    
    def calcular_totais(self):
        transacoes = self.listar_transacoes()
        totais = type('Obj', (), {})()
        totais.receita = sum(t['valor'] for t in transacoes if t['tipo'] == 'receita')
        totais.despesa = sum(t['valor'] for t in transacoes if t['tipo'] == 'despesa')
        return totais

service = TransacaoService()

@app.route('/')
def index():
    transacoes = service.listar_transacoes()
    totais = service.calcular_totais()
    saldo = totais.receita - totais.despesa
    
    # Ordenar por data (mais recentes primeiro)
    transacoes_ordenadas = sorted(transacoes, key=lambda x: datetime.strptime(x['data'], "%d/%m/%Y %H:%M"), reverse=True)
    
    return render_template_string(HTML_TEMPLATE, 
                                transacoes=transacoes_ordenadas[:10],  # Últimas 10 transações
                                totais=totais,
                                saldo=saldo)

@app.route('/add', methods=['POST'])
def add_transacao():
    descricao = request.form['descricao']
    valor = request.form['valor']
    tipo = request.form['tipo']
    categoria = request.form['categoria']
    
    service.adicionar_transacao(descricao, valor, tipo, categoria)
    return redirect('/')

@app.route('/delete/<id>', methods=['POST'])
def delete_transacao(id):
    service.excluir_transacao(id)
    return redirect('/')

@app.route('/api/transacoes', methods=['GET'])
def api_transacoes():
    transacoes = service.listar_transacoes()
    return jsonify(transacoes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
