from datetime import datetime
from typing import Literal

class Transacao:
    def __init__(self, descricao: str, valor: float, tipo: Literal['receita', 'despesa'], 
                 categoria: str, data: str = None, id: int = None):
        self.id = id
        self.descricao = descricao
        self.valor = valor
        self.tipo = tipo
        self.categoria = categoria
        self.data = data if data else datetime.now().strftime("%d/%m/%Y %H:%M")
    
    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao,
            'valor': self.valor,
            'tipo': self.tipo,
            'categoria': self.categoria,
            'data': self.data
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            descricao=data['descricao'],
            valor=data['valor'],
            tipo=data['tipo'],
            categoria=data['categoria'],
            data=data['data']
        )
