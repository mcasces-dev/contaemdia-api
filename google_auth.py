import json
import os
from datetime import datetime

class GoogleAuthService:
    def __init__(self, auth_service):
        self.auth_service = auth_service
    
    def autenticar_ou_criar_usuario_google(self, user_info):
        """
        Autentica ou cria usuário a partir dos dados do Google
        user_info: dict com email, name, picture, etc.
        """
        email = user_info['email']
        nome = user_info.get('name', email.split('@')[0])
        
        # Verificar se usuário já existe
        usuario_existente = self._buscar_usuario_por_email(email)
        
        if usuario_existente:
            return True, usuario_existente
        else:
            # Criar novo usuário sem senha
            return self._criar_usuario_google(email, nome, user_info)
    
    def _buscar_usuario_por_email(self, email):
        """Busca usuário por email"""
        dados = self.auth_service._carregar_usuarios()
        
        for usuario in dados['usuarios']:
            if usuario['email'] == email:
                return usuario
        return None
    
    def _criar_usuario_google(self, email, nome, user_info):
        """Cria novo usuário com autenticação Google"""
        dados = self.auth_service._carregar_usuarios()
        
        novo_usuario = {
            'id': len(dados['usuarios']) + 1,
            'email': email,
            'nome': nome,
            'google_id': user_info.get('sub'),
            'picture': user_info.get('picture'),
            'data_criacao': datetime.now().isoformat(),
            'auth_provider': 'google'
        }
        
        dados['usuarios'].append(novo_usuario)
        self.auth_service._salvar_usuarios(dados)
        
        return True, novo_usuario
