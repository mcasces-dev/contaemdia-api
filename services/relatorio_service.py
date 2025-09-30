from typing import List, Dict
from models.transacao import Transacao
from datetime import datetime

class RelatorioService:
    def __init__(self, transacao_service):
        self.transacao_service = transacao_service
    
    def calcular_saldo_total(self) -> float:
        """Calcula o saldo total (receitas - despesas)"""
        transacoes = self.transacao_service.listar_transacoes()
        saldo = 0
        
        for transacao in transacoes:
            if transacao.tipo == 'receita':
                saldo += transacao.valor
            else:
                saldo -= transacao.valor
        
        return saldo
    
    def calcular_total_por_tipo(self) -> Dict[str, float]:
        """Calcula o total de receitas e despesas"""
        transacoes = self.transacao_service.listar_transacoes()
        totais = {'receita': 0, 'despesa': 0}
        
        for transacao in transacoes:
            totais[transacao.tipo] += transacao.valor
        
        return totais
    
    def calcular_total_por_categoria(self) -> Dict[str, Dict[str, float]]:
        """Calcula o total por categoria para cada tipo"""
        transacoes = self.transacao_service.listar_transacoes()
        categorias = {'receita': {}, 'despesa': {}}
        
        for transacao in transacoes:
            if transacao.categoria not in categorias[transacao.tipo]:
                categorias[transacao.tipo][transacao.categoria] = 0
            categorias[transacao.tipo][transacao.categoria] += transacao.valor
        
        return categorias
    
    def gerar_relatorio_mensal(self, mes: int, ano: int) -> Dict:
        """Gera relatório mensal detalhado"""
        transacoes = self.transacao_service.listar_transacoes()
        transacoes_mes = []
        
        for transacao in transacoes:
            data_transacao = datetime.strptime(transacao.data, "%d/%m/%Y %H:%M")
            if data_transacao.month == mes and data_transacao.year == ano:
                transacoes_mes.append(transacao)
        
        totais_tipo = {'receita': 0, 'despesa': 0}
        for transacao in transacoes_mes:
            totais_tipo[transacao.tipo] += transacao.valor
        
        saldo_mensal = totais_tipo['receita'] - totais_tipo['despesa']
        
        return {
            'transacoes': transacoes_mes,
            'total_receitas': totais_tipo['receita'],
            'total_despesas': totais_tipo['despesa'],
            'saldo_mensal': saldo_mensal,
            'quantidade_transacoes': len(transacoes_mes)
        }