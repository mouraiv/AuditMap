import tkinter as tk
from tkinter import ttk

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
            header, text="Resultados da Validação", 
            font=('Helvetica', 16, 'bold'), 
            fg='white', bg='#2c3e50'
        ).pack(side='left')
        
        # Corpo principal
        body = tk.Frame(self, bg='#f0f0f0', padx=20, pady=20)
        body.grid(row=1, column=0, sticky='nsew')
        
        # Resumo da validação
        summary_frame = tk.LabelFrame(body, text="Resumo", bg='#f0f0f0', padx=10, pady=10)
        summary_frame.pack(fill='x', pady=(0, 20))
        
        self.total_label = tk.Label(
            summary_frame, text="Total de endereços: 0", 
            font=('Helvetica', 10), bg='#f0f0f0'
        )
        self.total_label.pack(anchor='w')
        
        self.ok_label = tk.Label(
            summary_frame, text="Endereços OK: 0", 
            font=('Helvetica', 10), bg='#f0f0f0', fg='green'
        )
        self.ok_label.pack(anchor='w')
        
        self.div_label = tk.Label(
            summary_frame, text="Endereços com divergência: 0", 
            font=('Helvetica', 10), bg='#f0f0f0', fg='red'
        )
        self.div_label.pack(anchor='w')
        
        # Divergências detalhadas
        div_frame = tk.LabelFrame(body, text="Divergências Detalhadas", bg='#f0f0f0', padx=10, pady=10)
        div_frame.pack(fill='x')
        
        # Treeview para mostrar divergências
        self.tree = ttk.Treeview(div_frame, columns=('type', 'count'), show='headings')
        self.tree.heading('type', text='Tipo de Divergência')
        self.tree.heading('count', text='Quantidade')
        self.tree.column('type', width=200)
        self.tree.column('count', width=100)
        self.tree.pack(fill='x')
        
        # Botões de ação
        btn_frame = tk.Frame(body, bg='#f0f0f0')
        btn_frame.pack(fill='x', pady=(20, 0))
        
        self.export_btn = tk.Button(
            btn_frame, text="Exportar Endereços OK", 
            state='disabled', bg='#3498db', fg='white'
        )
        self.export_btn.pack(side='left', padx=(0, 10))
        
        self.correct_btn = tk.Button(
            btn_frame, text="Corrigir Divergências", 
            command=self.correct_divergences, bg='#e74c3c', fg='white'
        )
        self.correct_btn.pack(side='left')
        
        back_btn = tk.Button(
            btn_frame, text="Voltar", 
            command=lambda: controller.show_frame('HomeFrame')
        )
        back_btn.pack(side='right')
    
    def correct_divergences(self):
        self.controller.show_frame('CorrectionFrame')
    
    def update_data(self):
        # Atualizar com dados reais da validação
        self.total_label.config(text="Total de endereços: 150")
        self.ok_label.config(text="Endereços OK: 40")
        self.div_label.config(text="Endereços com divergência: 110")
        
        # Limpar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Adicionar dados de exemplo
        divergences = [
            ('Logradouro', 5),
            ('CEP', 2),
            ('Bairro', 21),
            ('Número', 50),
            ('Não consta na base matrix', 32)
        ]
        
        for div in divergences:
            self.tree.insert('', 'end', values=div)
        
        self.export_btn.config(state='normal')