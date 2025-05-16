import tkinter as tk
from tkinter import ttk, messagebox
from ui.loading_spinner import LoadingSpinner
from api_opemstreet import buscar_endereco_por_coordenadas
from typing import Dict

class CorrectionFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.current_address_index = 0
        self.divergent_addresses = []
        self.current_divergence_type = None

        # Adicione esta linha para criar o spinner
        self.loading_spinner = LoadingSpinner(self)
        
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
        self.voltar.bind("<Button-1>", lambda e: self.controller.show_frame('ValidationFrame'))

        # Efeitos visuais opcionais
        self.voltar.bind("<Enter>", lambda e: self.voltar.config(font=('Helvetica', 10, 'bold', 'underline')))
        self.voltar.bind("<Leave>", lambda e: self.voltar.config(font=('Helvetica', 10, 'bold')))

        self.tecnico = tk.Label(
            header_info_frame, text="[ -- ]", 
            font=('Helvetica', 9, 'bold'), bg='#f0f0f0'
        )
        self.tecnico.grid(row=0, column=1, sticky='e', padx=(0, 20))

        self.empresa = tk.Label(
            header_info_frame, text="[ -- ]", 
            font=('Helvetica', 9, 'bold'), bg='#f0f0f0'
        )
        self.empresa.grid(row=0, column=2, sticky='w', padx=(0, 20))
        
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
        summary_frame.grid_columnconfigure(1, weight=0)
        summary_frame.grid_columnconfigure(2, weight=1)

        self.total_div_label = tk.Label(
            summary_frame, text="Total de surveys: 0",
            font=('Helvetica', 10, 'bold'), bg='#f0f0f0'
        )
        self.total_div_label.grid(row=0, column=0, sticky='w')

        self.total_ok_label = tk.Label(
            summary_frame, text="Surveys OK: 0",
            font=('Helvetica', 10, 'bold'), bg='#f0f0f0', fg='green'
        )
        self.total_ok_label.grid(row=0, column=1, sticky='w', padx=(20, 0))

        self.div_label = tk.Label(
            summary_frame, text="Surveys com divergência: 0", 
            font=('Helvetica', 10, 'bold'), bg='#f0f0f0', fg='red'
        )
        self.div_label.grid(row=0, column=2, sticky='w', padx=(20, 0))

        self.export_btn = tk.Button(
            summary_frame, text="Exportar Survey OK",
            bg='#3498db', fg='white', font=('Helvetica', 10, 'bold'),
            command=self.export_valid_surveys,
            pady=2
        )
        self.export_btn.grid(row=0, column=3, sticky='e', padx=(20, 0))

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
            'cep_dup': 'Logradouro com múltiplos CEPs',
            'nao_encontrado': 'Não Encontrado',
            'nao_encontrado_cep_dup': 'Não Encontrado / Logradouro com múltiplos CEPs'
        }

        for div_type in ['logradouro', 'bairro', 'logradouro_bairro', 'cep_dup', 'nao_encontrado', 'nao_encontrado_cep_dup']:
            btn_text = f"{div_type_names[div_type]} (0)"  # Usa o nome formatado do dicionário
            btn = tk.Label(
                div_list_frame, 
                text=btn_text,
                font=('Helvetica', 8, 'bold', 'underline'), 
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

        # Linha 0: Checkboxes + Latitude, Longitude, Localidade, CEP
        self.moradia_var = tk.IntVar()
        self.edificio_var = tk.IntVar()

        tk.Checkbutton(self.inner_form, text="Moradia", variable=self.moradia_var, bg='#f0f0f0', font=('Helvetica', 9, 'bold')).grid(row=0, column=0, columnspan=2, sticky='e', padx=0, pady=0)
        tk.Checkbutton(self.inner_form, text="Edifício", variable=self.edificio_var, bg='#f0f0f0', font=('Helvetica', 9, 'bold')).grid(row=0, column=1, sticky='w', padx=0, pady=0)

        tk.Label(self.inner_form, text="Latitude:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=0, column=2, sticky='e', padx=5, pady=0)
        self.latitude_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.latitude_entry.grid(row=0, column=3, sticky='ew', padx=0, pady=0)

        tk.Label(self.inner_form, text="Longitude:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=0, column=4, sticky='e', padx=5, pady=0)
        self.longitude_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.longitude_entry.grid(row=0, column=5, sticky='ew', padx=5, pady=0)

        tk.Label(self.inner_form, text="CEP:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=0, column=6, sticky='e', padx=5, pady=0)
        self.cep_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.cep_entry.grid(row=0, column=7, sticky='ew', padx=5, pady=0)

        # Linha 1: Grig label sugestão bairro, municipio, localidade, uf
        self.cep_entry_sg = tk.Label(self.inner_form)
        self.cep_entry_sg.grid(row=1, column=7, sticky='ew', padx=0, pady=(0,5))

        # Linha 2: Logradouro e Número
        tk.Label(self.inner_form, text="Lograd.:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=2, column=0, sticky='e', padx=5, pady=0)  # Alterado sticky para 'w' e padx reduzido
        self.logradouro_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.logradouro_entry.grid(row=2, column=1, columnspan=5, sticky='ew', padx=0, pady=(0, 0))
        
        tk.Label(self.inner_form, text="N°:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=2, column=6, sticky='e', padx=5, pady=0)
        self.numero_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.numero_entry.grid(row=2, column=7, sticky='ew', padx=0, pady=0)

        # Linha 3: Grig label sugestão logradouro
        self.logradouro_entry_sg = tk.Label(self.inner_form, height=1, highlightthickness=0, borderwidth=0, relief='flat')
        self.logradouro_entry_sg.grid(row=3, column=1, columnspan=5, sticky='ew', padx=0,  pady=(0,5))
       
        # Linha 4: Bairro, Município, LOCALIDADE, UF
        tk.Label(self.inner_form, text="Bairro:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=4, column=0, sticky='e', padx=5, pady=0)  # Alterado sticky para 'w' e padx reduzido
        self.bairro_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.bairro_entry.grid(row=4, column=1, sticky='ew', padx=(0,5), pady=0)  # Padx ajustado

        tk.Label(self.inner_form, text="Município:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=4, column=2, sticky='e', padx=5, pady=0)
        self.municipio_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.municipio_entry.grid(row=4, column=3, sticky='ew', padx=5, pady=0)

        tk.Label(self.inner_form, text="Localidade:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=4, column=4, sticky='e', padx=5, pady=0)
        self.localidade_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.localidade_entry.grid(row=4, column=5, sticky='ew', padx=5, pady=0)

        tk.Label(self.inner_form, text="UF:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=4, column=6, sticky='e', padx=5, pady=0)
        self.uf_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.uf_entry.grid(row=4, column=7, sticky='ew', padx=5, pady=0)

        # Linha 5: Grig label sugestão bairro, municipio, localidade, uf
        self.bairro_entry_sg = tk.Label(self.inner_form)
        self.bairro_entry_sg.grid(row=5, column=1, sticky='ew', padx=0,  pady=(0,5))

        self.municipio_entry_sg = tk.Label(self.inner_form)
        self.municipio_entry_sg.grid(row=5, column=3, sticky='ew', padx=0,  pady=(0,5))

        self.localidade_entry_sg = tk.Label(self.inner_form)
        self.localidade_entry_sg.grid(row=5, column=5, sticky='ew', padx=0,  pady=(0,5))

        self.uf_entry_sg = tk.Label(self.inner_form)
        self.uf_entry_sg.grid(row=5, column=7, sticky='ew', padx=0,  pady=(0,5))
    
        # Linha 6: Complementos
        tk.Label(self.inner_form, text="Compl.1:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=6, column=0, sticky='e', padx=0, pady=0)  # Alterado sticky para 'w' e padx reduzido
        self.complemento1_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.complemento1_entry.grid(row=6, column=1, columnspan=3, sticky='ew', padx=0, pady=0)

        tk.Label(self.inner_form, text="Compl.2:", bg='#f0f0f0', font=('Helvetica', 10, 'bold')).grid(row=6, column=4, sticky='e', padx=0, pady=0)
        self.complemento2_entry = tk.Entry(self.inner_form, font=('Helvetica', 10))
        self.complemento2_entry.grid(row=6, column=5, columnspan=3, sticky='ew', padx=0, pady=0)

        # Linha 7: Botões
        btn_frame = tk.Frame(self.inner_form, bg='#f0f0f0')
        btn_frame.grid(row=7, column=0, columnspan=8, pady=(10, 0))

        tk.Button(btn_frame, text="<<", command=self.previous_address, font=('Helvetica', 10, 'bold')).pack(side='left', padx=(0, 10))
        tk.Button(btn_frame, text="Corrigir", command=self.correct_and_next, bg='#2ecc71', fg='white', width=10, font=('Helvetica', 10, 'bold')).pack(side='left')
        tk.Button(btn_frame, text=">>", command=self.skip_address, font=('Helvetica', 10, 'bold')).pack(side='left', padx=(10, 0))

        # Address list for correction
        self.addresses_frame = tk.LabelFrame(body, text="Endereços para Correção", bg='#f0f0f0', font=('Helvetica', 10, 'bold'), padx=10, pady=10)
        self.addresses_frame.pack(fill='both', expand=True, pady=(10, 0))

        # Estilo da Treeview
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 8, "bold"))
        style.configure("Treeview", font=("Helvetica", 8, "bold"))
        
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

    def get_tecnico_atual(self):
        info_tecnico = self.controller.db.get_tecnico_empresa_surveys()

        if not info_tecnico or len(info_tecnico) < 2:
            return None, None
        
        tecnico_nome = info_tecnico.get('tecnico_nome', '[ -- ]')
        empresa_nome = info_tecnico.get('empresa_nome', '[ -- ]')

        self.tecnico.config(text=f"[ {tecnico_nome} ]")
        self.empresa.config(text=f"[ {empresa_nome} ]")

    def update_data(self):
        """Updates screen data with database information"""
        try:
            self.get_tecnico_atual()
            # Dicionário de mapeamento (deve ser o mesmo usado na criação dos botões)
            div_type_names = {
                'logradouro': 'Logradouro',
                'bairro': 'Bairro',
                'logradouro_bairro': 'Logradouro / Bairro',
                'cep_dup': 'Logradouro com múltiplos CEPs',
                'nao_encontrado': 'Não Encontrado',
                'nao_encontrado_cep_dup': 'Não Encontrado / Logradouro com múltiplos CEPs'
            }

            # Get divergence statistics
            stats = self.controller.db.get_divergence_types()
            
            # Update counters            
            self.total_div_label.config(text=f"Total de surveys: {stats.get('total_registros', 0)}")
            self.total_ok_label.config(text=f"Surveys OK: {stats.get('registros_ok', 0)}")
            self.div_label.config(text=f"Surveys com divergência: {stats.get('registros_divergentes', 0)}")
            
            # Update divergence type buttons with formatted names
            div_counts = {
                'logradouro': stats.get('logradouro_div', 0),
                'bairro': stats.get('bairro_div', 0),
                'logradouro_bairro': stats.get('logradouro_bairro_div', 0),
                'cep_dup': stats.get('cep_dup', 0),
                'nao_encontrado': stats.get('nao_encontrado', 0),
                'nao_encontrado_cep_dup': stats.get('nao_encontrado_cep_dup', 0)
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
            elif div_counts['cep_dup'] > 0:
                self.load_divergence_type('cep_dup')
            elif div_counts['nao_encontrado'] > 0:
                self.load_divergence_type('nao_encontrado')
            elif div_counts['nao_encontrado_cep_dup'] > 0:
                self.load_divergence_type('nao_encontrado_cep_dup')

            # Verifica o CEP do primeiro endereço carregado
            if hasattr(self, 'divergent_addresses') and self.divergent_addresses:
                #carregar sugestões
                self.carregar_sugestao()
            
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

    def limpar_destaque_correcao(self, entry_widget, campo, event=None):
        cep = self.cep_entry.get().strip()
        dados_banco = self.controller.db.obter_dados_por_cep(cep)

        if not dados_banco or campo not in dados_banco:
            return

        valor_digitado = entry_widget.get().strip().lower()
        valor_correto = str(dados_banco[campo]).strip().lower()

        if valor_digitado == valor_correto and valor_digitado != "":
            entry_widget.config(bg='white')
        else:
            entry_widget.config(bg='#ffcccc')

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
        elif self.current_divergence_type == 'cep_dup':
            return "Logradouro com múltiplos CEPs"
        elif self.current_divergence_type == 'nao_encontrado':
            return "Endereço não encontrado"
        elif self.current_divergence_type == 'nao_encontrado_cep_dup':
            return "Não Encontrado / Logradouro com múltiplos CEPs"
        return "Divergência desconhecida"

    def load_current_address(self, from_tree=False):
        """Loads current address into form"""
        if not (0 <= self.current_address_index < len(self.divergent_addresses)):
            return

        addr = self.divergent_addresses[self.current_address_index]

        def safe_insert(entry_widget, value, is_divergent=False, default=''):
            if entry_widget is None:
                return
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, str(value) if value is not None else default)
            
            # Define a cor de fundo baseada no tipo de divergência
            if self.current_divergence_type in ['cep_dup', 'nao_encontrado', 'nao_encontrado_cep_dup']:
                # Se for um dos tipos especiais, usa azul claro para todos os campos (exceto os excluídos)
                excluded_widgets = [self.latitude_entry, self.longitude_entry, 
                                self.complemento1_entry, self.complemento2_entry]
                if entry_widget not in excluded_widgets:
                    entry_widget.config(bg='#e6f3ff')  # Azul bem clarinho
            else:
                # Para outros tipos, usa o padrão (vermelho para divergentes)
                entry_widget.config(bg='#ffcccc' if is_divergent else 'white')

        # Inserção com checagem de divergência
        safe_insert(self.logradouro_entry, addr.get('logradouro'), addr.get('lograd_div') == 2)
        safe_insert(self.numero_entry, addr.get('numero_fachada'))  # sem flag
        safe_insert(self.bairro_entry, addr.get('bairro'), addr.get('bairro_div') == 2)
        safe_insert(self.cep_entry, addr.get('cep'))  # sem flag
        safe_insert(self.localidade_entry, addr.get('localidade'))  # sem flag
        safe_insert(self.uf_entry, addr.get('uf_abrev'))  # sem flag
        safe_insert(self.municipio_entry, addr.get('municipio'))  # sem flag
        safe_insert(self.latitude_entry, addr.get('coordX'))  # sem flag (não muda cor)
        safe_insert(self.longitude_entry, addr.get('coordY'))  # sem flag (não muda cor)
        safe_insert(self.complemento1_entry, addr.get('complemento1'))  # sem flag (não muda cor)
        safe_insert(self.complemento2_entry, addr.get('complemento2'))  # sem flag (não muda cor)

        self.moradia_var.set(addr.get('moradia', 0))
        self.edificio_var.set(addr.get('edificio', 0))

        #carregar sugestões
        self.carregar_sugestao()

        if not from_tree:
            items = self.addresses_tree.get_children()
            if items and self.current_address_index < len(items):
                self.addresses_tree.selection_set(items[self.current_address_index])
                self.addresses_tree.focus(items[self.current_address_index])

    def carregar_sugestao(self):
        """Carrega sugestões baseadas no tipo de divergência"""
         # Limpa todas as sugestões anteriores (apenas o texto)
        self.limpar_sugestoes_anteriores()
        # Se for um dos tipos especiais, busca sugestões da API
        if self.current_divergence_type in ['cep_dup', 'nao_encontrado', 'nao_encontrado_cep_dup']:
            lat = self.latitude_entry.get().strip()
            lon = self.longitude_entry.get().strip()
            self.buscar_sugestoes_api(lat, lon)
        else:
            # Para outros tipos, faz a verificação por CEP normal
            self.verificar_endereco_por_cep()

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
            elif self.current_divergence_type == 'cep_dup':
                updates['cep_dup'] = 1
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

    def buscar_sugestoes_api(self, lat, lon):
        """Versão usando run_with_spinner"""
        def consulta_api():
            try:
                _lat = float(lat.replace(',', '.'))
                _lon = float(lon.replace(',', '.'))
                return buscar_endereco_por_coordenadas(_lat, _lon)
            except ValueError:
                return None

        def atualizar_ui(endereco_api):
            if not endereco_api:
                return

            # Mapeamento entre campos da API e widgets de sugestão
            # Agora só precisamos do widget, sem informações de posicionamento
            campos_api = {
                'logradouro': self.logradouro_entry_sg,
                'bairro': self.bairro_entry_sg,
                'municipio': self.municipio_entry_sg,
                'localidade': self.localidade_entry_sg,
                'uf': self.uf_entry_sg,
                'cep': self.cep_entry_sg
            }

            for campo, widget_sg in campos_api.items():
                if valor := endereco_api.get(campo, ''):
                    widget_sg.config(
                        text=f"[API] {valor.upper()}",
                        fg='white',
                        bg='#0066cc',
                        font=('Helvetica', 8, 'italic', 'bold'),
                        height=1,
                        borderwidth=0,
                        highlightthickness=0,
                        anchor='w',
                        padx=5
                    )

        # Executa com spinner automático
        self.loading_spinner.run_with_spinner(
            target_func=consulta_api,
            callback=atualizar_ui
        )

    def verificar_endereco_por_cep(self):
        """Verifica e exibe sugestões de endereço baseadas no CEP"""
        try:
            cep = self.cep_entry.get().strip()
            dados_banco = self.controller.db.obter_dados_por_cep(cep)

            if not dados_banco:
                return

            # Mapeamento dos campos para verificação
            # Apenas os widgets, sem info de posicionamento
            campos_verificacao = {
                'logradouro': self.logradouro_entry_sg,
                'bairro': self.bairro_entry_sg,
                'municipio': self.municipio_entry_sg,
                'localidade': self.localidade_entry_sg,
                'uf': self.uf_entry_sg
            }

            # Atualiza apenas o texto das labels de sugestão
            for campo, widget_sg in campos_verificacao.items():
                #Carregar valor
                valor_correto = dados_banco.get(campo, '')
                if widget_sg and valor_correto:
                    widget_sg.config(
                        text=f"[ROTEIRO] {valor_correto.upper()}",
                        fg='white',
                        bg='#008000',
                        height=1,
                        borderwidth=0,
                        highlightthickness=0,
                        font=('Helvetica', 8, 'italic', 'bold'),
                        anchor='w',
                        padx=5
                    )
                    
        except Exception as e:
            print(f"Erro ao verificar endereço por CEP: {str(e)}")

    def limpar_sugestoes_anteriores(self):
        """Remove o texto de todas as sugestões anteriores"""
        for attr in ['logradouro', 'bairro', 'municipio', 'localidade', 'uf', 'cep']:
            entry_sg = getattr(self, f'{attr}_entry_sg', None)
            if entry_sg:
                entry_sg.config(text='', bg=self.inner_form.cget('bg'))

    def export_valid_surveys(self):
        """Exports validated surveys"""
        try:
            valid_surveys = self.controller.db.get_surveys_by_status(1)  # Status 1 = OK
            # Here you can implement export logic to CSV, Excel, etc.
            messagebox.showinfo("Exportação", f"{len(valid_surveys)} surveys válidos prontos para exportação!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao obter surveys válidos: {str(e)}")