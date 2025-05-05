import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict

class CorrectionFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.current_address_index = 0
        self.divergent_addresses = []
        self.current_divergence_type = None
        
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
            summary_frame, text="Total de divergências: 0", 
            font=('Helvetica', 10), bg='#f0f0f0'
        )
        self.total_div_label.pack(side='left')
        
        self.total_ok_label = tk.Label(
            summary_frame, text="Endereços OK: 0", 
            font=('Helvetica', 10), bg='#f0f0f0', fg='green'
        )
        self.total_ok_label.pack(side='left', padx=(20, 0))
        
        # Botão de exportar
        self.export_btn = tk.Button(
            top_frame, text="Exportar Survey OK", 
            bg='#3498db', fg='white',
            command=self.export_valid_surveys
        )
        self.export_btn.pack(side='right', padx=(10, 0))
        
        # Lista de divergências
        div_list_frame = tk.LabelFrame(body, text="Tipos de Divergência", bg='#f0f0f0', padx=10, pady=10)
        div_list_frame.pack(fill='x')
        
        # Divergências dinâmicas
        self.div_buttons = []
        for div_type in ['logradouro', 'bairro', 'cep', 'numero', 'nao_encontrado']:
            btn = tk.Label(
                div_list_frame, text=f"{div_type.capitalize()} (0)", 
                font=('Helvetica', 10, 'underline'), 
                fg='red', bg='#f0f0f0', cursor='hand2'
            )
            btn.pack(side='left', padx=5)
            btn.bind('<Button-1>', lambda e, t=div_type: self.load_divergence_type(t))
            self.div_buttons.append(btn)
        
        # Formulário de correção
        self.form_frame = tk.LabelFrame(body, text="Corrigir Endereço", bg='#f0f0f0', padx=10, pady=10)
        self.form_frame.pack(fill='x', pady=(20, 0))
        
        # Grid para formulário
        for i in range(4):
            self.form_frame.grid_columnconfigure(i, weight=1)
        
        # Campos do formulário
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
        
        tk.Button(
            btn_frame, text="Ignorar", 
            command=self.skip_address, bg='#e74c3c', fg='white'
        ).pack(side='left', padx=(10, 0))
        
        # Lista de endereços para correção
        self.addresses_frame = tk.LabelFrame(body, text="Endereços para Correção", bg='#f0f0f0', padx=10, pady=10)
        self.addresses_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # Treeview para endereços
        self.addresses_tree = ttk.Treeview(
            self.addresses_frame, 
            columns=('id', 'logradouro', 'numero', 'bairro', 'cep', 'divergencias'), 
            show='headings'
        )
        
        # Configuração das colunas
        columns = {
            'id': {'text': 'ID', 'width': 50},
            'logradouro': {'text': 'Logradouro', 'width': 200},
            'numero': {'text': 'Número', 'width': 80},
            'bairro': {'text': 'Bairro', 'width': 150},
            'cep': {'text': 'CEP', 'width': 100},
            'divergencias': {'text': 'Divergências', 'width': 200}
        }
        
        for col, config in columns.items():
            self.addresses_tree.heading(col, text=config['text'])
            self.addresses_tree.column(col, width=config['width'])
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.addresses_frame, orient="vertical", command=self.addresses_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.addresses_tree.configure(yscrollcommand=scrollbar.set)
        self.addresses_tree.pack(fill='both', expand=True)
        
        # Botão de voltar
        back_btn = tk.Button(
            body, text="Voltar para Validação", 
            command=lambda: controller.show_frame('ValidationFrame')
        )
        back_btn.pack(pady=(20, 0))

    def update_data(self):
        """Atualiza os dados da tela com informações do banco"""
        try:
            # Obter estatísticas de divergências
            stats = self.controller.db.get_divergence_types()
            
            # Atualizar contadores
            self.total_div_label.config(text=f"Total de divergências: {stats['total_registros'] - stats['registros_ok']}")
            self.total_ok_label.config(text=f"Endereços OK: {stats['registros_ok']}")
            
            # Atualizar botões de tipos de divergência
            div_counts = {
                'logradouro': stats['logradouro_div'],
                'bairro': stats['bairro_div'],
                'cep': stats['cep_div'],
                'numero': 0,  # Será calculado
                'nao_encontrado': stats['nao_encontrado']
            }
            
            for btn, (div_type, count) in zip(self.div_buttons, div_counts.items()):
                btn.config(text=f"{div_type.capitalize()} ({count})")
            
            # Carregar primeira divergência
            if div_counts['logradouro'] > 0:
                self.load_divergence_type('logradouro')
            elif div_counts['bairro'] > 0:
                self.load_divergence_type('bairro')
            elif div_counts['cep'] > 0:
                self.load_divergence_type('cep')
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar dados: {str(e)}")

    def load_divergence_type(self, div_type: str):
        """Carrega endereços com o tipo específico de divergência"""
        try:
            self.current_divergence_type = div_type
            self.current_address_index = 0
            
            # Obter endereços divergentes do banco
            if div_type == 'nao_encontrado':
                self.divergent_addresses = self.controller.db.get_surveys_by_status(3)  # Não encontrado
            else:
                # Para outros tipos, precisamos de uma consulta mais específica
                self.divergent_addresses = self.controller.db.get_divergent_addresses(div_type)
            
            # Atualizar treeview
            self.update_addresses_tree()
            
            # Carregar primeiro endereço no formulário
            if self.divergent_addresses:
                self.load_current_address()
            else:
                self.clear_form()
                messagebox.showinfo("Sem divergências", f"Não há divergências do tipo {div_type}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar divergências: {str(e)}")

    def update_addresses_tree(self):
        """Atualiza a treeview com os endereços divergentes"""
        self.addresses_tree.delete(*self.addresses_tree.get_children())
        
        for addr in self.divergent_addresses:
            self.addresses_tree.insert('', 'end', values=(
                addr.get('id'),
                addr.get('logradouro', ''),
                addr.get('numero_fachada', ''),
                addr.get('bairro', ''),
                addr.get('cep', ''),
                ', '.join(self.get_divergences_for_address(addr))
            ))

    def get_divergences_for_address(self, address: Dict) -> List[str]:
        """Retorna a lista de divergências para um endereço específico"""
        divergences = []
        if not address.get('logradouro'):
            divergences.append('logradouro')
        if not address.get('bairro'):
            divergences.append('bairro')
        if not address.get('cep'):
            divergences.append('cep')
        if not address.get('numero_fachada'):
            divergences.append('numero')
        return divergences

    def load_current_address(self):
        """Carrega o endereço atual no formulário"""
        if 0 <= self.current_address_index < len(self.divergent_addresses):
            addr = self.divergent_addresses[self.current_address_index]
            
            self.logradouro_entry.delete(0, tk.END)
            self.logradouro_entry.insert(0, addr.get('logradouro', ''))
            
            self.numero_entry.delete(0, tk.END)
            self.numero_entry.insert(0, addr.get('numero_fachada', ''))
            
            self.bairro_entry.delete(0, tk.END)
            self.bairro_entry.insert(0, addr.get('bairro', ''))
            
            self.cep_entry.delete(0, tk.END)
            self.cep_entry.insert(0, addr.get('cep', ''))
            
            # Selecionar na treeview
            items = self.addresses_tree.get_children()
            if items and self.current_address_index < len(items):
                self.addresses_tree.selection_set(items[self.current_address_index])
                self.addresses_tree.focus(items[self.current_address_index])

    def clear_form(self):
        """Limpa o formulário"""
        for entry in [self.logradouro_entry, self.numero_entry, self.bairro_entry, self.cep_entry]:
            entry.delete(0, tk.END)

    def previous_address(self):
        """Volta para o endereço anterior"""
        if self.current_address_index > 0:
            self.current_address_index -= 1
            self.load_current_address()

    def correct_and_next(self):
        """Corrige o endereço atual e avança para o próximo"""
        try:
            if not self.divergent_addresses:
                return
                
            # Obter dados do formulário
            updates = {
                'logradouro': self.logradouro_entry.get(),
                'numero_fachada': self.numero_entry.get(),
                'bairro': self.bairro_entry.get(),
                'cep': self.cep_entry.get(),
                'status': 1  # Marcar como OK
            }
            
            # Atualizar no banco de dados
            addr_id = self.divergent_addresses[self.current_address_index]['id']
            self.controller.db.update_address(addr_id, updates)
            
            # Remover da lista de divergentes
            self.divergent_addresses.pop(self.current_address_index)
            self.update_addresses_tree()
            
            # Avançar para próximo ou recarregar
            if self.current_address_index >= len(self.divergent_addresses):
                self.current_address_index = max(0, len(self.divergent_addresses) - 1)
            
            if self.divergent_addresses:
                self.load_current_address()
            else:
                self.clear_form()
                messagebox.showinfo("Concluído", "Todas as divergências deste tipo foram corrigidas!")
                self.update_data()  # Atualizar estatísticas
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao corrigir endereço: {str(e)}")

    def skip_address(self):
        """Pula o endereço atual sem corrigir"""
        if self.divergent_addresses and self.current_address_index < len(self.divergent_addresses) - 1:
            self.current_address_index += 1
            self.load_current_address()

    def export_valid_surveys(self):
        """Exporta os surveys validados"""
        try:
            valid_surveys = self.controller.db.get_surveys_by_status(1)  # Status 1 = OK
            # Aqui você pode implementar a lógica de exportação para CSV, Excel, etc.
            messagebox.showinfo("Exportação", f"{len(valid_surveys)} surveys válidos prontos para exportação!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao obter surveys válidos: {str(e)}")