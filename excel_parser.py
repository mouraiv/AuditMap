import pandas as pd
from typing import List, Dict

class ExcelParser:
    @staticmethod
    def parse_campo_map_maker(file_path: str) -> List[Dict]:
        """Parse campo_Map_Maker.xlsx file"""
        try:
            # Ler o arquivo Excel
            df = pd.read_excel(file_path)
            
            # Renomear colunas para padrão SQLite
            df.columns = df.columns.str.replace(' ', '_').str.replace('Ã§', 'c').str.replace('Ã£', 'a').str.replace('Ã¡', 'a')
            
            # Converter para lista de dicionários
            records = df.to_dict('records')
            
            # Ajustar nomes de campos específicos
            for record in records:
                if 'MultiChoiceSelection:_Tipo_HP/Moradia/Comercio/Apartamento' in record:
                    record['tipo_imovel'] = record.pop('MultiChoiceSelection:_Tipo_HP/Moradia/Comercio/Apartamento')
                if 'Weblink:_Pavimento' in record:
                    record['pavimento'] = record.pop('Weblink:_Pavimento')
                if 'Weblink:_Endereco_completo' in record:
                    record['endereco_completo'] = record.pop('Weblink:_Endereco_completo')
                if 'Weblink:_Complemento' in record:
                    record['complemento'] = record.pop('Weblink:_Complemento')
                if 'Weblink:_Quantidade' in record:
                    record['quantidade'] = record.pop('Weblink:_Quantidade')
                if 'Nº_Fachada' in record:
                    record['numero_fachada'] = record.pop('Nº_Fachada')
            
            return records
        except Exception as e:
            raise Exception(f"Erro ao processar arquivo Excel: {str(e)}")