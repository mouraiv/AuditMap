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
        
        # Header
        header = tk.Frame(self, bg='#2c3e50', padx=10, pady=10)
        header.grid(row=0, column=0, sticky='ew')
        
        tk.Label(
            header, text="AuditMap - Correção de Divergências", 
            font=('Helvetica', 16, 'bold'), 
            fg='white', bg='#2c3e50'
        ).pack(side='left')
        
        # Main body
        body = tk.Frame(self, bg='#f0f0f0', padx=20, pady=20)
        body.grid(row=1, column=0, sticky='nsew')
        
        # Top panel (summary)
        top_frame = tk.Frame(body, bg='#f0f0f0')
        top_frame.pack(fill='x', pady=(0, 10))
        
        # Frame principal do topo
        top_frame.grid_rowconfigure(0, weight=1)
        top_frame.grid_columnconfigure(0, weight=1)  # Para o summary_frame
        top_frame.grid_columnconfigure(1, weight=0)  # Para o botão

        # Summary Frame
        summary_frame = tk.LabelFrame(top_frame, text="Resumo", bg='#f0f0f0',
                                    font=('Helvetica', 10, 'bold'), padx=10, pady=10)
        summary_frame.grid(row=0, column=0, columnspan=2, sticky='nsew')  # Ocupa as duas colunas

        summary_frame.grid_columnconfigure(0, weight=0)
        summary_frame.grid_columnconfigure(1, weight=1)
        summary_frame.grid_columnconfigure(2, weight=0)

        self.total_div_label = tk.Label(
            summary_frame, text="Total de divergências: 0",
            font=('Helvetica', 10, 'bold'), bg='#f0f0f0'
        )
        self.total_div_label.grid(row=0, column=0, sticky='w')

        self.total_ok_label = tk.Label(
            summary_frame, text="Endereços OK: 0",
            font=('Helvetica', 10, 'bold'), bg='#f0f0f0', fg='green'
        )
        self.total_ok_label.grid(row=0, column=1, sticky='w', padx=(20, 0))

        self.export_btn = tk.Button(
            summary_frame, text="Exportar Survey OK",
            bg='#3498db', fg='white', font=('Helvetica', 10, 'bold'),
            command=self.export_valid_surveys,
            pady=2
        )
        self.export_btn.grid(row=0, column=2, sticky='e', padx=(20, 0))

        # Divergence list
        div_list_frame = tk.LabelFrame(body, text="Tipos de Divergência", bg='#f0f0f0', font=('Helvetica', 10, 'bold'), padx=10, pady=10)
        div_list_frame.pack(fill='x')
        
        # Dynamic divergence buttons
        self.div_buttons = []
        # Dicionário de tradução/mapeamento dos tipos
        div_type_names = {
            'logradouro': 'Logradouro',
            'bairro': 'Bairro',
            'logradouro_bairro': 'Logradouro / Bairro',
            'nao_encontrado': 'Não Encontrado'
        }

        for div_type in ['logradouro', 'bairro', 'logradouro_bairro', 'nao_encontrado']:
            btn_text = f"{div_type_names[div_type]} (0)"  # Usa o nome formatado do dicionário
            btn = tk.Label(
                div_list_frame, 
                text=btn_text,
                font=('Helvetica', 10, 'bold', 'underline'), 
                fg='red', 
                bg='#f0f0f0', 
                cursor='hand2'
            )
            btn.pack(side='left', padx=5)
            btn.bind('<Button-1>', lambda e, t=div_type: self.load_divergence_type(t))
            self.div_buttons.append(btn)
        
        # Correction form
        # Frame principal preenchendo a janela
        self.form_frame = tk.LabelFrame(body, text="Corrigir Endereço", font=('Helvetica', 10, 'bold'), bg='#f0f0f0', padx=10, pady=10)
        self.form_frame.pack(fill='x', pady=(10, 0))  # <- ocupa toda a largura

        # Frame interno centralizado para o conteúdo
        self.inner_form = tk.Frame(self.form_frame, bg='#f0f0f0')
        self.inner_form.pack(anchor='w', fill='x', padx=(0,10))  # <- centralizado e preenchendo a largura

        # Configure form grid
        #for i in range(6):
        self.inner_form.grid_rowconfigure(0, weight=1)
        self.inner_form.grid_columnconfigure(2, weight=1)
        self.inner_form.grid_columnconfigure(3, weight=1)
        self.inner_form.grid_columnconfigure(4, weight=1)
        self.inner_form.grid_columnconfigure(5, weight=1)
        self.inner_form.grid_columnconfigure(6, weight=1)
        self.inner_form.grid_columnconfigure(7, weight=1)

        # Linha 1: Checkboxes + Latitude, Longitude, Localidade, CEP
        self.moradia_var = tk.IntVar()
        self.edificio_var = tk.IntVar()

        tk.Checkbutton(self.inner_form, text="Moradia", variable=self.moradia_var, bg='#f0f0f0', font=('Helvetica', 9, 'bold')).grid(row=0, column=0, columnspan=2, sticky='e', padx=0, pady=5)
        tk.Checkbutton(self.inner_form, text="Edifício", variable=self.edificio_var, bg='#f0f0f0', font=('Helvetica', 9, 'bold')).grid(row=0, column=1, sticky='w', padx=0, pady=5)

        tk.Label(self.inner_form, text="Latitude:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=0, column=2, sticky='e', padx=5, pady=5)
        self.latitude_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.latitude_entry.grid(row=0, column=3, sticky='ew', padx=0, pady=5)

        tk.Label(self.inner_form, text="Longitude:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=0, column=4, sticky='e', padx=5, pady=5)
        self.longitude_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.longitude_entry.grid(row=0, column=5, sticky='ew', padx=5, pady=5)

        tk.Label(self.inner_form, text="CEP:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=0, column=6, sticky='e', padx=5, pady=5)
        self.cep_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.cep_entry.grid(row=0, column=7, sticky='ew', padx=5, pady=5)

        # Linha 2: Logradouro e Número
        tk.Label(self.inner_form, text="Lograd.:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=1, column=0, sticky='e', padx=(0,5), pady=5)  # Alterado sticky para 'w' e padx reduzido
        self.logradouro_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.logradouro_entry.grid(row=1, column=1, columnspan=5, sticky='ew', padx=(0,5), pady=5)  # Padx ajustado

        tk.Label(self.inner_form, text="N°:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=1, column=6, sticky='e', padx=5, pady=5)
        self.numero_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.numero_entry.grid(row=1, column=7, sticky='ew', padx=5, pady=5)

        # Linha 3: Bairro, Município, LOCALIDADE, UF
        tk.Label(self.inner_form, text="Bairro:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=2, column=0, sticky='e', padx=(0,5), pady=5)  # Alterado sticky para 'w' e padx reduzido
        self.bairro_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.bairro_entry.grid(row=2, column=1, sticky='ew', padx=(0,5), pady=5)  # Padx ajustado

        tk.Label(self.inner_form, text="Município:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=2, column=2, sticky='e', padx=5, pady=5)
        self.municipio_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.municipio_entry.grid(row=2, column=3, sticky='ew', padx=5, pady=5)

        tk.Label(self.inner_form, text="Localidade:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=2, column=4, sticky='e', padx=5, pady=5)
        self.localidade_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.localidade_entry.grid(row=2, column=5, sticky='ew', padx=5, pady=5)

        tk.Label(self.inner_form, text="UF:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=2, column=6, sticky='e', padx=5, pady=5)
        self.uf_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.uf_entry.grid(row=2, column=7, sticky='ew', padx=5, pady=5)

        # Linha 4: Complementos
        tk.Label(self.inner_form, text="Compl.1:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=3, column=0, sticky='e', padx=(0,5), pady=5)  # Alterado sticky para 'w' e padx reduzido
        self.complemento1_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.complemento1_entry.grid(row=3, column=1, columnspan=3, sticky='ew', padx=(0,5), pady=5)

        tk.Label(self.inner_form, text="Compl.2:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=3, column=4, sticky='e', padx=5, pady=5)
        self.complemento2_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.complemento2_entry.grid(row=3, column=5, columnspan=3, sticky='ew', padx=5, pady=5)

        # Botões
        btn_frame = tk.Frame(self.inner_form, bg='#f0f0f0')
        btn_frame.grid(row=4, column=0, columnspan=8, pady=(10, 0))

        tk.Button(btn_frame, text="<<", command=self.previous_address, font=('Helvetica', 10, 'bold')).pack(side='left', padx=(0, 10))
        tk.Button(btn_frame, text="Corrigir", command=self.correct_and_next, bg='#2ecc71', fg='white', width=10, font=('Helvetica', 10, 'bold')).pack(side='left')
        tk.Button(btn_frame, text=">>", command=self.skip_address, font=('Helvetica', 10, 'bold')).pack(side='left', padx=(10, 0))

        # Address list for correction
        self.addresses_frame = tk.LabelFrame(body, text="Endereços para Correção", bg='#f0f0f0', font=('Helvetica', 10, 'bold'), padx=10, pady=10)
        self.addresses_frame.pack(fill='both', expand=True, pady=(10, 0))

        # Estilo da Treeview
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.configure("Treeview", font=("Helvetica", 10, "bold"))
        
        # Treeview for addresses
        self.addresses_tree = ttk.Treeview(
            self.addresses_frame, 
            columns=('id', 'logradouro', 'numero', 'bairro', 'cep', 'divergencias'), 
            show='headings'
        )

        # Adicione este binding após criar a Treeview
        self.addresses_tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # Cores alternadas e destaque para quantidade > 0
        self.addresses_tree.tag_configure('even', background='#f0f0f0')
        self.addresses_tree.tag_configure('odd', background='white')
        
        # Column configuration
        columns = {
            'id': {'text': 'ID', 'width': 30},
            'logradouro': {'text': 'Logradouro', 'width': 250},
            'numero': {'text': 'Número', 'width': 30},
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
        
        # Back button
        back_btn = tk.Button(
            body, text="Voltar para Validação", 
            command=lambda: controller.show_frame('ValidationFrame'),
            font=('Helvetica', 10, 'bold')
        )
        back_btn.pack(pady=(20, 0))

    def update_data(self):
        """Updates screen data with database information"""
        try:
            # Dicionário de mapeamento (deve ser o mesmo usado na criação dos botões)
            div_type_names = {
                'logradouro': 'Logradouro',
                'bairro': 'Bairro',
                'logradouro_bairro': 'Logradouro / Bairro',
                'nao_encontrado': 'Não Encontrado'
            }

            # Get divergence statistics
            stats = self.controller.db.get_divergence_types()
            
            # Update counters
            total_div = (stats.get('logradouro_div', 0) + 
                    stats.get('bairro_div', 0) +
                    stats.get('logradouro_bairro_div', 0) +  
                    stats.get('nao_encontrado', 0))
            
            self.total_div_label.config(text=f"Total de divergências: {total_div}")
            self.total_ok_label.config(text=f"Endereços OK: {stats.get('registros_ok', 0)}")
            
            # Update divergence type buttons with formatted names
            div_counts = {
                'logradouro': stats.get('logradouro_div', 0),
                'bairro': stats.get('bairro_div', 0),
                'logradouro_bairro': stats.get('logradouro_bairro_div', 0),
                'nao_encontrado': stats.get('nao_encontrado', 0)
            }
            
            for btn, div_type in zip(self.div_buttons, div_counts.keys()):
                formatted_name = div_type_names[div_type]
                count = div_counts[div_type]
                btn.config(text=f"{formatted_name} ({count})")
            
            # Load first available divergence
            if div_counts['logradouro'] > 0:
                self.load_divergence_type('logradouro')
            elif div_counts['bairro'] > 0:
                self.load_divergence_type('bairro')
            elif div_counts['logradouro_bairro'] > 0:
                self.load_divergence_type('logradouro_bairro')
            elif div_counts['nao_encontrado'] > 0:
                self.load_divergence_type('nao_encontrado')
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar dados: {str(e)}")

    def on_tree_select(self, event):
        """Handles treeview row selection by user"""
        selected_item = self.addresses_tree.selection()
        if selected_item:
            item_index = self.addresses_tree.index(selected_item[0])
            if item_index != self.current_address_index:
                self.current_address_index = item_index
                self.load_current_address(from_tree=True)

    def load_divergence_type(self, div_type: str):
        """Loads addresses with specific divergence type"""
        try:
            self.current_divergence_type = div_type
            self.current_address_index = 0
            
            # Get divergent addresses from database
            self.divergent_addresses = self.controller.db.get_divergent_addresses(div_type)
            
            # Update treeview
            self.update_addresses_tree()
            
            # Load first address in form
            if self.divergent_addresses:
                self.load_current_address()
            else:
                self.clear_form()
                messagebox.showinfo("Sem divergências", f"Não há divergências do tipo {div_type}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar divergências: {str(e)}")

    def update_addresses_tree(self):
        """Updates treeview with divergent addresses"""
        self.addresses_tree.delete(*self.addresses_tree.get_children())
        
        # Add new items with alternating colors
        for i, addr in enumerate(self.divergent_addresses):
            tag = 'even' if i % 2 == 0 else 'odd'
            self.addresses_tree.insert('', 'end', 
                                    values=(
                                        addr.get('id'),
                                        addr.get('logradouro', ''),
                                        addr.get('numero_fachada', ''),
                                        addr.get('bairro', ''),
                                        addr.get('cep', ''),
                                        self.get_divergence_description(addr)
                                    ),
                                    tags=(tag,))

    def get_divergence_description(self, address: Dict) -> str:
        """Returns divergence description for specific address"""
        if self.current_divergence_type == 'logradouro':
            return "Logradouro"
        elif self.current_divergence_type == 'bairro':
            return "Bairro"
        elif self.current_divergence_type == 'logradouro_bairro':
            return "Logradouro / Bairro"
        elif self.current_divergence_type == 'nao_encontrado':
            return "Endereço não encontrado"
        return "Divergência desconhecida"

    def load_current_address(self, from_tree=False):
        """Loads current address into form"""
        if not (0 <= self.current_address_index < len(self.divergent_addresses)):
            return

        addr = self.divergent_addresses[self.current_address_index]
        print(f"Carregando endereço: {addr}")

        def safe_insert(entry_widget, value, is_divergent=False, default=''):
            if entry_widget is None:
                return
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, str(value) if value is not None else default)
            # Muda a cor de fundo se for divergente
            entry_widget.config(bg='#ffcccc' if is_divergent else 'white')

        # Inserção com checagem de divergência
        safe_insert(self.logradouro_entry, addr.get('logradouro'), addr.get('lograd_div') == 2)
        safe_insert(self.numero_entry, addr.get('numero_fachada'))  # sem flag
        safe_insert(self.bairro_entry, addr.get('bairro'), addr.get('bairro_div') == 2)
        safe_insert(self.cep_entry, addr.get('cep'))  # sem flag
        safe_insert(self.localidade_entry, addr.get('localidade'))  # sem flag
        safe_insert(self.uf_entry, addr.get('uf_abrev'))  # sem flag
        safe_insert(self.municipio_entry, addr.get('municipio'))  # sem flag
        safe_insert(self.latitude_entry, addr.get('coordX'))  # sem flag
        safe_insert(self.longitude_entry, addr.get('coordY'))  # sem flag
        safe_insert(self.complemento1_entry, addr.get('complemento1'))  # sem flag
        safe_insert(self.complemento2_entry, addr.get('complemento2'))  # sem flag

        self.moradia_var.set(addr.get('moradia', 0))
        self.edificio_var.set(addr.get('edificio', 0))

        if not from_tree:
            items = self.addresses_tree.get_children()
            if items and self.current_address_index < len(items):
                self.addresses_tree.selection_set(items[self.current_address_index])
                self.addresses_tree.focus(items[self.current_address_index])

    def clear_form(self):
        """Clears the form"""
        for entry in [
            self.logradouro_entry, self.numero_entry, self.bairro_entry, 
            self.cep_entry, self.localidade_entry, self.uf_entry,
            self.municipio_entry, self.latitude_entry, self.longitude_entry,
            self.complemento1_entry, self.complemento2_entry
        ]:
            entry.delete(0, tk.END)
        
        self.moradia_var.set(0)
        self.edificio_var.set(0)

    def previous_address(self):
        """Goes back to previous address"""
        if self.current_address_index > 0:
            self.current_address_index -= 1
            self.load_current_address()

    def correct_and_next(self):
        """Corrects current address and moves to next"""
        try:
            if not self.divergent_addresses:
                return
                
            # Get form data
            updates = {
                'logradouro': self.logradouro_entry.get(),
                'numero_fachada': self.numero_entry.get(),
                'bairro': self.bairro_entry.get(),
                'cep': self.cep_entry.get(),
                'localidade': self.localidade_entry.get(),
                'uf': self.uf_entry.get(),
                'municipio': self.municipio_entry.get(),
                'latitude': self.latitude_entry.get(),
                'longitude': self.longitude_entry.get(),
                'complemento1': self.complemento1_entry.get(),
                'complemento2': self.complemento2_entry.get(),
                'moradia': self.moradia_var.get(),
                'edificio': self.edificio_var.get(),
                'status': 1  # Mark as OK
            }
            
            # Reset specific divergence flags based on current type
            if self.current_divergence_type == 'logradouro':
                updates['lograd_div'] = 1
            elif self.current_divergence_type == 'bairro':
                updates['bairro_div'] = 1
            elif self.current_divergence_type == 'logradouro_bairro':
                updates['logradouro_bairro_div'] = 1
            elif self.current_divergence_type == 'nao_encontrado':
                updates['status'] = 1  # Ensure status is set to OK
            
            # Update in database
            addr_id = self.divergent_addresses[self.current_address_index]['id']
            self.controller.db.update_address(addr_id, updates)
            
            # Remove from divergent list
            self.divergent_addresses.pop(self.current_address_index)
            self.update_addresses_tree()
            
            # Move to next or reload
            if self.current_address_index >= len(self.divergent_addresses):
                self.current_address_index = max(0, len(self.divergent_addresses) - 1)
            
            if self.divergent_addresses:
                self.load_current_address()
            else:
                self.clear_form()
                messagebox.showinfo("Concluído", "Todas as divergências deste tipo foram corrigidas!")
                self.update_data()  # Update statistics
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao corrigir endereço: {str(e)}")

    def skip_address(self):
        """Skips current address without correcting"""
        if self.divergent_addresses and self.current_address_index < len(self.divergent_addresses) - 1:
            self.current_address_index += 1
            self.load_current_address()

    def export_valid_surveys(self):
        """Exports validated surveys"""
        try:
            valid_surveys = self.controller.db.get_surveys_by_status(1)  # Status 1 = OK
            # Here you can implement export logic to CSV, Excel, etc.
            messagebox.showinfo("Exportação", f"{len(valid_surveys)} surveys válidos prontos para exportação!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao obter surveys válidos: {str(e)}")