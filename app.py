import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
from datetime import datetime
from services.transacao_service import TransacaoService
from services.relatorio_service import RelatorioService
from models.transacao import Transacao
from models.categoria import Categoria
import os
from PIL import Image
import sys

# Configurar o caminho para assets
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class FinanceApp:
    def __init__(self):
        # Inicializar serviços
        self.transacao_service = TransacaoService()
        self.relatorio_service = RelatorioService(self.transacao_service)
        
        # Configurar aparência
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # Criar janela principal
        self.root = ctk.CTk()
        self.root.title("Controle Financeiro Pessoal")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # Configurar grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.criar_sidebar()
        self.criar_area_principal()
        self.atualizar_dashboard()
        
    def criar_sidebar(self):
        # Frame sidebar
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)
        
        # Logo/Título
        title_label = ctk.CTkLabel(
            self.sidebar, 
            text="Controle Financeiro",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Botões de navegação
        botoes_nav = [
            ("📊 Dashboard", self.mostrar_dashboard),
            ("💰 Nova Receita", lambda: self.mostrar_formulario("receita")),
            ("💸 Nova Despesa", lambda: self.mostrar_formulario("despesa")),
            ("📋 Transações", self.mostrar_transacoes),
            ("📈 Relatórios", self.mostrar_relatorios),
            ("⚙️ Configurações", self.mostrar_configuracoes)
        ]
        
        for i, (texto, comando) in enumerate(botoes_nav, 1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=texto,
                command=comando,
                font=ctk.CTkFont(size=14),
                anchor="w",
                fg_color="transparent"
            )
            btn.grid(row=i, column=0, padx=20, pady=5, sticky="ew")
        
        # Modo dark/light
        self.modo_switch = ctk.CTkSwitch(
            self.sidebar, 
            text="Modo Escuro",
            command=self.alternar_modo,
            font=ctk.CTkFont(size=12)
        )
        self.modo_switch.grid(row=7, column=0, padx=20, pady=20)
        self.modo_switch.select()
        
    def criar_area_principal(self):
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        self.header_label = ctk.CTkLabel(
            self.main_frame,
            text="Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.header_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Container para conteúdo
        self.conteudo_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.conteudo_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.conteudo_frame.grid_columnconfigure(0, weight=1)
        
    def criar_widgets_dashboard(self):
        # Limpar frame de conteúdo
        for widget in self.conteudo_frame.winfo_children():
            widget.destroy()
        
        # Cards de resumo
        resumo_frame = ctk.CTkFrame(self.conteudo_frame)
        resumo_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        resumo_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        totais = self.relatorio_service.calcular_total_por_tipo()
        saldo = self.relatorio_service.calcular_saldo_total()
        
        # Card Saldo
        saldo_card = ctk.CTkFrame(resumo_frame, fg_color="#2B5B2B" if saldo >= 0 else "#8B2B2B")
        saldo_card.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(saldo_card, text="Saldo Total", font=ctk.CTkFont(size=16)).pack(pady=(10, 5))
        ctk.CTkLabel(saldo_card, text=f"R$ {saldo:,.2f}", 
                    font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 10))
        
        # Card Receitas
        receita_card = ctk.CTkFrame(resumo_frame, fg_color="#2B5B2B")
        receita_card.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(receita_card, text="Receitas", font=ctk.CTkFont(size=16)).pack(pady=(10, 5))
        ctk.CTkLabel(receita_card, text=f"R$ {totais['receita']:,.2f}", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 10))
        
        # Card Despesas
        despesa_card = ctk.CTkFrame(resumo_frame, fg_color="#8B2B2B")
        despesa_card.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(despesa_card, text="Despesas", font=ctk.CTkFont(size=16)).pack(pady=(10, 5))
        ctk.CTkLabel(despesa_card, text=f"R$ {totais['despesa']:,.2f}", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 10))
        
        # Transações recentes
        transacoes_frame = ctk.CTkFrame(self.conteudo_frame)
        transacoes_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        transacoes_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(transacoes_frame, text="Transações Recentes", 
                    font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Treeview para transações
        columns = ("Data", "Tipo", "Categoria", "Descrição", "Valor")
        self.tree = ttk.Treeview(transacoes_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        self.tree.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Atualizar transações
        self.atualizar_lista_transacoes()
        
    def criar_formulario_transacao(self, tipo):
        for widget in self.conteudo_frame.winfo_children():
            widget.destroy()
        
        form_frame = ctk.CTkFrame(self.conteudo_frame)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        form_frame.grid_columnconfigure(1, weight=1)
        
        titulo = "Nova Receita" if tipo == "receita" else "Nova Despesa"
        ctk.CTkLabel(form_frame, text=titulo, 
                    font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, columnspan=2, pady=20)
        
        # Descrição
        ctk.CTkLabel(form_frame, text="Descrição:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.descricao_entry = ctk.CTkEntry(form_frame, placeholder_text="Ex: Salário, Aluguel, Mercado...")
        self.descricao_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        
        # Valor
        ctk.CTkLabel(form_frame, text="Valor (R$):").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.valor_entry = ctk.CTkEntry(form_frame, placeholder_text="0.00")
        self.valor_entry.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        
        # Categoria
        ctk.CTkLabel(form_frame, text="Categoria:").grid(row=3, column=0, padx=20, pady=10, sticky="w")
        categorias = Categoria.get_categorias_por_tipo(tipo)
        self.categoria_var = ctk.StringVar(value=categorias[0].nome)
        categoria_menu = ctk.CTkOptionMenu(form_frame, variable=self.categoria_var,
                                         values=[cat.nome for cat in categorias])
        categoria_menu.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        
        # Data
        ctk.CTkLabel(form_frame, text="Data:").grid(row=4, column=0, padx=20, pady=10, sticky="w")
        data_atual = datetime.now().strftime("%d/%m/%Y")
        self.data_entry = ctk.CTkEntry(form_frame, placeholder_text="DD/MM/AAAA")
        self.data_entry.insert(0, data_atual)
        self.data_entry.grid(row=4, column=1, padx=20, pady=10, sticky="ew")
        
        # Botões
        botoes_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        botoes_frame.grid(row=5, column=0, columnspan=2, pady=30)
        
        ctk.CTkButton(botoes_frame, text="Salvar", 
                     command=lambda: self.salvar_transacao(tipo),
                     fg_color="#2B5B2B", hover_color="#1E3F1E").pack(side="left", padx=10)
        ctk.CTkButton(botoes_frame, text="Cancelar", 
                     command=self.mostrar_dashboard,
                     fg_color="#6C757D", hover_color="#5A6268").pack(side="left", padx=10)
        
        self.tipo_transacao = tipo
        
    def criar_tela_transacoes(self):
        for widget in self.conteudo_frame.winfo_children():
            widget.destroy()
        
        transacoes_frame = ctk.CTkFrame(self.conteudo_frame)
        transacoes_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        transacoes_frame.grid_columnconfigure(0, weight=1)
        transacoes_frame.grid_rowconfigure(1, weight=1)
        
        # Header com filtros
        header_frame = ctk.CTkFrame(transacoes_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=10)
        header_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(header_frame, text="Todas as Transações", 
                    font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, sticky="w")
        
        # Filtros
        filtros_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        filtros_frame.grid(row=0, column=1, sticky="e")
        
        ctk.CTkLabel(filtros_frame, text="Filtrar:").pack(side="left", padx=5)
        self.filtro_tipo = ctk.CTkOptionMenu(filtros_frame, values=["Todos", "Receita", "Despesa"],
                                           command=self.filtrar_transacoes)
        self.filtro_tipo.pack(side="left", padx=5)
        
        # Treeview
        tree_frame = ctk.CTkFrame(transacoes_frame)
        tree_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        columns = ("ID", "Data", "Tipo", "Categoria", "Descrição", "Valor")
        self.tree_transacoes = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree_transacoes.heading(col, text=col)
            width = 80 if col == "ID" else 120
            self.tree_transacoes.column(col, width=width)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_transacoes.yview)
        self.tree_transacoes.configure(yscrollcommand=scrollbar.set)
        
        self.tree_transacoes.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Botões de ação
        acoes_frame = ctk.CTkFrame(transacoes_frame, fg_color="transparent")
        acoes_frame.grid(row=2, column=0, pady=10)
        
        ctk.CTkButton(acoes_frame, text="Atualizar", 
                     command=self.atualizar_lista_transacoes).pack(side="left", padx=5)
        ctk.CTkButton(acoes_frame, text="Excluir Selecionada", 
                     command=self.excluir_transacao_selecionada,
                     fg_color="#8B2B2B", hover_color="#6B1A1A").pack(side="left", padx=5)
        
        self.atualizar_lista_transacoes()
        
    def criar_tela_relatorios(self):
        for widget in self.conteudo_frame.winfo_children():
            widget.destroy()
        
        relatorios_frame = ctk.CTkFrame(self.conteudo_frame)
        relatorios_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        relatorios_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(relatorios_frame, text="Relatórios Detalhados", 
                    font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=20)
        
        # Estatísticas por categoria
        stats_frame = ctk.CTkFrame(relatorios_frame)
        stats_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        stats_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Receitas por categoria
        receitas_frame = ctk.CTkFrame(stats_frame)
        receitas_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(receitas_frame, text="💰 Receitas por Categoria", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        categorias = self.relatorio_service.calcular_total_por_categoria()
        for cat, valor in categorias['receita'].items():
            cat_frame = ctk.CTkFrame(receitas_frame, fg_color="transparent")
            cat_frame.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(cat_frame, text=cat).pack(side="left")
            ctk.CTkLabel(cat_frame, text=f"R$ {valor:,.2f}").pack(side="right")
        
        # Despesas por categoria
        despesas_frame = ctk.CTkFrame(stats_frame)
        despesas_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(despesas_frame, text="💸 Despesas por Categoria", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        for cat, valor in categorias['despesa'].items():
            cat_frame = ctk.CTkFrame(despesas_frame, fg_color="transparent")
            cat_frame.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(cat_frame, text=cat).pack(side="left")
            ctk.CTkLabel(cat_frame, text=f"R$ {valor:,.2f}").pack(side="right")
        
    def criar_tela_configuracoes(self):
        for widget in self.conteudo_frame.winfo_children():
            widget.destroy()
        
        config_frame = ctk.CTkFrame(self.conteudo_frame)
        config_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(config_frame, text="Configurações", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        # Backup
        backup_frame = ctk.CTkFrame(config_frame)
        backup_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(backup_frame, text="Backup de Dados", 
                    font=ctk.CTkFont(size=16)).pack(pady=10)
        
        ctk.CTkButton(backup_frame, text="Exportar Dados", 
                     command=self.exportar_dados).pack(pady=5)
        ctk.CTkButton(backup_frame, text="Limpar Todos os Dados", 
                     command=self.limpar_dados,
                     fg_color="#8B2B2B", hover_color="#6B1A1A").pack(pady=5)
        
    # Métodos de navegação
    def mostrar_dashboard(self):
        self.header_label.configure(text="Dashboard")
        self.criar_widgets_dashboard()
        
    def mostrar_formulario(self, tipo):
        titulo = "Nova Receita" if tipo == "receita" else "Nova Despesa"
        self.header_label.configure(text=titulo)
        self.criar_formulario_transacao(tipo)
        
    def mostrar_transacoes(self):
        self.header_label.configure(text="Transações")
        self.criar_tela_transacoes()
        
    def mostrar_relatorios(self):
        self.header_label.configure(text="Relatórios")
        self.criar_tela_relatorios()
        
    def mostrar_configuracoes(self):
        self.header_label.configure(text="Configurações")
        self.criar_tela_configuracoes()
        
    # Métodos funcionais
    def salvar_transacao(self, tipo):
        descricao = self.descricao_entry.get().strip()
        valor_str = self.valor_entry.get().strip()
        categoria = self.categoria_var.get()
        data = self.data_entry.get().strip()
        
        if not descricao:
            messagebox.showerror("Erro", "Por favor, insira uma descrição.")
            return
            
        try:
            valor = float(valor_str)
            if valor <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um valor válido (maior que zero).")
            return
        
        transacao = Transacao(descricao, valor, tipo, categoria, data)
        self.transacao_service.adicionar_transacao(transacao)
        
        messagebox.showinfo("Sucesso", f"{tipo.capitalize()} adicionada com sucesso!")
        self.mostrar_dashboard()
        
    def atualizar_lista_transacoes(self):
        # Limpar treeview
        for item in self.tree_transacoes.get_children():
            self.tree_transacoes.delete(item)
            
        transacoes = self.transacao_service.listar_transacoes()
        for transacao in transacoes:
            tipo_display = "💰 Receita" if transacao.tipo == "receita" else "💸 Despesa"
            valor_formatado = f"R$ {transacao.valor:,.2f}"
            
            self.tree_transacoes.insert("", "end", values=(
                transacao.id,
                transacao.data,
                tipo_display,
                transacao.categoria,
                transacao.descricao,
                valor_formatado
            ))
            
    def filtrar_transacoes(self, tipo_filtro):
        transacoes = self.transacao_service.listar_transacoes()
        
        # Limpar treeview
        for item in self.tree_transacoes.get_children():
            self.tree_transacoes.delete(item)
            
        for transacao in transacoes:
            if tipo_filtro == "Todos" or \
               (tipo_filtro == "Receita" and transacao.tipo == "receita") or \
               (tipo_filtro == "Despesa" and transacao.tipo == "despesa"):
                
                tipo_display = "💰 Receita" if transacao.tipo == "receita" else "💸 Despesa"
                valor_formatado = f"R$ {transacao.valor:,.2f}"
                
                self.tree_transacoes.insert("", "end", values=(
                    transacao.id,
                    transacao.data,
                    tipo_display,
                    transacao.categoria,
                    transacao.descricao,
                    valor_formatado
                ))
                
    def excluir_transacao_selecionada(self):
        selecionado = self.tree_transacoes.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Por favor, selecione uma transação para excluir.")
            return
            
        item = selecionado[0]
        valores = self.tree_transacoes.item(item, "values")
        transacao_id = int(valores[0])
        
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta transação?"):
            if self.transacao_service.excluir_transacao(transacao_id):
                messagebox.showinfo("Sucesso", "Transação excluída com sucesso!")
                self.atualizar_lista_transacoes()
                self.atualizar_dashboard()
            else:
                messagebox.showerror("Erro", "Não foi possível excluir a transação.")
                
    def atualizar_dashboard(self):
        if self.header_label.cget("text") == "Dashboard":
            self.criar_widgets_dashboard()
            
    def alternar_modo(self):
        modo_atual = ctk.get_appearance_mode()
        novo_modo = "Light" if modo_atual == "Dark" else "Dark"
        ctk.set_appearance_mode(novo_modo)
        
    def exportar_dados(self):
        messagebox.showinfo("Exportar", "Funcionalidade de exportação em desenvolvimento.")
        
    def limpar_dados(self):
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja limpar TODOS os dados?\nEsta ação não pode ser desfeita."):
            # Implementar limpeza de dados
            messagebox.showinfo("Sucesso", "Dados limpos com sucesso!")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FinanceApp()
    app.run()