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
                'nao_encontrado': divergencias['nao_encontrado']
            }
        }
    
    def validate_survey(self, campo_data: Dict, survey_data: Dict) -> List[str]:
        """Valida um registro específico comparando campo vs survey"""
        divergences = []
        
        # Validação de logradouro
        campo_logradouro = str(campo_data.get('endereco_completo', '')).strip()
        survey_logradouro = str(survey_data.get('logradouro', '')).strip()
        if not campo_logradouro or not survey_logradouro or campo_logradouro != survey_logradouro:
            divergences.append('logradouro')
        
        # Validação de bairro
        campo_bairro = str(campo_data.get('bairro', '')).strip()
        survey_bairro = str(survey_data.get('bairro', '')).strip()
        if not campo_bairro or not survey_bairro or campo_bairro != survey_bairro:
            divergences.append('bairro')
        
        # Validação de CEP
        campo_cep = str(campo_data.get('cep', '')).strip()
        survey_cep = str(survey_data.get('cep', '')).strip()
        if not campo_cep or not survey_cep or campo_cep != survey_cep:
            divergences.append('cep')
        
        return divergences