import tkinter as tk
from tkinter import ttk, messagebox
from validator import AddressValidator

class ValidationFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.configure(bg='#f0f0f0')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Cabeçalho
        header = tk.Frame(self, bg='#2c3e50', padx=10, pady=10)
        header.grid(row=0, column=0, sticky='ew')
        
        tk.Label(
            header, text="AuditMap - Resultados da Validação", 
            font=('Helvetica', 16, 'bold'), 
            fg='white', bg='#2c3e50'
        ).pack(side='left')
        
        # Corpo principal
        body = tk.Frame(self, bg='#f0f0f0', padx=20, pady=5)
        body.grid(row=1, column=0, sticky='nsew')

        # header info (tecnico)
        header_info_frame = tk.Frame(body, bg='#f0f0f0')
        header_info_frame.pack(fill='x', pady=(0, 5))

        header_info_frame.grid_columnconfigure(0, weight=1)
        header_info_frame.grid_columnconfigure(1, weight=1)
        header_info_frame.grid_columnconfigure(2, weight=0)

        self.voltar = tk.Label(
            header_info_frame, text="<< Voltar", 
            font=('Helvetica', 10, 'bold'), bg='#f0f0f0', fg='blue'
        )
        self.voltar.grid(row=0, column=0, sticky='w', padx=(0, 20))

        # Evento de clique
        self.voltar.bind("<Button-1>", lambda e: self.controller.show_frame('HomeFrame'))

        # Efeitos visuais opcionais
        self.voltar.bind("<Enter>", lambda e: self.voltar.config(font=('Helvetica', 10, 'bold', 'underline')))
        self.voltar.bind("<Leave>", lambda e: self.voltar.config(font=('Helvetica', 10, 'bold')))

        self.tecnico = tk.Label(
            header_info_frame, text="[ Técnico: -- ]", 
            font=('Helvetica', 9, 'bold'), bg='#f0f0f0'
        )
        self.tecnico.grid(row=0, column=1, sticky='e', padx=(0, 20))

        self.empresa = tk.Label(
            header_info_frame, text="[ Empresa: -- ]", 
            font=('Helvetica', 9, 'bold'), bg='#f0f0f0'
        )
        self.empresa.grid(row=0, column=2, sticky='w', padx=(0, 20))

        # Top panel (summary)
        top_frame = tk.Frame(body, bg='#f0f0f0')
        top_frame.pack(fill='x', pady=(0, 10))
        
        # Resumo da validação
        summary_frame = tk.LabelFrame(top_frame, text="Resumo", font=('Helvetica', 10, 'bold'), bg='#f0f0f0', padx=10, pady=10)
        summary_frame.pack(fill='x', pady=(0, 10))
        
        self.total_label = tk.Label(
            summary_frame, text="Total de surveys: 0", 
            font=('Helvetica', 10, 'bold'), bg='#f0f0f0'
        )
        self.total_label.grid(row=0, column=0, sticky='w', padx=(0, 20))
        
        self.ok_label = tk.Label(
            summary_frame, text="Surveys OK: 0", 
            font=('Helvetica', 10, 'bold'), bg='#f0f0f0', fg='green'
        )
        self.ok_label.grid(row=0, column=1, sticky='w', padx=(0, 20))
        
        self.div_label = tk.Label(
            summary_frame, text="Surveys com divergência: 0", 
            font=('Helvetica', 10, 'bold'), bg='#f0f0f0', fg='red'
        )
        self.div_label.grid(row=0, column=2, sticky='w')
        
        # Divergências detalhadas
        div_frame = tk.LabelFrame(body, text="Divergências Detalhadas", font=('Helvetica', 10, 'bold'), bg='#f0f0f0', padx=10, pady=10)
        div_frame.pack(fill='x')

        # Estilo da Treeview
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.configure("Treeview", font=("Helvetica", 10, "bold"))

        # Treeview
        self.tree = ttk.Treeview(div_frame, columns=('type', 'count'), show='headings', height=10)
        self.tree.heading('type', text='Tipo de Divergência')
        self.tree.heading('count', text='Quantidade')
        self.tree.column('type', width=200)
        self.tree.column('count', width=100)
        self.tree.pack(fill='x')

        # Cores alternadas e destaque para quantidade > 0
        self.tree.tag_configure('even', background='#f0f0f0')
        self.tree.tag_configure('odd', background='white')
        
        # Botões de ação
        btn_frame = tk.Frame(body, bg='#f0f0f0')
        btn_frame.pack(fill='x', pady=(20, 0))
        
        self.export_btn = tk.Button(
            btn_frame, text="Exportar Endereços OK", 
            state='disabled', bg='#3498db', fg='white', font=('Helvetica', 10, 'bold')
        )
        self.export_btn.pack(side='left', padx=(0, 10))
        
        self.correct_btn = tk.Button(
            btn_frame, text="Corrigir Divergências", 
            command=self.correct_divergences, bg='#e74c3c', fg='white', font=('Helvetica', 10, 'bold')
        )
        self.correct_btn.pack(side='left')
        
    def get_tecnico_atual(self):
        info_tecnico = self.controller.db.get_tecnico_empresa_surveys()

        if not info_tecnico or len(info_tecnico) < 2:
            return None, None
        
        tecnico_nome = info_tecnico.get('tecnico_nome', '--')
        empresa_nome = info_tecnico.get('empresa_nome', '--')

        self.tecnico.config(text=f"[ Técnico: {tecnico_nome} ]")
        self.empresa.config(text=f"[ Empresa: {empresa_nome} ]")
    
    def correct_divergences(self):
        self.controller.show_frame('CorrectionFrame')
    
    def update_data(self):
        """Busca dados reais do banco e atualiza a interface"""
        try:
            self.get_tecnico_atual()

            validator = AddressValidator(self.controller.db)
            stats = validator.validate_all_surveys()
            
            # Atualiza os labels
            self.total_label.config(text=f"Total de surveys: {stats['total']}")
            self.ok_label.config(text=f"Surveys OK: {stats['ok']}")
            self.div_label.config(text=f"Surveys com divergência: {stats['total'] - stats['ok']}")

            divergente = {k: v for k, v in stats['divergencias'].items() if k != 'cep'}

            # Dicionário de tradução/mapeamento dos tipos
            div_type_names = {
                'logradouro': 'Logradouro',
                'bairro': 'Bairro',
                'logradouro_bairro': 'Logradouro / Bairro',
                'nao_encontrado': 'Não Encontrado'
            }

            # Atualiza a treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            for i, (div_type, count) in enumerate(divergente.items()):
                tag = 'even' if i % 2 == 0 else 'odd'
                self.tree.insert('', 'end', values=(div_type_names[div_type], count), tags=(tag,))

            # Habilita botões conforme necessário
            self.export_btn.config(state='normal' if stats['total'] > 0 else 'disabled')
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar dados: {str(e)}")

