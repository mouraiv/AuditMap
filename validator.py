from typing import List, Dict
from database import Database

class AddressValidator:
    def __init__(self, db: Database):
        self.db = db
    
    def validate_all_surveys(self) -> Dict[str, int]:
        """Valida todos os surveys e retorna estatísticas consolidadas"""
        divergencias = self.db.get_divergence_types()
        
        return {
            'total': divergencias['total_registros'],
            'ok': divergencias['registros_ok'],
            'divergencias': {
                'logradouro': divergencias['logradouro_div'],
                'bairro': divergencias['bairro_div'],
                'logradouro_bairro': divergencias['logradouro_bairro_div'],
                'cep': divergencias['cep_div'],
                'cep_dup': divergencias['cep_dup'],
                'nao_encontrado': divergencias['nao_encontrado'],
                'nao_encontrado_cep_dup': divergencias['nao_encontrado_cep_dup']
            }
        }
    