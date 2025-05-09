import tkinter as tk
import os
import threading
from database import Database
from tkinter import ttk, messagebox
from tkinter import filedialog
from xml_parser import XMLParser

class HomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Adicionar estes atributos para controlar o estado das operações
        self.running_validation = False  # Para controlar a validação
        self.running_import = False      # Para controlar a importação
        
        self.configure(bg='#f0f0f0')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Cabeçalho
        header = tk.Frame(self, bg='#2c3e50', padx=10, pady=10)
        header.grid(row=0, column=0, sticky='ew')
        
        tk.Label(
            header, text="AuditMap", 
            font=('Helvetica', 16, 'bold'), 
            fg='white', bg='#2c3e50'
        ).pack(side='left')
        
        # Corpo principal
        body = tk.Frame(self, bg='#f0f0f0', padx=20, pady=20)
        body.grid(row=1, column=0, sticky='nsew')
        
        # Seção de importação
        import_frame = tk.LabelFrame(body, text="Importar Bases", bg='#f0f0f0', font=('Helvetica', 10, 'bold'), padx=10, pady=10)
        import_frame.pack(fill='x', pady=(0, 20))
        
        # Matrix (XML)
        matrix_frame = tk.Frame(import_frame, bg='#f0f0f0')
        matrix_frame.pack(fill='x', pady=5)
        
        tk.Label(
            matrix_frame, text="Base Netwin (XML):", 
            font=('Helvetica', 10, 'bold'), bg='#f0f0f0'
        ).pack(side='left', padx=(0, 10))
        
        self.matrix_path = tk.StringVar()
        tk.Entry(
            matrix_frame, textvariable=self.matrix_path, 
            width=50, state='readonly', font=('Helvetica', 10)
        ).pack(side='left', expand=True, fill='x')
        
        tk.Button(
            matrix_frame, text="Selecionar Pasta", 
            command=self.select_matrix_folder, font=('Helvetica', 10, 'bold')
        ).pack(side='left', padx=(10, 0))
        
        # Campo (Excel)
        campo_frame = tk.Frame(import_frame, bg='#f0f0f0')
        campo_frame.pack(fill='x', pady=5)
        
        tk.Label(
            campo_frame, text="Base Campo (Excel):", 
            font=('Helvetica', 10, 'bold'), bg='#f0f0f0'
        ).pack(side='left', padx=(0, 10))
        
        self.campo_path = tk.StringVar()
        tk.Entry(
            campo_frame, textvariable=self.campo_path, 
            width=50, state='readonly', font=('Helvetica', 10)
        ).pack(side='left', expand=True, fill='x')
        
        tk.Button(
            campo_frame, text="Selecionar Arquivo", 
            command=self.select_campo_file, font=('Helvetica', 10, 'bold')
        ).pack(side='left', padx=(10, 0))
        
        # Botão de importar
        self.import_btn = tk.Button(
            import_frame, text="Importar Bases", 
            command=self.start_import_thread, bg='#3498db', fg='white', font=('Helvetica', 10, 'bold')
        )
        self.import_btn.pack(pady=(10, 0))
        
        # Progresso de importação (dentro da seção de importação)
        self.import_progress_frame = tk.Frame(import_frame, bg='#f0f0f0')
        
        self.import_progress_label = tk.Label(
            self.import_progress_frame, 
            text="",  # Texto será definido durante a operação
            font=('Helvetica', 10, 'bold'), 
            bg='#f0f0f0'
        )
        self.import_progress_label.pack(pady=(0, 5))
        
        self.import_progress = ttk.Progressbar(
            self.import_progress_frame, 
            mode='indeterminate',
            length=300
        )
        self.import_progress.pack(pady=(0, 5))

        # Nova seção para Técnico Responsável
        self.tecnico_frame = tk.LabelFrame(body, text="Técnico Responsável", bg='#f0f0f0', font=('Helvetica', 10, 'bold'), padx=10, pady=10)
        #self.tecnico_frame.pack(fill='x', pady=(0, 20))

        # Frame para os combobox
        combobox_frame = tk.Frame(self.tecnico_frame, bg='#f0f0f0')
        combobox_frame.pack(pady=5)

        # Variáveis para armazenar as seleções
        self.selected_tecnico = tk.StringVar()
        self.selected_empresa = tk.StringVar()

        # Combobox de Técnico
        self.tecnicos_cb = ttk.Combobox(
            combobox_frame, 
            textvariable=self.selected_tecnico,
            font=('Helvetica', 9),
            state='readonly',
            width=30
        )
        self.tecnicos_cb.grid(row=0, column=0, padx=(0, 10))

        # Combobox de Empresa
        self.empresas_cb = ttk.Combobox(
            combobox_frame, 
            textvariable=self.selected_empresa,
            font=('Helvetica', 9),
            state='readonly',
            width=30
        )
        self.empresas_cb.grid(row=0, column=1)

        # Configurar os eventos de seleção
        self.tecnicos_cb.bind('<<ComboboxSelected>>', self.on_tecnico_selected)
        self.empresas_cb.bind('<<ComboboxSelected>>', self.on_empresa_selected)

        # Atualizar os combobox com os dados do banco
        self.update_comboboxes()
        
        # Seção de validação
        self.validation_frame = tk.LabelFrame(body, text="Validação", bg='#f0f0f0', font=('Helvetica', 10, 'bold'), padx=10, pady=10)
        # Frame auxiliar para os botões
        button_container = tk.Frame(self.validation_frame, bg='#f0f0f0')
        button_container.pack(pady=(0, 10), anchor='center')  # Centraliza o frame
        
        self.validation_btn = tk.Button(
            button_container, text="Validar Endereços", 
            command=self.start_validation_thread, state='disabled', bg='#2ecc71', fg='white', font=('Helvetica', 10, 'bold')
        )

        self.correct_btn = tk.Button(
            button_container, text="Resultado da validação", 
            command=self.validation_show_frame, bg='#3498db', fg='white', font=('Helvetica', 10, 'bold')
        )
        
        # Progresso de validação (dentro da seção de validação)
        self.validation_progress_frame = tk.Frame(self.validation_frame, bg='#f0f0f0')
        
        self.validation_progress_label = tk.Label(
            self.validation_progress_frame, 
            text="",  # Texto será definido durante a operação
            font=('Helvetica', 10, 'bold'), 
            bg='#f0f0f0'
        )
        self.validation_progress_label.pack(pady=(0, 5))
        
        self.validation_progress = ttk.Progressbar(
            self.validation_progress_frame, 
            mode='determinate',
            length=300,
            maximum=100
        )
        self.validation_progress.pack(pady=(0, 5))
        
        # Status
        self.status_label = tk.Label(
            body, text="Nenhuma base importada", 
            font=('Helvetica', 12, 'bold'), bg='#f0f0f0', fg='#7f8c8d'
        )
        #self.status_label.pack(pady=(20, 0))

        self.after_idle(self.check_existing_validated_data)

    def validation_show_frame(self):
        self.controller.show_frame('ValidationFrame')

    def get_selecao_atual(self):
        """Retorna o técnico e a empresa atualmente selecionados"""
        tecnico_nome = self.selected_tecnico.get()
        empresa_nome = self.selected_empresa.get()
        return tecnico_nome, empresa_nome

    def check_existing_validated_data(self):
        try:
            db = Database()
            db.connect()

            # Verificar se já existem dados validados
            total_registros = db.count_total_registros_survey()

            # Obter último técnico e empresa
            ultimo = db.get_tecnico_empresa_surveys()

            # Recupera registros importados
            registros_importados = db.obter_importacoes()

            # Obter estatísticas usando a mesma conexão
            stats = db.get_divergence_types()

            db.close()

            if total_registros > 0:
                self.tecnico_frame.pack(fill='x', pady=(0, 20))
                self.validation_btn.config(text="Revalidar Endereços")
                self.validation_btn.config(state='normal')
                self.has_validated_data = True
                self.validation_frame.pack(fill='x', pady=(0, 20))
                self.validation_btn.pack(side='left', padx=5)
                self.correct_btn.pack(side='left', padx=5)

                if ultimo:
                    #Selecionar último técnico
                    self.selected_tecnico.set(ultimo['tecnico_nome'])

                    # Forçar atualização dos comboboxes
                    self.on_tecnico_selected()

                # Preencher entry com caminho recuperado matriz
                if "Folder" in registros_importados:
                    self.matrix_path.set(registros_importados["Folder"]["file_path"])

                # Preencher entry com caminho recuperado campo excel
                if "Excel (.xlsx)" in registros_importados:
                    self.campo_path.set(registros_importados["Excel (.xlsx)"]["file_path"])

                # Atualizar status na interface
                self.status_label.config(
                    text=f"Validação concluída - OK: {stats['registros_ok']}, Divergentes: {stats['registros_divergentes']}, Não encontrados: {stats['nao_encontrado']}",
                    fg='#27ae60'
                )
                self.status_label.pack(pady=(20, 0))
            else:
                self.validation_btn.config(text="Validar Endereços")
                self.has_validated_data = False
                self.validation_btn.pack(side='left', padx=5)
                self.correct_btn.pack_forget()  # Esconder botão corrigir divergências

        except Exception as e:
            print(f"Erro ao verificar registros validados: {e}")
            self.has_validated_data = False

    def update_comboboxes(self):
        """Atualiza os comboboxes com dados do banco"""
        empresas = self.controller.db.get_empresas()
        
        # Lista de todos os técnicos
        tecnicos = []
        for emp in empresas:
            tecnicos.extend([(tec['nome_tecnico'], emp['nome_empresa']) for tec in emp['tecnicos']])
        
        # Remove duplicados mantendo a ordem
        unique_tecnicos = []
        seen = set()
        for nome, empresa in tecnicos:
            if nome not in seen:
                seen.add(nome)
                unique_tecnicos.append(nome)
        
        # Adiciona valor padrão em maiúsculo
        unique_tecnicos.insert(0, "TÉCNICO")
        
        self.tecnicos_cb['values'] = unique_tecnicos
        if unique_tecnicos:
            self.tecnicos_cb.current(0)
            # Força a atualização do combobox de empresas
            self.empresas_cb['values'] = ["EMPRESA"]
            self.empresas_cb.current(0)

    def on_tecnico_selected(self, event=None):
        """Atualiza empresas quando um técnico é selecionado"""
        tecnico_nome = self.selected_tecnico.get()
        empresas = self.controller.db.get_empresas()
        
        if tecnico_nome == "TÉCNICO":
            # Restaura todas as empresas disponíveis
            todas_empresas = [emp['nome_empresa'] for emp in empresas]
            todas_empresas.insert(0, "EMPRESA")
            self.empresas_cb['values'] = todas_empresas
            self.empresas_cb.current(0)
            self.status_label.pack_forget()
            self.validation_frame.pack_forget()
            return
        else:
            # Mostra o frame quando um técnico válido é selecionado
            self.validation_frame.pack(fill='x')
            self.status_label.pack(pady=(20, 0))

        # Encontra empresas associadas ao técnico selecionado
        empresas_do_tecnico = []
        empresa_selecionada = None
        for emp in empresas:
            for tec in emp['tecnicos']:
                if tec['nome_tecnico'] == tecnico_nome:
                    empresa_selecionada = emp['nome_empresa']
                    empresas_do_tecnico.append(emp['nome_empresa'])
                    break

        # Adiciona o valor padrão "EMPRESA" no início
        empresas_do_tecnico.insert(0, "EMPRESA")
        
        self.empresas_cb['values'] = empresas_do_tecnico

        # Seleciona automaticamente a empresa do técnico, se encontrada
        if empresa_selecionada:
            self.empresas_cb.set(empresa_selecionada)
        else:
            self.empresas_cb.current(0)

    def on_empresa_selected(self, event=None):
        """Atualiza técnicos quando uma empresa é selecionada"""
        empresa_nome = self.selected_empresa.get()
        empresas = self.controller.db.get_empresas()
        
        if empresa_nome == "EMPRESA":
            # Restaura todos os técnicos disponíveis
            todos_tecnicos = []
            seen = set()
            for emp in empresas:
                for tec in emp['tecnicos']:
                    if tec['nome_tecnico'] not in seen:
                        seen.add(tec['nome_tecnico'])
                        todos_tecnicos.append(tec['nome_tecnico'])
            todos_tecnicos.insert(0, "TÉCNICO")
            self.tecnicos_cb['values'] = todos_tecnicos
            self.tecnicos_cb.current(0)
            self.status_label.pack_forget()
            self.validation_frame.pack_forget()
            return
            
        # Encontra técnicos associados à empresa selecionada
        tecnicos_da_empresa = []
        for emp in empresas:
            if emp['nome_empresa'] == empresa_nome:
                tecnicos_da_empresa = [tec['nome_tecnico'] for tec in emp['tecnicos']]
                break
        
        # Adiciona valor padrão "TÉCNICO" no início
        tecnicos_da_empresa.insert(0, "TÉCNICO")
        
        self.tecnicos_cb['values'] = tecnicos_da_empresa
        self.tecnicos_cb.current(0)

    def update_progress_bar(self, current, total):
        percent = int((current / total) * 100)
        self.validation_progress['value'] = percent
        self.validation_progress_label.config(text=f"Validando dados... {percent}%")
        self.update_idletasks()

    def show_import_progress(self, message):
        """Mostra o indicador de progresso de importação"""
        #Desabilitar frame tecnico responsavel e validação
        self.status_label.pack_forget()
        self.validation_frame.pack_forget()
        self.tecnico_frame.pack_forget()

        #Selecionar último técnico
        self.selected_tecnico.set('TÉCNICO')

        # Forçar atualização dos comboboxes
        self.on_tecnico_selected()

        #ITERAR PROGRESS BAR
        self.import_progress_label.config(text=message)
        self.import_progress_frame.pack(fill='x', pady=(10, 0))
        self.import_progress.start()
        self.import_btn.config(state='disabled')
        self.update()
    
    def hide_import_progress(self):
        """Esconde o indicador de progresso de importação"""
        self.import_progress.stop()
        self.import_progress_frame.pack_forget()
        self.import_btn.config(state='normal')
        self.check_existing_validated_data()
        self.update()
    
    def show_validation_progress(self, message):
        """Mostra o indicador de progresso de validação"""
        self.validation_progress_label.config(text=message)
        self.validation_progress_frame.pack(fill='x', pady=(10, 0))
        self.validation_btn.config(state='disabled')
        self.update()
    
    def hide_validation_progress(self):
        """Esconde o indicador de progresso de validação"""
        self.validation_progress.stop()
        self.validation_progress_frame.pack_forget()
        self.validation_btn.config(state='normal')
        self.check_existing_validated_data()
        self.update()

    def select_matrix_folder(self):
        folder_path = filedialog.askdirectory(title="Selecione a pasta com os arquivos XML")
        if folder_path:
            self.matrix_path.set(folder_path)
            self.check_import_ready()
    
    def select_campo_file(self):
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo Excel de campo",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if file_path:
            self.campo_path.set(file_path)
            self.check_import_ready()
    
    def check_import_ready(self):
        if self.matrix_path.get() and self.campo_path.get():
            self.validation_btn.config(state='normal')
    
    def start_import_thread(self):
        """Inicia a importação em uma thread separada"""
        if not messagebox.askyesno(
            "Confirmar Importação",
            "Deseja importar todas as bases? Esta operação pode demorar alguns minutos."
        ):
            return
        
        if self.running_import:
            return
            
        self.show_import_progress("Importando bases de dados...")
        
        # Criar e iniciar a thread de importação
        import_thread = threading.Thread(
            target=self.import_bases_thread,
            args=(self.matrix_path.get(), self.campo_path.get()),
            daemon=True
        )
        import_thread.start()
    
    def start_validation_thread(self):
        """Inicia a validação em uma thread separada"""
        if self.has_validated_data:
            confirm = messagebox.askyesno(
                "Revalidar Endereços",
                "Já existem dados validados!\nSe prosseguir com a revalidação, os dados já validados serão perdidos.\n\nDeseja prosseguir?"
            )
        else:
            confirm = messagebox.askyesno(
                "Confirmar Validação",
                "Deseja validar todos os endereços? Esta operação pode demorar alguns minutos."
            )

        if not confirm:
            return

        if self.running_validation:
            return

        self.running_validation = True
        self.show_validation_progress("Validando endereços...")

        validation_thread = threading.Thread(
            target=self.validate_addresses_thread,
            daemon=True
        )
        validation_thread.start()
    
    def validate_addresses_thread(self):
        """Função executada na thread separada para validação"""
        try:
            # Cria uma nova instância do Database para esta thread
            db = Database()  # Isso cria uma nova conexão
            db.connect()     # Garante que a conexão está ativa

            total_registros = db.count_total_registros_campo()

            # Passe a função de callback corretamente
            progress_callback = lambda current: self.update_progress_bar(current, total_registros)

            #Armazenar o nome do técnico
            tecnico_nome = self.get_selecao_atual()[0]

            # Chamar a função de validação usando a nova conexão
            success, message = db.import_and_validate_surveys(tecnico_nome ,progress_callback=progress_callback)
            
            # Obter estatísticas usando a mesma conexão
            stats = db.get_divergence_types()
            
            # Atualizar a interface na thread principal
            self.after(0, self.on_validation_complete, success, message, stats)
            
        except Exception as e:
            self.after(0, self.on_validation_error, str(e))
        finally:
            self.running_validation = False
            if db:
                db.close()  # Fecha a conexão quando terminar
    
    def on_validation_complete(self, success, message, stats):
        """Chamado quando a validação é concluída"""
        self.hide_validation_progress()
        
        if success:
            # Mostrar mensagem com resumo
            messagebox.showinfo(
                "Validação Concluída",
                f"Validação realizada com sucesso!\n\n"
                f"Total de endereços: {stats['total_registros']}\n"
                f"Endereços OK: {stats['registros_ok']}\n"
                f"Endereços com divergência: {stats['registros_divergentes']}\n"
                f"Endereços não encontrados: {stats['nao_encontrado']}"
            )
            
            # Atualizar status na interface
            self.status_label.config(
                text=f"Validação concluída - OK: {stats['registros_ok']}, Divergentes: {stats['registros_divergentes']}, Não encontrados: {stats['nao_encontrado']}",
                fg='#27ae60'
            )
            self.validation_btn.config(text="Revalidar Endereços")
            
            # Atualizar os dados na interface principal
            if hasattr(self.controller, 'frames') and hasattr(self.controller, 'VALIDATION_FRAME'):
                if self.controller.VALIDATION_FRAME in self.controller.frames:
                    self.controller.show_frame(self.controller.VALIDATION_FRAME)
                    self.controller.frames[self.controller.VALIDATION_FRAME].update_data()
        else:
            messagebox.showerror("Erro na Validação", message)
            self.status_label.config(text="Erro na validação", fg='#e74c3c')
    
    def on_validation_error(self, error_msg):
        """Chamado quando ocorre um erro na validação"""
        self.hide_validation_progress()
        messagebox.showerror("Erro", f"Falha ao validar endereços: {error_msg}")
        self.status_label.config(text="Erro na validação", fg='#e74c3c')
    
    def import_bases_thread(self, matrix_folder, campo_file):
        """Função executada na thread separada para importação"""
        try:
            # Cria uma nova instância do Database para esta thread
            db = Database()
            db.connect()

            # Mapeamento dos arquivos XML e seus respectivos parsers
            xml_files = {
                'caixasopticas.xml': {
                    'parser': XMLParser.parse_caixas_opticas,
                    'importer': db.insert_caixas_opticas
                },
                'complementos.xml': {
                    'parser': XMLParser.parse_complementos,
                    'importer': db.insert_complementos
                },
                'empresas.xml': {
                    'parser': XMLParser.parse_empresas,
                    'importer': db.insert_empresas
                },
                'operadores.xml': {
                    'parser': XMLParser.parse_operadores,
                    'importer': db.insert_operadores
                },
                'roteiro.xml': {
                    'parser': XMLParser.parse_roteiros,
                    'importer': db.insert_roteiros
                },
                'tipos_imovel.xml': {
                    'parser': XMLParser.parse_tipos_imovel,
                    'importer': db.insert_tipos_imovel
                },
                'zonas.xml': {
                    'parser': XMLParser.parse_zonas,
                    'importer': db.insert_zonas
                }
            }
            
            imported_files = []
            error_occurred = False
            error_message = ""
            
            # Verificar se todos os arquivos XML necessários existem
            missing_files = []
            for xml_file in xml_files.keys():
                if not os.path.exists(os.path.join(matrix_folder, xml_file)):
                    missing_files.append(xml_file)
            
            if missing_files:
                self.after(0, self.on_import_error, 
                          f"Os seguintes arquivos não foram encontrados na pasta:\n{', '.join(missing_files)}")
                return
            
            # Iniciar transação
            db.conn.execute("BEGIN TRANSACTION")
            
            # 1. Processar cada arquivo XML
            for xml_file, handlers in xml_files.items():
                file_path = os.path.join(matrix_folder, xml_file)
                
                try:
                    # Chamar o método estático diretamente na classe
                    data = handlers['parser'](file_path)
                    
                    # Importar para o banco de dados
                    handlers['importer'](data)
                    
                    imported_files.append(xml_file)
                    
                except Exception as e:
                    error_occurred = True
                    error_message = f"Erro ao processar {xml_file}:\n{str(e)}"
                    break
            
            # 2. Se os XMLs foram importados com sucesso, processar o Excel de campo
            if not error_occurred:
                try:
                    # Ler dados do Excel
                    excel_data = self.read_excel_data(campo_file)
                    
                    # Importar dados de campo
                    success, message = db.import_excel_data(campo_file, excel_data)
                    
                    if not success:
                        error_occurred = True
                        error_message = f"Erro ao importar Excel de campo:\n{message}"
                    else:
                        imported_files.append(os.path.basename(campo_file))
                
                except Exception as e:
                    error_occurred = True
                    error_message = f"Erro ao processar arquivo Excel:\n{str(e)}"
            
            if error_occurred:
                # Rollback em caso de erro
                db.conn.rollback()
                self.after(0, self.on_import_error, error_message)
            else:
                # Commit se tudo ocorrer bem
                db.conn.commit()
                self.after(0, self.on_import_complete, imported_files)

                # Registrar a importação no banco de dados
                db.registrar_importacao("Folder",matrix_folder)
                db.registrar_importacao("Excel (.xlsx)",campo_file)
        
        except Exception as e:
            db.conn.rollback()
            self.after(0, self.on_import_error, f"Ocorreu um erro inesperado:\n{str(e)}")
        finally:
            db.close()  # Fecha a conexão quando terminar
    
    def on_import_complete(self, imported_files):
        """Chamado quando a importação é concluída com sucesso"""
        self.hide_import_progress()
        messagebox.showinfo(
            "Importação concluída", 
            f"Todas as bases foram importadas com sucesso!\n\n"
            f"Arquivos processados:\n{', '.join(imported_files)}"
        )
        self.tecnico_frame.pack(fill='x', pady=(0, 20))
        self.status_label.config(text="Bases prontas para validação", fg='#27ae60')
        self.validation_btn.config(text="Validar Endereços")
        self.validation_btn.config(state='normal')
    
    def on_import_error(self, error_message):
        """Chamado quando ocorre um erro na importação"""
        self.hide_import_progress()
        messagebox.showerror("Erro na Importação", error_message)
        self.status_label.config(text="Erro na importação", fg='#e74c3c')
    
    def read_excel_data(self, file_path):
        """Lê o arquivo Excel com tratamento robusto de tipos e formata Latitude/Longitude"""
        try:
            import pandas as pd

            # Ler o arquivo Excel forçando Latitude e Longitude como texto
            df = pd.read_excel(file_path, dtype={'Latitude': str, 'Longitude': str})

            # Renomear coluna para nome consistente (se existir)
            if 'Weblink: EndereÃ§o completo' in df.columns:
                df.rename(columns={'Weblink: EndereÃ§o completo': 'Weblink: Endereço completo'}, inplace=True)

            # Verificar se a coluna de endereço existe
            endereco_col = 'Weblink: Endereço completo'
            if endereco_col not in df.columns:
                raise ValueError(f"Coluna de endereço ('{endereco_col}') não encontrada")
            
            def corrigir_codificacao(texto):
                try:
                    if pd.isna(texto):
                        return None
                    return texto.encode('latin1').decode('utf-8')
                except:
                    return texto  # Retorna como está se der erro

            # Função para processar o campo de endereço
            def processar_endereco(endereco):
                try:
                    endereco_codificado = corrigir_codificacao(endereco)
                    if pd.isna(endereco_codificado):
                        return {'endereco': None, 'bairro': None, 'cep': None, 'pais': None}
                    endereco_str = str(endereco_codificado).strip()
                    if not endereco_str:
                        return {'endereco': None, 'bairro': None, 'cep': None, 'pais': None}
                    partes = [p.strip() for p in endereco_str.split(',') if p.strip()]
                    return {
                        'endereco': partes[0] if len(partes) > 0 else None,
                        'bairro': partes[1] if len(partes) > 1 else None,
                        'cep': partes[2].replace('-', '') if len(partes) > 2 else None,
                        'pais': partes[3] if len(partes) > 3 else None
                    }
                except Exception as e:
                    print(f"Erro ao processar endereço '{endereco_codificado}': {str(e)}")
                    return {'endereco': str(endereco_codificado), 'bairro': None, 'cep': None, 'pais': None}

            # Função para formatar latitude e longitude
            def format_latlon(value):
                if pd.isna(value):
                    return None
                try:
                    value = str(value).strip().replace('.', '')  # Remove pontos
                    is_negative = value.startswith('-')
                    if is_negative:
                        value = value[1:]
                    formatted = value[:2] + ',' + value[2:]
                    return '-' + formatted if is_negative else formatted
                except Exception as e:
                    print(f"Erro ao formatar latitude/longitude: {value} -> {e}")
                    return None

            # Processar e expandir colunas de endereço
            enderecos_processados = df[endereco_col].apply(processar_endereco)
            df = df.join(pd.json_normalize(enderecos_processados))

            # Aplicar formatação em Latitude e Longitude (se existirem)
            if 'Latitude' in df.columns:
                df['Latitude'] = df['Latitude'].apply(format_latlon)
            if 'Longitude' in df.columns:
                df['Longitude'] = df['Longitude'].apply(format_latlon)

            # Função para converter valores para strings inteiros
            def converter_para_str_int(valor):
                if pd.isna(valor):
                    return None
                try:
                    valor_str = str(valor)
                    if valor_str.endswith('.0'):
                        valor_str = valor_str[:-2]  # Remove o ".0"
                    return valor_str
                except Exception:
                    return str(valor)

            # Aplicar conversão nas colunas que devem ser inteiras
            if 'Nº Fachada' in df.columns:
                df['Nº Fachada'] = df['Nº Fachada'].apply(converter_para_str_int)

            if 'Weblink: Quantidade' in df.columns:
                df['Weblink: Quantidade'] = df['Weblink: Quantidade'].apply(converter_para_str_int)

            if 'Weblink: Pavimento' in df.columns:
                df['Weblink: Pavimento'] = df['Weblink: Pavimento'].apply(converter_para_str_int)

            if 'hps' in df.columns:
                df['hps'] = df['hps'].apply(converter_para_str_int)

            if 'Postes' in df.columns:
                df['Postes'] = df['Postes'].apply(converter_para_str_int)

            # Converter para lista de dicionários
            data = df.to_dict('records')

            if data[0]: 
                data 
            else:
                self.status_label.config(text="Nenhum dado encontrado", fg='#7f8c8d')
                
            return data

        except Exception as e:
            raise Exception(f"Erro ao ler Excel: {str(e)}")
        
    def validate_addresses(self):
        """Chama a validação dos endereços após confirmação"""
        if not messagebox.askyesno(
            "Confirmar Validação",
            "Deseja validar todos os endereços? Esta operação pode demorar alguns minutos."
        ):
            return
        
        # Mostrar status de processamento
        self.status_label.config(text="Validando endereços...", fg='#f39c12')
        self.update()  # Atualizar a interface
        
        try:
            # Chamar a função de validação do banco de dados
            success, message = self.controller.db.import_and_validate_surveys()
            
            if success:
                # Obter estatísticas
                stats = self.controller.db.get_divergence_types()
                
                # Mostrar mensagem com resumo
                messagebox.showinfo(
                    "Validação Concluída",
                    f"Validação realizada com sucesso!\n\n"
                    f"Total de endereços: {stats['total_registros']}\n"
                    f"Endereços OK: {stats['registros_ok']}\n"
                    f"Endereços com divergência: {stats['registros_divergentes']}\n"
                    f"Endereços não encontrados: {stats['nao_encontrado']}"
                )
                
                # Atualizar status na interface
                self.status_label.config(
                    text=f"Validação concluída - OK: {stats['registros_ok']}, Divergentes: {stats['registros_divergentes']}, Não encontrados: {stats['nao_encontrado']}",
                    fg='#27ae60'
                )
                
                # Mostrar frame de validação com resultados
                self.controller.show_frame(self.controller.VALIDATION_FRAME)
                self.controller.frames[self.controller.VALIDATION_FRAME].update_data()
            else:
                messagebox.showerror("Erro na Validação", message)
                self.status_label.config(text="Erro na validação", fg='#e74c3c')
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao validar endereços: {str(e)}")
            self.status_label.config(text="Erro na validação", fg='#e74c3c')
    
    def update_data(self):
        # Atualizar status quando a tela é mostrada
        pass