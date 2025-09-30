class Categoria:
    CATEGORIAS_PADRAO = {
        'receita': ['Salário', 'Freelance', 'Investimentos', 'Presente', 'Outros'],
        'despesa': ['Alimentação', 'Transporte', 'Moradia', 'Lazer', 'Saúde', 'Educação', 'Outros']
    }
    
    def __init__(self, nome: str, tipo: str, cor: str = '#000000'):
        self.nome = nome
        self.tipo = tipo
        self.cor = cor
    
    @classmethod
    def get_categorias_por_tipo(cls, tipo: str):
        return [cls(nome, tipo) for nome in cls.CATEGORIAS_PADRAO.get(tipo, [])]
