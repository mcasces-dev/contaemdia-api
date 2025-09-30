def validar_valor(valor: str) -> tuple[bool, float]:
    """Valida se o valor é um número positivo"""
    try:
        valor_float = float(valor)
        if valor_float <= 0:
            return False, 0
        return True, valor_float
    except ValueError:
        return False, 0

def validar_tipo(tipo: str) -> bool:
    """Valida se o tipo é receita ou despesa"""
    return tipo.lower() in ['receita', 'despesa']

def validar_data(data: str) -> bool:
    """Valida o formato da data"""
    try:
        from datetime import datetime
        datetime.strptime(data, "%d/%m/%Y")
        return True
    except ValueError:
        return False