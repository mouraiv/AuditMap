import tkinter as tk
import os
import pandas as pd
from tkinter import ttk, messagebox
from tkinter import filedialog
from xml_parser import XMLParser

class HomeFrame(tk.Frame):
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
            header, text="AuditMap", 
            font=('Helvetica', 16, 'bold'), 
            fg='white', bg='#2c3e50'
        ).pack(side='left')
        
        # Corpo principal
        body = tk.Frame(self, bg='#f0f0f0', padx=20, pady=20)
        body.grid(row=1, column=0, sticky='nsew')
        
        # Seção de importação
        import_frame = tk.LabelFrame(body, text="Importar Bases", bg='#f0f0f0', padx=10, pady=10)
        import_frame.pack(fill='x', pady=(0, 20))
        
        # Matrix (XML)
        matrix_frame = tk.Frame(import_frame, bg='#f0f0f0')
        matrix_frame.pack(fill='x', pady=5)
        
        tk.Label(
            matrix_frame, text="Base Matrix (XML):", 
            font=('Helvetica', 10), bg='#f0f0f0'
        ).pack(side='left', padx=(0, 10))
        
        self.matrix_path = tk.StringVar()
        tk.Entry(
            matrix_frame, textvariable=self.matrix_path, 
            width=50, state='readonly'
        ).pack(side='left', expand=True, fill='x')
        
        tk.Button(
            matrix_frame, text="Selecionar Pasta", 
            command=self.select_matrix_folder
        ).pack(side='left', padx=(10, 0))
        
        # Campo (Excel)
        campo_frame = tk.Frame(import_frame, bg='#f0f0f0')
        campo_frame.pack(fill='x', pady=5)
        
        tk.Label(
            campo_frame, text="Base Campo (Excel):", 
            font=('Helvetica', 10), bg='#f0f0f0'
        ).pack(side='left', padx=(0, 10))
        
        self.campo_path = tk.StringVar()
        tk.Entry(
            campo_frame, textvariable=self.campo_path, 
            width=50, state='readonly'
        ).pack(side='left', expand=True, fill='x')
        
        tk.Button(
            campo_frame, text="Selecionar Arquivo", 
            command=self.select_campo_file
        ).pack(side='left', padx=(10, 0))
        
        # Botão de importar
        tk.Button(
            import_frame, text="Importar Bases", 
            command=self.import_bases, bg='#3498db', fg='white'
        ).pack(pady=(10, 0))
        
        # Seção de validação
        validation_frame = tk.LabelFrame(body, text="Validação", bg='#f0f0f0', padx=10, pady=10)
        validation_frame.pack(fill='x')
        
        self.validation_btn = tk.Button(
            validation_frame, text="Validar Endereços", 
            command=self.validate_addresses, state='disabled', bg='#2ecc71', fg='white'
        )
        self.validation_btn.pack(pady=10)
        
        # Status
        self.status_label = tk.Label(
            body, text="Nenhuma base importada", 
            font=('Helvetica', 9), bg='#f0f0f0', fg='#7f8c8d'
        )
        self.status_label.pack(pady=(20, 0))
    
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
                print(f"\nColunas disponíveis no arquivo: {df.columns.tolist()}")
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

            # Função para converter valores para inteiros, se possível
            def converter_para_inteiro(valor):
                if pd.isna(valor):
                    return None
                try:
                    return int(valor)
                except ValueError:
                    return valor  # Caso não seja um número inteiro, retorna o valor original

            # Aplicar conversão nas colunas que devem ser inteiras
            if 'Nº Fachada' in df.columns:
                df['Nº Fachada'] = df['Nº Fachada'].apply(converter_para_inteiro)

            if 'Weblink: Quantidade' in df.columns:
                df['Weblink: Quantidade'] = df['Weblink: Quantidade'].apply(converter_para_inteiro)

            if 'Weblink: Pavimento' in df.columns:
                df['Weblink: Pavimento'] = df['Weblink: Pavimento'].apply(converter_para_inteiro)

            if 'hps' in df.columns:
                df['hps'] = df['hps'].apply(converter_para_inteiro)

            if 'Postes' in df.columns:
                df['Postes'] = df['Postes'].apply(converter_para_inteiro)

            # Converter para lista de dicionários
            data = df.to_dict('records')

            print("\nExemplo de registro processado:")
            print(data[0] if data else "Nenhum dado encontrado")

            return data

        except Exception as e:
            raise Exception(f"Erro ao ler Excel: {str(e)}")
        
    def import_bases(self):
        matrix_folder = self.matrix_path.get()
        campo_file = self.campo_path.get()
        
        if not matrix_folder or not campo_file:
            messagebox.showerror("Erro", "Selecione tanto a pasta com os arquivos XML quanto o arquivo Excel de campo")
            return
        
        # Mapeamento dos arquivos XML e seus respectivos parsers (usando métodos estáticos)
        xml_files = {
            'caixasopticas.xml': {
                'parser': XMLParser.parse_caixas_opticas,  # Método estático
                'importer': self.controller.db.insert_caixas_opticas
            },
            'complementos.xml': {
                'parser': XMLParser.parse_complementos,
                'importer': self.controller.db.insert_complementos
            },
            'empresas.xml': {
                'parser': XMLParser.parse_empresas,
                'importer': self.controller.db.insert_empresas
            },
            'operadores.xml': {
                'parser': XMLParser.parse_operadores,
                'importer': self.controller.db.insert_operadores
            },
            'roteiro.xml': {
                'parser': XMLParser.parse_roteiros,
                'importer': self.controller.db.insert_roteiros
            },
            'tipos_imovel.xml': {
                'parser': XMLParser.parse_tipos_imovel,
                'importer': self.controller.db.insert_tipos_imovel
            },
            'zonas.xml': {
                'parser': XMLParser.parse_zonas,
                'importer': self.controller.db.insert_zonas
            }
        }
        
        imported_files = []
        error_occurred = False
        error_message = ""
        
        try:
            # Verificar se todos os arquivos XML necessários existem
            missing_files = []
            for xml_file in xml_files.keys():
                if not os.path.exists(os.path.join(matrix_folder, xml_file)):
                    missing_files.append(xml_file)
            
            if missing_files:
                messagebox.showerror(
                    "Arquivos faltando", 
                    f"Os seguintes arquivos não foram encontrados na pasta:\n{', '.join(missing_files)}"
                )
                return
            
            # Iniciar transação
            self.controller.db.conn.execute("BEGIN TRANSACTION")
            
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
                    success, message = self.controller.db.import_excel_data(campo_file, excel_data)
                    
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
                self.controller.db.conn.rollback()
                messagebox.showerror("Erro na Importação", error_message)
                self.status_label.config(text="Erro na importação", fg='#e74c3c')
            else:
                # Commit se tudo ocorrer bem
                self.controller.db.conn.commit()
                messagebox.showinfo(
                    "Importação concluída", 
                    f"Todas as bases foram importadas com sucesso!\n\n"
                    f"Arquivos processados:\n{', '.join(imported_files)}"
                )
                self.status_label.config(text="Bases prontas para validação", fg='#27ae60')
                self.validation_btn.config(state='normal')
        
        except Exception as e:
            self.controller.db.conn.rollback()
            messagebox.showerror("Erro Fatal", f"Ocorreu um erro inesperado:\n{str(e)}")
            self.status_label.config(text="Erro na importação", fg='#e74c3c')
    
    def validate_addresses(self):
        self.controller.show_frame(self.controller.VALIDATION_FRAME)
    
    def update_data(self):
        # Atualizar status quando a tela é mostrada
        pass