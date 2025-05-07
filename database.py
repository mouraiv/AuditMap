import sqlite3
import re
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
class Database:
    def __init__(self, db_name="auditmap.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()  # Conexão inicial para a thread principal

    def connect(self):
        """Cria uma nova conexão para a thread atual"""
        if self.conn:
            self.close()  # Fecha a conexão existente se houver
            
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        return self.conn
    
    def initialize_db(self):
        """Inicializa o banco de dados (cria tabelas se não existirem)"""
        try:
            # Tabela para armazenar as caixas ópticas
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS caixas_opticas (
                    id INTEGER PRIMARY KEY,
                    id_caixa INTEGER,
                    fabricante TEXT,
                    capacidade INTEGER,
                    designacao TEXT,
                    tipo_caixa TEXT,
                    altura INTEGER,
                    largura INTEGER,
                    profundidade INTEGER
                )
            ''')
            
            # Tabela para complementos
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS complementos (
                    id INTEGER PRIMARY KEY,
                    id_complemento INTEGER,
                    arg1_obrig TEXT,
                    arg2_obrig TEXT,
                    arg3_obrig TEXT,
                    arg4_obrig TEXT,
                    arg5_obrig TEXT,
                    tipo1 TEXT,
                    tipo2 TEXT,
                    tipo3 TEXT,
                    tipo4 TEXT,
                    tipo5 TEXT,
                    abrev TEXT,
                    tipo3_principal TEXT,
                    tipo_survey_tipo_3 TEXT,
                    visibilidade TEXT,
                    descricao TEXT
                )
            ''')
            
            # Tabela para empresas e técnicos
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS empresas (
                    id INTEGER PRIMARY KEY,
                    id_empresa INTEGER,
                    nome_empresa TEXT
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tecnicos (
                    id INTEGER PRIMARY KEY,
                    id_empresa INTEGER,
                    id_tecnico INTEGER,
                    nome_tecnico TEXT,
                    FOREIGN KEY (id_empresa) REFERENCES empresas (id)
                )
            ''')
            
            # Tabela para operadores
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS operadores (
                    id INTEGER PRIMARY KEY,
                    id_operador INTEGER,
                    nome_operador TEXT
                )
            ''')
            
            # Tabela para roteiros (endereços matrix)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS roteiros (
                    id INTEGER PRIMARY KEY,
                    id_roteiro INTEGER,
                    uf TEXT,
                    uf_abrev TEXT,
                    cod_municipio INTEGER,
                    municipio TEXT,
                    id_localidade INTEGER,
                    cod_localidade INTEGER,
                    localidade TEXT,
                    localidade_abrev TEXT,
                    cod_bairro INTEGER,
                    bairro TEXT,
                    cod_lograd INTEGER,
                    nome_lograd TEXT,
                    id_tipo_lograd INTEGER,
                    tipo_lograd TEXT,
                    tipo_lograd_abrev TEXT,
                    id_titulo INTEGER,
                    titulo TEXT,
                    titulo_abrev TEXT,
                    cep TEXT
                )
            ''')
            
            # Tabela para tipos de imóvel
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tipos_imovel (
                    id INTEGER PRIMARY KEY,
                    id_tipo INTEGER,
                    tipo_imovel TEXT,
                    abrev TEXT,
                    arg_obrig TEXT,
                    visibilidade TEXT
                )
            ''')
            
            # Tabela para zonas
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS zonas (
                    id INTEGER PRIMARY KEY,
                    codigo TEXT,
                    nome TEXT
                )
            ''')
            
            # Tabela para dados de campo
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS campo (
                    id INTEGER PRIMARY KEY,
                    latitude TEXT, 
                    longitude TEXT,
                    numero_fachada TEXT,
                    tipo_imovel TEXT,
                    pavimento TEXT,
                    endereco_completo TEXT,
                    bairro TEXT,
                    cep TEXT,
                    pais TEXT,
                    complemento TEXT,
                    quantidade TEXT,
                    data TEXT
                )
            ''')
            
            # Tabela para logs de importação
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS import_logs (
                    id INTEGER PRIMARY KEY,
                    file_type TEXT,
                    file_path TEXT,
                    import_date TEXT
                )
            ''')

            # Tabela para syrvey de campo
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS survey (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo_survey INTEGER NOT NULL DEFAULT 1,
                    versao TEXT,
                    autorizacao TEXT,
                    gravado BOOLEAN,
                    idCEMobile INTEGER,
                    coordX TEXT,
                    coordY TEXT,
                    codigoZona TEXT,
                    nomeZona TEXT,
                    localidade TEXT,
                    logradouro TEXT,
                    numero_fachada TEXT,
                    id_complemento1 INTEGER,
                    argumento1 TEXT,
                    id_complemento3 INTEGER, -- pode ser usado também pela UC
                    cep TEXT,
                    cod_bairro INTEGER,
                    bairro TEXT,
                    id_roteiro INTEGER,
                    id_localidade INTEGER,
                    cod_lograd INTEGER,
                    tecnico_id INTEGER,
                    tecnico_nome TEXT,
                    empresa_id INTEGER,
                    empresa_nome TEXT,
                    data TEXT,
                    observacoes TEXT,
                    totalUCs INTEGER,
                    numPisos INTEGER,
                    ocupacao TEXT,
                    redeInterna TEXT,
                    fotoExteriorEdificio TEXT,
                    fotoFachadaEdificio TEXT,
                    status INTEGER DEFAULT 3, -- 1 = OK, 2 = Divergente, 3 = Não encontrado
                    lograd_div INTEGER DEFAULT 0, -- 1 = OK, 2 = Divergente
                    bairro_div INTEGER DEFAULT 0, -- 1 = OK, 2 = Divergente
                    cep_div INTEGER DEFAULT 0, -- 1 = OK, 2 = Divergente
                    baixado BOOLEAN
                )
            ''')

            # Tabela para logs de importação
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS uc (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    survey_id INTEGER NOT NULL,
                    destinacao TEXT,
                    id_complemento3 INTEGER,
                    argumento3 TEXT,
                    id_complemento4 INTEGER,
                    argumento4_logico INTEGER,
                    argumento4_real TEXT,
                    FOREIGN KEY (survey_id) REFERENCES survey(id)
                )
            ''')

            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_roteiro_cep ON roteiros(cep)")

            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        
    # registrar importação
    def registrar_importacao(self, file_type, file_path):
        """Insere ou atualiza registros na tabela import_logs."""
        self.cursor.execute("SELECT COUNT(*) FROM import_logs")
        total_registros = self.cursor.fetchone()[0]

        if total_registros < 2:
            # Inserir se ainda não há registros suficientes
            self.cursor.execute('''
                INSERT INTO import_logs (file_type, file_path, import_date)
                VALUES (?, ?, ?)
            ''', (file_type, file_path, datetime.now().isoformat()))
        else:
            # Atualizar o registro correspondente
            self.cursor.execute('''
                UPDATE import_logs
                SET file_path = ?, import_date = ?
                WHERE file_type = ?
            ''', (file_path, datetime.now().isoformat(), file_type))

        self.conn.commit()

    def obter_importacoes(self):
        """Retorna os registros de importação existentes."""
        self.cursor.execute('''
            SELECT file_type, file_path, import_date
            FROM import_logs
        ''')
        resultados = self.cursor.fetchall()

        # Transforma a lista de tuplas em um dicionário
        importacoes = {row[0]: {"file_path": row[1], "import_date": row[2]} for row in resultados}
        return importacoes
    
    # Implementar metodos para importação de dados
    def _import_caixas_opticas(self, data):
        self.cursor.execute("DELETE FROM caixas_opticas")  # Limpar tabela antes de importar
        self.insert_caixas_opticas(data)

    def _import_complementos(self, data):
        self.cursor.execute("DELETE FROM complementos")  # Limpar tabela antes de importar
        self.insert_complementos(data)

    def _import_empresas(self, data):
        self.cursor.execute("DELETE FROM empresas")  # Limpar tabela antes de importar
        self.insert_empresas(data)

    def _import_operadores(self, data):
        self.cursor.execute("DELETE FROM operadores")  # Limpar tabela antes de importar
        self.insert_operadores(data)

    def _import_roteiros(self, data):
        self.cursor.execute("DELETE FROM roteiros")  # Limpar tabela antes de importar
        self.insert_roteiros(data)

    def _import_tipos_imovel(self, data):
        self.cursor.execute("DELETE FROM tipos_imovel")  # Limpar tabela antes de importar
        self.insert_tipos_imovel(data)

    def _import_zonas(self, data):
        self.cursor.execute("DELETE FROM zonas")  # Limpar tabela antes de importar
        self.insert_zonas(data)
    
    def get_divergence_types(self):
        """Retorna os tipos de divergência entre tabela campo e survey com suas quantidades"""
        self.cursor.execute("""
            SELECT
                COUNT(*) AS total_registros,
                SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) AS registros_ok,
                SUM(CASE WHEN status = 2 THEN 1 ELSE 0 END) AS registros_divergentes,
                SUM(CASE WHEN status = 3 THEN 1 ELSE 0 END) AS nao_encontrado,
                SUM(CASE WHEN lograd_div = 2 THEN 1 ELSE 0 END) AS logradouro_div,
                SUM(CASE WHEN bairro_div = 2 THEN 1 ELSE 0 END) AS bairro_div,
                SUM(CASE WHEN cep_div = 2 THEN 1 ELSE 0 END) AS cep_div
            FROM survey
        """)
        
        result = self.cursor.fetchone()
        
        if result:
            return {
                'total_registros': result[0],
                'registros_ok': result[1],
                'registros_divergentes': result[2],
                'nao_encontrado': result[3],
                'logradouro_div': result[4],
                'bairro_div': result[5],
                'cep_div': result[6]
            }
        return {
            'total_registros': 0,
            'registros_ok': 0,
            'registros_divergentes': 0,
            'nao_encontrado': 0,
            'logradouro_div': 0,
            'bairro_div': 0,
            'cep_div': 0
        }
    
    def get_surveys_by_status(self, status: int) -> List[Dict]:
        """Retorna surveys por status (1=OK, 2=Divergente, 3=Não encontrado)"""
        self.cursor.execute("SELECT * FROM survey WHERE status = ?", (status,))
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def get_divergent_addresses(self, div_type: str) -> List[Dict]:
        """Retorna surveys com um tipo específico de divergência"""
        query = """
            SELECT s.* FROM survey s
            JOIN campo c ON s.logradouro = c.endereco_completo
            WHERE s.status = 2 AND (
        """
        
        conditions = {
            'logradouro': "(c.endereco_completo IS NULL OR TRIM(c.endereco_completo) = '' OR s.logradouro IS NULL OR TRIM(s.logradouro) = '' OR c.endereco_completo != s.logradouro)",
            'bairro': "(c.bairro IS NULL OR TRIM(c.bairro) = '' OR s.bairro IS NULL OR TRIM(s.bairro) = '' OR c.bairro != s.bairro)",
            'cep': "(c.cep IS NULL OR TRIM(c.cep) = '' OR s.cep IS NULL OR TRIM(s.cep) = '' OR c.cep != s.cep)",
            'numero': "(c.numero_fachada IS NULL OR TRIM(c.numero_fachada) = '' OR s.numero_fachada IS NULL OR TRIM(s.numero_fachada) = '' OR c.numero_fachada != s.numero_fachada)"
        }
        
        if div_type not in conditions:
            return []
        
        query += conditions[div_type] + ")"
        
        self.cursor.execute(query)
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def update_address(self, address_id: int, updates: Dict):
        """Atualiza os dados de um endereço no survey"""
        set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values())
        values.append(address_id)
        
        query = f"UPDATE survey SET {set_clause} WHERE id = ?"
        self.cursor.execute(query, values)
        self.conn.commit()
    
    def expand_complemento(self, value):
        if pd.isna(value):
            return None
        try:
            value = str(value)
            
            match = re.match(r'(.*?)(\d+)\s*-\s*(\d+)', value)
            if match:
                base = match.group(1).strip()
                start = int(match.group(2))
                end = int(match.group(3))
                return ', '.join([f"{base} {i}" if i == start else str(i) for i in range(start, end + 1)])
            return value
        except Exception as e:
            print(f"Erro ao processar complemento: {value} -> {e}")
            return value

    def import_excel_data(self, file_path, data):
        try:
            # Limpar tabela antes de importar
            self.cursor.execute("DELETE FROM campo")

            for row in data:
                endereco_completo = str(row.get('endereco', '')) if pd.notna(row.get('endereco')) else None
                bairro = str(row.get('bairro', '')) if pd.notna(row.get('bairro')) else None
                cep = str(row.get('cep', '')) if pd.notna(row.get('cep')) else None
                pais = str(row.get('pais', '')) if pd.notna(row.get('pais')) else None

                complemento = self.expand_complemento(row.get('Weblink: Complemento'))

                self.cursor.execute('''
                    INSERT INTO campo (
                        latitude, longitude, numero_fachada,
                        tipo_imovel, pavimento, endereco_completo, bairro, cep, pais,
                        complemento, quantidade, data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(row.get('Latitude', '')) if pd.notna(row.get('Latitude')) else None,
                    str(row.get('Longitude', '')) if pd.notna(row.get('Longitude')) else None,
                    str(row.get('Nº Fachada', '')) if pd.notna(row.get('Nº Fachada')) else None,
                    str(row.get('MultiChoiceSelection: Tipo HP/Moradia/Comercio/Apartamento', '')) if pd.notna(row.get('MultiChoiceSelection: Tipo HP/Moradia/Comercio/Apartamento')) else None,
                    str(row.get('Weblink: Pavimento', '')) if pd.notna(row.get('Weblink: Pavimento')) else None,
                    endereco_completo,
                    bairro,
                    cep,
                    pais,
                    complemento,
                    str(row.get('Weblink: Quantidade', '')) if pd.notna(row.get('Weblink: Quantidade')) else None,
                    str(row.get('Data', '')) if pd.notna(row.get('Data')) else None,
                ))
            
            # Limpar tabela survey
            self.cursor.execute("DELETE FROM survey")
            
            self.conn.commit()
            return True, f"Importados {len(data)} registros com sucesso"
        
        except Exception as e:
            self.conn.rollback()
            return False, f"Erro na importação: {str(e)}"
        
    def count_total_registros_campo(self):
        """Conta surveys por status"""
        self.cursor.execute("SELECT COUNT(*) FROM campo")
        return self.cursor.fetchone()[0]
        
    def carregar_roteiros_por_cep(self):
        """Carrega todos os roteiros e os organiza por CEP."""
        self.cursor.execute("SELECT * FROM roteiros")
        colunas = [desc[0] for desc in self.cursor.description]
        roteiros = self.cursor.fetchall()
        return {
            (str(r[colunas.index('cep')]).strip() if r[colunas.index('cep')] else ''): dict(zip(colunas, r))
            for r in roteiros
        }
            
    def import_and_validate_surveys(self, progress_callback=None):
        """Importa e valida TODOS os dados de campo para a tabela survey com flags de divergência."""
        try:
            self.conn.execute("BEGIN")  # Transação explícita
            self.cursor.execute("DELETE FROM survey")  # Limpar dados anteriores
            
            # Carregar dados de campo
            self.cursor.execute("SELECT * FROM campo")
            campo_records = self.cursor.fetchall()
            campo_columns = [col[0] for col in self.cursor.description]

            # Carregar roteiros por CEP em memória
            roteiros_por_cep = self.carregar_roteiros_por_cep()

            total_imported = 0

            for record in campo_records:
                campo_data = dict(zip(campo_columns, record))

                # Valores padrões
                lograd_div = 0
                bairro_div = 0
                cep_div = 0
                status = 3

                cep = (campo_data.get('cep') or '').strip()
                roteiro = roteiros_por_cep.get(cep)

                if roteiro:
                    # Validar CEP
                    cep_roteiro = (roteiro.get('cep') or '').strip()
                    if cep and cep_roteiro:
                        cep_div = 1 if cep == cep_roteiro else 2

                    if cep_div == 1:
                        logradouro_campo = self.normalize_text(campo_data.get('endereco_completo', ''))
                        logradouro_roteiro = self.normalize_text(roteiro.get('nome_lograd', ''))
                        if logradouro_campo and logradouro_roteiro:
                            lograd_div = 1 if logradouro_campo == logradouro_roteiro else 2

                        bairro_campo = self.normalize_text(campo_data.get('bairro', ''))
                        bairro_roteiro = self.normalize_text(roteiro.get('bairro', ''))
                        if bairro_campo and bairro_roteiro:
                            bairro_div = 1 if bairro_campo == bairro_roteiro else 2

                        # Definir status
                        if lograd_div == 1 and bairro_div == 1:
                            status = 1
                        else:
                            status = 2
                    else:
                        lograd_div = 0
                        bairro_div = 0

                # Preparar dados para o insert
                survey_data = {
                    'tipo_survey': 1,
                    'coordX': campo_data.get('latitude', ''),
                    'coordY': campo_data.get('longitude', ''),
                    'logradouro': campo_data.get('endereco_completo', ''),
                    'numero_fachada': campo_data.get('numero_fachada', ''),
                    'bairro': campo_data.get('bairro', ''),
                    'cep': campo_data.get('cep', ''),
                    'status': status,
                    'lograd_div': lograd_div,
                    'bairro_div': bairro_div,
                    'cep_div': cep_div,
                    'data': campo_data.get('data', datetime.now().strftime('%Y-%m-%d')),
                    'observacoes': 'Importado automático',
                    'versao': '',
                    'autorizacao': '',
                    'gravado': False,
                    'idCEMobile': 0,
                    'totalUCs': 0,
                    'numPisos': 0,
                    'baixado': False
                }

                if roteiro:
                    survey_data.update({
                        'codigoZona': roteiro.get('codigo', ''),
                        'nomeZona': roteiro.get('nome', ''),
                        'localidade': roteiro.get('localidade', ''),
                        'id_roteiro': roteiro.get('id_roteiro', 0),
                        'id_localidade': roteiro.get('id_localidade', 0),
                        'cod_lograd': roteiro.get('cod_lograd', 0),
                        'cod_bairro': roteiro.get('cod_bairro', 0),
                        'tipo_lograd': roteiro.get('tipo_lograd', '')
                    })

                self.insert_survey(survey_data)
                total_imported += 1

                if progress_callback:
                    progress_callback(total_imported)

            self.conn.commit()
            return True, f"Importados e validados {total_imported} surveys (OK: {self.count_surveys_by_status(1)}, Divergentes: {self.count_surveys_by_status(2)}, Não encontrados: {self.count_surveys_by_status(3)})"
        
        except Exception as e:
            self.conn.rollback()
            return False, f"Erro na importação/validação: {str(e)}"
        
    def count_total_registros_survey(self):
        """Conta surveys por status"""
        self.cursor.execute("SELECT COUNT(*) FROM survey")
        return self.cursor.fetchone()[0]

    def count_surveys_by_status(self, status):
        """Conta surveys por status"""
        self.cursor.execute("SELECT COUNT(*) FROM survey WHERE status = ?", (status,))
        return self.cursor.fetchone()[0]

    def normalize_text(self, text):
        """Normaliza texto para comparação: remove acentos, espaços extras e converte para minúsculas"""
        if not text:
            return ""
        
        import unicodedata
        # Remove acentos
        text = unicodedata.normalize('NFKD', str(text)).encode('ASCII', 'ignore').decode('ASCII')
        # Remove espaços extras, pontuação e converte para minúsculas
        text = ''.join(e for e in text if e.isalnum() or e.isspace())
        return ' '.join(text.strip().lower().split())
    
    # Métodos para caixas ópticas
    def insert_caixas_opticas(self, caixas: List[Dict]):
        """Insere múltiplas caixas ópticas na tabela"""
        for caixa in caixas:
            self.cursor.execute('''
                INSERT INTO caixas_opticas (
                    id_caixa, fabricante, capacidade, designacao, 
                    tipo_caixa, altura, largura, profundidade
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                caixa['id_caixa'], caixa['fabricante'], caixa['capacidade'],
                caixa['designacao'], caixa['tipo_caixa'], caixa.get('altura'),
                caixa.get('largura'), caixa.get('profundidade')
            ))
        self.conn.commit()
    
    def get_caixas_opticas(self) -> List[Dict]:
        """Retorna todas as caixas ópticas"""
        self.cursor.execute("SELECT * FROM caixas_opticas")
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    # Métodos para complementos
    def insert_complementos(self, complementos: List[Dict]):
        """Insere múltiplos complementos na tabela"""
        for comp in complementos:
            self.cursor.execute('''
                INSERT INTO complementos (
                    id_complemento, arg1_obrig, arg2_obrig, arg3_obrig, 
                    arg4_obrig, arg5_obrig, tipo1, tipo2, tipo3, tipo4, 
                    tipo5, abrev, tipo3_principal, tipo_survey_tipo_3, 
                    visibilidade, descricao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                comp['id_complemento'], comp['arg1_obrig'], comp['arg2_obrig'],
                comp['arg3_obrig'], comp['arg4_obrig'], comp['arg5_obrig'],
                comp['tipo1'], comp['tipo2'], comp['tipo3'], comp['tipo4'],
                comp['tipo5'], comp['abrev'], comp['tipo3_principal'],
                comp['tipo_survey_tipo_3'], comp['visibilidade'], comp['descricao']
            ))
        self.conn.commit()
    
    def get_complementos(self) -> List[Dict]:
        """Retorna todos os complementos"""
        self.cursor.execute("SELECT * FROM complementos")
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    # Métodos para empresas e técnicos
    def insert_empresas(self, empresas: List[Dict]):
        """Insere múltiplas empresas e seus técnicos"""
        for emp in empresas:
            # Inserir empresa
            self.cursor.execute('''
                INSERT INTO empresas (id_empresa, nome_empresa)
                VALUES (?, ?)
            ''', (emp['id_empresa'], emp['nome_empresa']))
            
            empresa_id = self.cursor.lastrowid
            
            # Inserir técnicos
            for tec in emp.get('tecnicos', []):
                self.cursor.execute('''
                    INSERT INTO tecnicos (id_empresa, id_tecnico, nome_tecnico)
                    VALUES (?, ?, ?)
                ''', (empresa_id, tec['id_tecnico'], tec['nome_tecnico']))
        
        self.conn.commit()
    
    def get_empresas(self) -> List[Dict]:
        """Retorna todas as empresas com seus técnicos"""
        self.cursor.execute("SELECT id, id_empresa, nome_empresa FROM empresas")
        empresas = []
        for row in self.cursor.fetchall():
            empresa = {
                'id': row[0],
                'id_empresa': row[1],
                'nome_empresa': row[2],
                'tecnicos': []
            }
            
            self.cursor.execute('''
                SELECT id_tecnico, nome_tecnico 
                FROM tecnicos 
                WHERE id_empresa = ?
            ''', (empresa['id'],))
            
            for tec in self.cursor.fetchall():
                empresa['tecnicos'].append({
                    'id_tecnico': tec[0],
                    'nome_tecnico': tec[1]
                })
            
            empresas.append(empresa)
        
        return empresas
    
    # Métodos para operadores
    def insert_operadores(self, operadores: List[Dict]):
        """Insere múltiplos operadores na tabela"""
        for op in operadores:
            self.cursor.execute('''
                INSERT INTO operadores (id_operador, nome_operador)
                VALUES (?, ?)
            ''', (op['id_operador'], op['nome_operador']))
        self.conn.commit()
    
    def get_operadores(self) -> List[Dict]:
        """Retorna todos os operadores"""
        self.cursor.execute("SELECT * FROM operadores")
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    # Métodos para roteiros
    def insert_roteiros(self, roteiros: List[Dict]):
        """Insere múltiplos roteiros na tabela"""
        for rot in roteiros:
            self.cursor.execute('''
                INSERT INTO roteiros (
                    id_roteiro, uf, uf_abrev, cod_municipio, municipio,
                    id_localidade, cod_localidade, localidade, localidade_abrev,
                    cod_bairro, bairro, cod_lograd, nome_lograd, id_tipo_lograd,
                    tipo_lograd, tipo_lograd_abrev, id_titulo, titulo, titulo_abrev, cep
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                rot['id_roteiro'], rot['uf'], rot['uf_abrev'], rot['cod_municipio'],
                rot['municipio'], rot['id_localidade'], rot['cod_localidade'],
                rot['localidade'], rot['localidade_abrev'], rot['cod_bairro'],
                rot['bairro'], rot['cod_lograd'], rot['nome_lograd'],
                rot['id_tipo_lograd'], rot['tipo_lograd'], rot['tipo_lograd_abrev'],
                rot.get('id_titulo'), rot.get('titulo'), rot.get('titulo_abrev'),
                rot['cep']
            ))
        self.conn.commit()
    
    def get_roteiros(self) -> List[Dict]:
        """Retorna todos os roteiros"""
        self.cursor.execute("SELECT * FROM roteiros")
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def get_roteiro_by_cep(self, cep: str) -> Optional[Dict]:
        """Retorna um roteiro pelo CEP"""
        self.cursor.execute('''
            SELECT * FROM roteiros 
            WHERE cep = ?
        ''', (cep,))
        
        result = self.cursor.fetchone()
        if result:
            columns = [col[0] for col in self.cursor.description]
            return dict(zip(columns, result))
        return None
    
    # Métodos para tipos de imóvel
    def insert_tipos_imovel(self, tipos: List[Dict]):
        """Insere múltiplos tipos de imóvel na tabela"""
        for tipo in tipos:
            self.cursor.execute('''
                INSERT INTO tipos_imovel (
                    id_tipo, tipo_imovel, abrev, arg_obrig, visibilidade
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                tipo['id_tipo'], tipo['tipo_imovel'], 
                tipo['abrev'], tipo['arg_obrig'], tipo['visibilidade']
            ))
        self.conn.commit()
    
    def get_tipos_imovel(self) -> List[Dict]:
        """Retorna todos os tipos de imóvel"""
        self.cursor.execute("SELECT * FROM tipos_imovel")
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    # Métodos para zonas
    def insert_zonas(self, zonas: List[Dict]):
        """Insere múltiplas zonas na tabela"""
        for zona in zonas:
            self.cursor.execute('''
                INSERT INTO zonas (codigo, nome)
                VALUES (?, ?)
            ''', (zona['codigo'], zona['nome']))
        self.conn.commit()
    
    def get_zonas(self) -> List[Dict]:
        """Retorna todas as zonas"""
        self.cursor.execute("SELECT * FROM zonas")
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    # Métodos para dados de campo
    def insert_campo_data(self, records: List[Dict]):
        """Insere múltiplos registros de campo na tabela"""
        for rec in records:
            self.cursor.execute('''
                INSERT INTO campo (
                    folder_name, folder_color, latitude, longitude, numero_fachada,
                    description, color, phone_number, timestamp, pin_icon_code,
                    tipo_imovel, pavimento, endereco_completo, complemento,
                    quantidade, junto, data, inicio, termino, hps, postes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                rec.get('folder_name'), rec.get('folder_color'), 
                rec.get('latitude'), rec.get('longitude'),
                rec.get('numero_fachada'), rec.get('description'),
                rec.get('color'), rec.get('phone_number'),
                rec.get('timestamp'), rec.get('pin_icon_code'),
                rec.get('tipo_imovel'), rec.get('pavimento'),
                rec.get('endereco_completo'), rec.get('complemento'),
                rec.get('quantidade'), rec.get('junto'),
                rec.get('data'), rec.get('inicio'),
                rec.get('termino'), rec.get('hps'),
                rec.get('postes')
            ))
        self.conn.commit()

    def insert_survey(self, survey_data: Dict):
        """Insere um registro de survey na tabela"""
        self.cursor.execute('''
            INSERT INTO survey (
                tipo_survey, versao, autorizacao, gravado, idCEMobile,
                coordX, coordY, codigoZona, nomeZona, localidade,
                logradouro, numero_fachada, id_complemento1, argumento1,
                id_complemento3, cep, cod_bairro, bairro, id_roteiro,
                id_localidade, cod_lograd, tecnico_id, tecnico_nome,
                empresa_id, empresa_nome, data, observacoes, totalUCs,
                numPisos, ocupacao, redeInterna, fotoExteriorEdificio,
                fotoFachadaEdificio, status, lograd_div, bairro_div, cep_div, baixado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            survey_data.get('tipo_survey'),
            survey_data.get('versao'),
            survey_data.get('autorizacao'),
            survey_data.get('gravado', False),
            survey_data.get('idCEMobile'),
            survey_data.get('coordX'),
            survey_data.get('coordY'),
            survey_data.get('codigoZona'),
            survey_data.get('nomeZona'),
            survey_data.get('localidade'),
            survey_data.get('logradouro'),
            survey_data.get('numero_fachada'),
            survey_data.get('id_complemento1'),
            survey_data.get('argumento1'),
            survey_data.get('id_complemento3'),
            survey_data.get('cep'),
            survey_data.get('cod_bairro'),
            survey_data.get('bairro'),
            survey_data.get('id_roteiro'),
            survey_data.get('id_localidade'),
            survey_data.get('cod_lograd'),
            survey_data.get('tecnico_id'),
            survey_data.get('tecnico_nome'),
            survey_data.get('empresa_id'),
            survey_data.get('empresa_nome'),
            survey_data.get('data'),
            survey_data.get('observacoes'),
            survey_data.get('totalUCs', 0),
            survey_data.get('numPisos', 0),
            survey_data.get('ocupacao'),
            survey_data.get('redeInterna'),
            survey_data.get('fotoExteriorEdificio'),
            survey_data.get('fotoFachadaEdificio'),
            survey_data.get('status', 3),  # Default: Divergente
            survey_data.get('lograd_div', 0),  # Default: Divergente
            survey_data.get('bairro_div', 0),  # Default: Divergente
            survey_data.get('cep_div', 0),  # Default: Divergente
            survey_data.get('baixado', False)
        ))
        return self.cursor.lastrowid

    def insert_uc(self, survey_id: int, uc_data: Dict):
        """Insere um registro de UC relacionado a um survey"""
        self.cursor.execute('''
            INSERT INTO uc (
                survey_id, destinacao, id_complemento3, argumento3,
                id_complemento4, argumento4_logico, argumento4_real
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            survey_id,
            uc_data.get('destinacao'),
            uc_data.get('id_complemento3'),
            uc_data.get('argumento3'),
            uc_data.get('id_complemento4'),
            uc_data.get('argumento4_logico', 0),
            uc_data.get('argumento4_real')
        ))
        self.conn.commit()

    def get_all_surveys(self) -> List[Dict]:
        """Retorna todos os surveys"""
        self.cursor.execute("SELECT * FROM survey")
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def update_survey_status(self, survey_id: int, status: int):
        """Atualiza o status de um survey"""
        self.cursor.execute('''
            UPDATE survey 
            SET status = ? 
            WHERE id = ?
        ''', (status, survey_id))
        self.conn.commit()
    
    # Métodos para logs de importação
    def get_import_logs(self) -> List[Dict]:
        """Retorna todos os logs de importação"""
        self.cursor.execute("SELECT * FROM import_logs ORDER BY import_date DESC")
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def close(self):
        """Fecha a conexão com o banco de dados"""
        self.conn.close()