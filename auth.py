import hashlib
import secrets
import json
import os
from datetime import datetime, timedelta

class AuthService:
    def __init__(self, arquivo_usuarios='data/usuarios.json'):
        self.arquivo_usuarios = arquivo_usuarios
        self._criar_estrutura_usuarios()
    
    def _criar_estrutura_usuarios(self):
        os.makedirs(os.path.dirname(self.arquivo_usuarios), exist_ok=True)
        if not os.path.exists(self.arquivo_usuarios):
            with open(self.arquivo_usuarios, 'w') as f:
                json.dump({'usuarios': []}, f)
    
    def _carregar_usuarios(self):
        try:
            with open(self.arquivo_usuarios, 'r') as f:
                return json.load(f)
        except:
            return {'usuarios': []}
    
    def _salvar_usuarios(self, dados):
        with open(self.arquivo_usuarios, 'w') as f:
            json.dump(dados, f, indent=2)
    
    def _hash_senha(self, senha):
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def cadastrar_usuario(self, email, senha, nome):
        dados = self._carregar_usuarios()
        
        # Verificar se email já existe
        for usuario in dados['usuarios']:
            if usuario['email'] == email:
                return False, "Email já cadastrado"
        
        # Criar novo usuário
        novo_usuario = {
            'id': len(dados['usuarios']) + 1,
            'email': email,
            'senha_hash': self._hash_senha(senha),
            'nome': nome,
            'data_criacao': datetime.now().isoformat()
        }
        
        dados['usuarios'].append(novo_usuario)
        self._salvar_usuarios(dados)
        
        return True, "Usuário cadastrado com sucesso"
    
    def autenticar_usuario(self, email, senha):
        dados = self._carregar_usuarios()
        
        for usuario in dados['usuarios']:
            if usuario['email'] == email and usuario['senha_hash'] == self._hash_senha(senha):
                return True, usuario
        
        return False, "Email ou senha inválidos"
    
    def buscar_usuario_por_id(self, user_id):
        dados = self._carregar_usuarios()
        
        for usuario in dados['usuarios']:
            if usuario['id'] == user_id:
                return usuario
        
        return None
