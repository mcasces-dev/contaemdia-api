import json
import os
from typing import List, Optional
from models.transacao import Transacao

class TransacaoService:
    def __init__(self, arquivo_dados: str = 'data/financas.json'):
        self.arquivo_dados = arquivo_dados
        self._criar_estrutura_dados()
    
    def _criar_estrutura_dados(self):
        """Cria a estrutura de diretórios e arquivo se não existir"""
        os.makedirs(os.path.dirname(self.arquivo_dados), exist_ok=True)
        if not os.path.exists(self.arquivo_dados):
            with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
                json.dump({'transacoes': [], 'proximo_id': 1}, f, ensure_ascii=False, indent=2)
    
    def _carregar_dados(self):
        """Carrega os dados do arquivo JSON"""
        try:
            with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'transacoes': [], 'proximo_id': 1}
    
    def _salvar_dados(self, dados):
        """Salva os dados no arquivo JSON"""
        with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    
    def adicionar_transacao(self, transacao: Transacao) -> Transacao:
        """Adiciona uma nova transação"""
        dados = self._carregar_dados()
        
        transacao.id = dados['proximo_id']
        dados['proximo_id'] += 1
        
        dados['transacoes'].append(transacao.to_dict())
        self._salvar_dados(dados)
        
        return transacao
    
    def listar_transacoes(self) -> List[Transacao]:
        """Lista todas as transações"""
        dados = self._carregar_dados()
        return [Transacao.from_dict(t) for t in dados['transacoes']]
    
    def buscar_transacao_por_id(self, id: int) -> Optional[Transacao]:
        """Busca uma transação pelo ID"""
        dados = self._carregar_dados()
        for transacao_dict in dados['transacoes']:
            if transacao_dict['id'] == id:
                return Transacao.from_dict(transacao_dict)
        return None
    
    def atualizar_transacao(self, id: int, **kwargs) -> Optional[Transacao]:
        """Atualiza uma transação existente"""
        dados = self._carregar_dados()
        
        for transacao_dict in dados['transacoes']:
            if transacao_dict['id'] == id:
                for key, value in kwargs.items():
                    if key in transacao_dict and key != 'id':
                        transacao_dict[key] = value
                
                self._salvar_dados(dados)
                return Transacao.from_dict(transacao_dict)
        
        return None
    
    def excluir_transacao(self, id: int) -> bool:
        """Exclui uma transação"""
        dados = self._carregar_dados()
        
        for i, transacao_dict in enumerate(dados['transacoes']):
            if transacao_dict['id'] == id:
                dados['transacoes'].pop(i)
                self._salvar_dados(dados)
                return True
        
        return False
    
    def filtrar_transacoes(self, tipo: str = None, categoria: str = None) -> List[Transacao]:
        """Filtra transações por tipo e/ou categoria"""
        transacoes = self.listar_transacoes()
        
        if tipo:
            transacoes = [t for t in transacoes if t.tipo == tipo]
        if categoria:
            transacoes = [t for t in transacoes if t.categoria == categoria]
        
        return transacoes
