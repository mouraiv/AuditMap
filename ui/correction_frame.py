import tkinter as tk
from tkinter import ttk

class CorrectionFrame(tk.Frame):
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
            header, text="Correção de Divergências", 
            font=('Helvetica', 16, 'bold'), 
            fg='white', bg='#2c3e50'
        ).pack(side='left')
        
        # Corpo principal
        body = tk.Frame(self, bg='#f0f0f0', padx=20, pady=20)
        body.grid(row=1, column=0, sticky='nsew')
        
        # Painel superior (resumo)
        top_frame = tk.Frame(body, bg='#f0f0f0')
        top_frame.pack(fill='x', pady=(0, 20))
        
        # Resumo
        summary_frame = tk.LabelFrame(top_frame, text="Resumo", bg='#f0f0f0', padx=10, pady=10)
        summary_frame.pack(side='left', fill='x', expand=True)
        
        self.total_div_label = tk.Label(
            summary_frame, text="Total de divergências: 110", 
            font=('Helvetica', 10), bg='#f0f0f0'
        )
        self.total_div_label.pack(anchor='w')
        
        self.total_ok_label = tk.Label(
            summary_frame, text="Endereços OK: 40", 
            font=('Helvetica', 10), bg='#f0f0f0', fg='green'
        )
        self.total_ok_label.pack(anchor='w')
        
        # Botão de exportar
        self.export_btn = tk.Button(
            top_frame, text="Exportar Survey OK", 
            bg='#3498db', fg='white'
        )
        self.export_btn.pack(side='right', padx=(10, 0))
        
        # Lista de divergências
        div_list_frame = tk.LabelFrame(body, text="Tipos de Divergência", bg='#f0f0f0', padx=10, pady=10)
        div_list_frame.pack(fill='x')
        
        # Divergências (exemplo)
        div_types = [
            ('Logradouro (5)', 5),
            ('CEP (2)', 2),
            ('Bairro (21)', 21),
            ('Número (50)', 50),
            ('Não consta na base matrix (32)', 32)
        ]
        
        for text, count in div_types:
            btn = tk.Label(
                div_list_frame, text=text, 
                font=('Helvetica', 10, 'underline'), 
                fg='red', bg='#f0f0f0', cursor='hand2'
            )
            btn.pack(anchor='w', pady=2)
            btn.bind('<Button-1>', lambda e, t=text: self.load_divergence_type(t.split(' ')[0]))
        
        # Formulário de correção
        self.form_frame = tk.LabelFrame(body, text="Corrigir Endereço", bg='#f0f0f0', padx=10, pady=10)
        self.form_frame.pack(fill='x', pady=(20, 0))
        
        # Grid para formulário
        for i in range(4):
            self.form_frame.grid_columnconfigure(i, weight=1)
        
        # Campos do formulário (exemplo)
        tk.Label(self.form_frame, text="Logradouro:", bg='#f0f0f0').grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.logradouro_entry = tk.Entry(self.form_frame)
        self.logradouro_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        tk.Label(self.form_frame, text="Número:", bg='#f0f0f0').grid(row=0, column=2, sticky='e', padx=5, pady=5)
        self.numero_entry = tk.Entry(self.form_frame)
        self.numero_entry.grid(row=0, column=3, sticky='ew', padx=5, pady=5)
        
        tk.Label(self.form_frame, text="Bairro:", bg='#f0f0f0').grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.bairro_entry = tk.Entry(self.form_frame)
        self.bairro_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        tk.Label(self.form_frame, text="CEP:", bg='#f0f0f0').grid(row=1, column=2, sticky='e', padx=5, pady=5)
        cep_frame = tk.Frame(self.form_frame, bg='#f0f0f0')
        cep_frame.grid(row=1, column=3, sticky='ew', padx=5, pady=5)
        
        self.cep_entry = tk.Entry(cep_frame)
        self.cep_entry.pack(side='left', fill='x', expand=True)
        
        self.cep_source = ttk.Combobox(cep_frame, values=['Manual', 'Correios', 'Geocorp'], state='readonly')
        self.cep_source.set('Manual')
        self.cep_source.pack(side='left', padx=(5, 0))
        
        # Botões do formulário
        btn_frame = tk.Frame(self.form_frame, bg='#f0f0f0')
        btn_frame.grid(row=2, column=0, columnspan=4, pady=(10, 0))
        
        tk.Button(
            btn_frame, text="Retroceder", 
            command=self.previous_address
        ).pack(side='left', padx=(0, 10))
        
        tk.Button(
            btn_frame, text="Corrigir e Avançar", 
            command=self.correct_and_next, bg='#2ecc71', fg='white'
        ).pack(side='left')
        
        # Lista de endereços para correção
        self.addresses_frame = tk.LabelFrame(body, text="Endereços para Correção", bg='#f0f0f0', padx=10, pady=10)
        self.addresses_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # Treeview para endereços
        self.addresses_tree = ttk.Treeview(
            self.addresses_frame, 
            columns=('id', 'logradouro', 'numero', 'bairro', 'cep', 'divergencias'), 
            show='headings'
        )
        
        self.addresses_tree.heading('id', text='ID')
        self.addresses_tree.heading('logradouro', text='Logradouro')
        self.addresses_tree.heading('numero', text='Número')
        self.addresses_tree.heading('bairro', text='Bairro')
        self.addresses_tree.heading('cep', text='CEP')
        self.addresses_tree.heading('divergencias', text='Divergências')
        
        self.addresses_tree.column('id', width=50)
        self.addresses_tree.column('logradouro', width=200)
        self.addresses_tree.column('numero', width=80)
        self.addresses_tree.column('bairro', width=150)
        self.addresses_tree.column('cep', width=100)
        self.addresses_tree.column('divergencias', width=200)
        
        self.addresses_tree.pack(fill='both', expand=True)
        
        # Adicionar dados de exemplo
        for i in range(1, 6):
            self.addresses_tree.insert('', 'end', values=(
                i, 
                f"Rua Exemplo {i}", 
                f"10{i}", 
                f"Bairro {i}", 
                f"00000-00{i}", 
                "Logradouro, Número"
            ))
        
        # Botão de voltar
        back_btn = tk.Button(
            body, text="Voltar para Validação", 
            command=lambda: controller.show_frame('ValidationFrame')
        )
        back_btn.pack(pady=(20, 0))
    
    def load_divergence_type(self, div_type):
        # Carregar endereços com o tipo específico de divergência
        print(f"Carregando divergências do tipo: {div_type}")
    
    def previous_address(self):
        # Voltar para o endereço anterior
        print("Retrocedendo para endereço anterior")
    
    def correct_and_next(self):
        # Corrigir e avançar para o próximo endereço
        print("Corrigindo e avançando para próximo endereço")
    
    def update_data(self):
        # Atualizar dados quando a tela é mostrada
        pass