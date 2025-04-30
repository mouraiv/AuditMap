import tkinter as tk
from tkinter import ttk, messagebox

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
    
    # Em ValidationFrame
    def update_data(self):
        """Busca dados reais do banco e atualiza a interface"""
        try:
            db = self.controller.db
            
            # Busca estatísticas
            total = db.get_total_addresses()
            valid = db.get_valid_addresses()
            divergent = db.get_divergent_addresses()
            divergence_types = db.get_divergence_types()
            
            # Atualiza os labels
            self.total_label.config(text=f"Total de endereços: {total}")
            self.ok_label.config(text=f"Endereços OK: {valid}")
            self.div_label.config(text=f"Endereços com divergência: {divergent}")
            
            # Atualiza a treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            for div_type, count in divergence_types:
                self.tree.insert('', 'end', values=(div_type, count))
                
            # Habilita botões conforme necessário
            self.export_btn.config(state='normal' if total > 0 else 'disabled')
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar dados: {str(e)}")