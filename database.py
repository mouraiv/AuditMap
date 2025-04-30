import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
class Database:
    def __init__(self, db_name="auditmap.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
    
    def initialize_db(self):
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
                folder_name TEXT,
                folder_color TEXT,
                latitude REAL,
                longitude REAL,
                numero_fachada TEXT,
                description TEXT,
                color TEXT,
                phone_number TEXT,
                timestamp TEXT,
                pin_icon_code TEXT,
                tipo_imovel TEXT,
                pavimento TEXT,
                endereco_completo TEXT,
                complemento TEXT,
                quantidade TEXT,
                junto TEXT,
                data TEXT,
                inicio TEXT,
                termino TEXT,
                hps TEXT,
                postes TEXT,
                status INTEGER DEFAULT 2,  -- 1=OK, 2=Divergente, 3=Baixado
                divergencias TEXT
            )
        ''')
        
        # Tabela para logs de importação
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS import_logs (
                id INTEGER PRIMARY KEY,
                file_type TEXT,
                file_path TEXT,
                import_date TEXT,
                records_imported INTEGER
            )
        ''')
        
        self.conn.commit()
    
    def import_xml_data(self, file_type, file_path, data):
        try:
            if file_type == "caixas_opticas":
                self._import_caixas_opticas(data)
            elif file_type == "complementos":
                self._import_complementos(data)
            elif file_type == "empresas":
                self._import_empresas(data)
            elif file_type == "operadores":
                self._import_operadores(data)
            elif file_type == "roteiros":
                self._import_roteiros(data)
            elif file_type == "tipos_imovel":
                self._import_tipos_imovel(data)
            elif file_type == "zonas":
                self._import_zonas(data)
            
            # Registrar a importação
            self.cursor.execute('''
                INSERT INTO import_logs (file_type, file_path, import_date, records_imported)
                VALUES (?, ?, ?, ?)
            ''', (file_type, file_path, datetime.now().isoformat(), len(data)))
            
            self.conn.commit()
            return True, f"Importação de {len(data)} registros concluída com sucesso."
        except Exception as e:
            self.conn.rollback()
            return False, f"Erro na importação: {str(e)}"
    
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
    
    # Implementar outros métodos _import_* para cada tipo de dados
    
    def import_excel_data(self, file_path, data):
        try:
            # Limpar tabela antes de importar novos dados
            self.cursor.execute("DELETE FROM campo")
            
            # Inserir novos dados
            for row in data:
                self.cursor.execute('''
                    INSERT INTO campo (
                        folder_name, folder_color, latitude, longitude, numero_fachada,
                        description, color, phone_number, timestamp, pin_icon_code,
                        tipo_imovel, pavimento, endereco_completo, complemento,
                        quantidade, junto, data, inicio, termino, hps, postes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('Folder name'), row.get('Folder color'), row.get('Latitude'),
                    row.get('Longitude'), row.get('Nº Fachada'), row.get('Description'),
                    row.get('Color'), row.get('Phone number'), row.get('Timestamp'),
                    row.get('Pin icon code'), row.get('MultiChoiceSelection: Tipo HP/Moradia/Comercio/Apartamento'),
                    row.get('Weblink: Pavimento'), row.get('Weblink: Endereço completo'),
                    row.get('Weblink: Complemento'), row.get('Weblink: Quantidade'),
                    row.get('junto?'), row.get('Data'), row.get('inicio'), row.get('termino'),
                    row.get('hps'), row.get('Postes')
                ))
            
            # Registrar a importação
            self.cursor.execute('''
                INSERT INTO import_logs (file_type, file_path, import_date, records_imported)
                VALUES (?, ?, ?, ?)
            ''', ('campo', file_path, datetime.now().isoformat(), len(data)))
            
            self.conn.commit()
            return True, f"Importação de {len(data)} registros de campo concluída com sucesso."
        except Exception as e:
            self.conn.rollback()
            return False, f"Erro na importação: {str(e)}"
    
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
                    quantidade, junto, data, inicio, termino, hps, postes, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                rec.get('postes'), 2  # Status padrão: Divergente
            ))
        self.conn.commit()
    
    def get_all_campo_addresses(self) -> List[Dict]:
        """Retorna todos os endereços de campo"""
        self.cursor.execute("SELECT * FROM campo")
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def get_campo_addresses_by_status(self, status: int) -> List[Dict]:
        """Retorna endereços de campo por status"""
        self.cursor.execute('''
            SELECT * FROM campo 
            WHERE status = ?
        ''', (status,))
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def get_divergent_addresses(self, divergence_type: str = None) -> List[Dict]:
        """Retorna endereços divergentes, opcionalmente filtrando por tipo de divergência"""
        query = "SELECT * FROM campo WHERE status = 2"
        params = []
        
        if divergence_type:
            query += " AND divergencias LIKE ?"
            params.append(f'%{divergence_type}%')
        
        self.cursor.execute(query, params)
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def update_address_status(self, address_id: int, status: int, divergences: str = None):
        """Atualiza o status de um endereço"""
        if divergences is not None:
            self.cursor.execute('''
                UPDATE campo 
                SET status = ?, divergencias = ? 
                WHERE id = ?
            ''', (status, divergences, address_id))
        else:
            self.cursor.execute('''
                UPDATE campo 
                SET status = ? 
                WHERE id = ?
            ''', (status, address_id))
        self.conn.commit()
    
    def update_address(self, address_id: int, updates: Dict):
        """Atualiza os dados de um endereço"""
        set_clause = ', '.join(f"{key} = ?" for key in updates.keys())
        values = list(updates.values())
        values.append(address_id)
        
        self.cursor.execute(f'''
            UPDATE campo 
            SET {set_clause} 
            WHERE id = ?
        ''', values)
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