from typing import List, Dict, Tuple
from database import Database

class AddressValidator:
    def __init__(self, db: Database):
        self.db = db
    
    def validate_all_addresses(self) -> Dict[str, int]:
        """Valida todos os endereços e retorna estatísticas de divergências"""
        # Obter todos os endereços de campo
        campo_addresses = self.db.get_all_campo_addresses()
        
        # Obter todos os endereços matrix (roteiros)
        matrix_addresses = self.db.get_all_roteiros()
        
        # Inicializar contadores
        stats = {
            'total': len(campo_addresses),
            'ok': 0,
            'divergencias': {
                'logradouro': 0,
                'cep': 0,
                'bairro': 0,
                'numero': 0,
                'nao_matrix': 0,
                'complemento': 0,
                'tipo_imovel': 0
            }
        }
        
        # Validar cada endereço
        for campo_addr in campo_addresses:
            divergences = self._validate_address(campo_addr, matrix_addresses)
            
            if not divergences:
                stats['ok'] += 1
                self.db.update_address_status(campo_addr['id'], 1)  # Status 1 = OK
            else:
                self.db.update_address_status(campo_addr['id'], 2, ', '.join(divergences))  # Status 2 = Divergente
                for div in divergences:
                    stats['divergencias'][div] += 1
        
        return stats
    
    def _validate_address(self, campo_addr: Dict, matrix_addresses: List[Dict]) -> List[str]:
        """Valida um endereço específico e retorna lista de divergências"""
        divergences = []
        
        # Extrair informações do endereço de campo
        campo_endereco = campo_addr.get('endereco_completo', '')
        campo_numero = campo_addr.get('numero_fachada', '')
        campo_bairro = campo_addr.get('description', '').split(' - ')[-1] if campo_addr.get('description') else ''
        
        # Tentar encontrar correspondência na matrix
        matched = False
        for matrix_addr in matrix_addresses:
            # Verificar correspondência básica
            if (matrix_addr['nome_lograd'].lower() in campo_endereco.lower() and
                matrix_addr['bairro'].lower() in campo_bairro.lower()):
                
                matched = True
                
                # Verificar divergências específicas
                if matrix_addr['nome_lograd'].lower() != campo_endereco.split(',')[0].strip().lower():
                    divergences.append('logradouro')
                
                if matrix_addr['bairro'].lower() != campo_bairro.lower():
                    divergences.append('bairro')
                
                if campo_numero and not self._validate_number(campo_numero, matrix_addr['nome_lograd']):
                    divergences.append('numero')
                
                if campo_addr.get('cep') and matrix_addr['cep'] != campo_addr['cep']:
                    divergences.append('cep')
                
                break
        
        if not matched:
            divergences.append('nao_matrix')
        
        # Validar tipo de imóvel
        if campo_addr.get('tipo_imovel') and not self._validate_tipo_imovel(campo_addr['tipo_imovel']):
            divergences.append('tipo_imovel')
        
        # Validar complemento
        if campo_addr.get('complemento') and not self._validate_complemento(campo_addr['complemento']):
            divergences.append('complemento')
        
        return divergences
    
    def _validate_number(self, number: str, logradouro: str) -> bool:
        """Valida se o número da fachada é válido para o logradouro"""
        # Implementação básica - pode ser aprimorada
        return number.isdigit()
    
    def _validate_tipo_imovel(self, tipo: str) -> bool:
        """Valida se o tipo de imóvel existe na matrix"""
        tipos = self.db.get_tipos_imovel()
        return any(t['tipo_imovel'].lower() == tipo.lower() for t in tipos)
    
    def _validate_complemento(self, complemento: str) -> bool:
        """Valida se o complemento existe na matrix"""
        complementos = self.db.get_complementos()
        return any(c['descricao'].lower() == complemento.lower() for c in complementos)