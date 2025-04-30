import tkinter as tk
import os
from tkinter import ttk, messagebox
from tkinter import filedialog

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
    
    def import_bases(self):
        matrix_folder = self.matrix_path.get()
        
        if not matrix_folder:
            messagebox.showerror("Erro", "Selecione a pasta com os arquivos XML primeiro")
            return
        
        # Mapeamento dos arquivos XML e seus respectivos parsers
        xml_files = {
            'caixasopticas.xml': {
                'parser': self.controller.db.parse_caixas_opticas,
                'importer': self.controller.db.insert_caixas_opticas
            },
            'complementos.xml': {
                'parser': self.controller.db.parse_complementos,
                'importer': self.controller.db.insert_complementos
            },
            'empresas.xml': {
                'parser': self.controller.db.parse_empresas,
                'importer': self.controller.db.insert_empresas
            },
            'operadores.xml': {
                'parser': self.controller.db.parse_operadores,
                'importer': self.controller.db.insert_operadores
            },
            'roteiro.xml': {
                'parser': self.controller.db.parse_roteiros,
                'importer': self.controller.db.insert_roteiros
            },
            'tipos_imovel.xml': {
                'parser': self.controller.db.parse_tipos_imovel,
                'importer': self.controller.db.insert_tipos_imovel
            },
            'zonas.xml': {
                'parser': self.controller.db.parse_zonas,
                'importer': self.controller.db.insert_zonas
            }
        }
        
        imported_files = []
        error_occurred = False
        error_message = ""
        
        try:
            # Verificar se todos os arquivos necessários existem
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
            
            # Processar cada arquivo XML
            for xml_file, handlers in xml_files.items():
                file_path = os.path.join(matrix_folder, xml_file)
                
                try:
                    # Parsear o XML
                    data = handlers['parser'](file_path)
                    
                    # Importar para o banco de dados
                    handlers['importer'](data)
                    
                    imported_files.append(xml_file)
                    
                except Exception as e:
                    error_occurred = True
                    error_message = f"Erro ao processar {xml_file}:\n{str(e)}"
                    break
            
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
                    f"Todos os arquivos foram importados com sucesso!\n\n"
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