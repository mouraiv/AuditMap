import xml.etree.ElementTree as ET
from typing import List, Dict

class XMLParser:
    @staticmethod
    def parse_caixas_opticas(file_path: str) -> List[Dict]:
        """Parse caixasopticas.xml file"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        caixas = []
        for cop in root.findall('cop'):
            caixa = {
                'id_caixa': int(cop.find('idCaixa').text),
                'fabricante': cop.find('fabricante').text,
                'capacidade': int(cop.find('capacidade').text),
                'designacao': cop.find('designacao').text,
                'tipo_caixa': cop.find('tipoCaixa').text,
                'altura': int(cop.find('altura').text) if cop.find('altura') is not None else None,
                'largura': int(cop.find('largura').text) if cop.find('largura') is not None else None,
                'profundidade': int(cop.find('profundidade').text) if cop.find('profundidade') is not None else None
            }
            caixas.append(caixa)
        
        return caixas

    @staticmethod
    def parse_complementos(file_path: str) -> List[Dict]:
        """Parse complementos.xml file"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        complementos = []
        for comp in root.findall('complemento'):
            complemento = {
                'id_complemento': int(comp.get('id')),
                'arg1_obrig': comp.get('arg1_obrig'),
                'arg2_obrig': comp.get('arg2_obrig'),
                'arg3_obrig': comp.get('arg3_obrig'),
                'arg4_obrig': comp.get('arg4_obrig'),
                'arg5_obrig': comp.get('arg5_obrig'),
                'tipo1': comp.get('tipo1'),
                'tipo2': comp.get('tipo2'),
                'tipo3': comp.get('tipo3'),
                'tipo4': comp.get('tipo4'),
                'tipo5': comp.get('tipo5'),
                'abrev': comp.get('abrev'),
                'tipo3_principal': comp.get('tipo3_principal'),
                'tipo_survey_tipo_3': comp.get('tipo_survey_tipo_3'),
                'visibilidade': comp.get('visibilidade'),
                'descricao': comp.text.strip() if comp.text else None
            }
            complementos.append(complemento)
        
        return complementos

    @staticmethod
    def parse_empresas(file_path: str) -> List[Dict]:
        """Parse empresas.xml file"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        empresas = []
        for empresa in root.findall('empresa'):
            emp = {
                'id_empresa': int(empresa.find('idEmpresa').text),
                'nome_empresa': empresa.find('nomeEmpresa').text,
                'tecnicos': []
            }
            
            tecnicos = empresa.find('tecnicos')
            if tecnicos is not None:
                for tecnico in tecnicos.findall('tecnico'):
                    t = {
                        'id_tecnico': int(tecnico.find('idTecnico').text),
                        'nome_tecnico': tecnico.find('nomeTecnico').text
                    }
                    emp['tecnicos'].append(t)
            
            empresas.append(emp)
        
        return empresas

    @staticmethod
    def parse_operadores(file_path: str) -> List[Dict]:
        """Parse operadores.xml file"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        operadores = []
        for operador in root.findall('operador'):
            op = {
                'id_operador': int(operador.get('id')) if operador.get('id').isdigit() else operador.get('id'),
                'nome_operador': operador.text
            }
            operadores.append(op)
        
        return operadores

    @staticmethod
    def parse_roteiros(file_path: str) -> List[Dict]:
        """Parse roteiro.xml file com tratamento de campos nulos"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        roteiros = []
        for roteiro in root.findall('roteiro'):
            # Função auxiliar para tratar conversão de inteiros
            def get_int(element, tag):
                elem = element.find(tag)
                return int(elem.text) if elem is not None and elem.text and elem.text.strip() else None
            
            # Função auxiliar para tratar textos
            def get_text(element, tag):
                elem = element.find(tag)
                return elem.text if elem is not None else None
            
            rot = {
                'id_roteiro': get_int(roteiro, 'id'),
                'uf': get_text(roteiro, 'uf'),
                'uf_abrev': get_text(roteiro, 'uf_abrev'),
                'cod_municipio': get_int(roteiro, 'cod_municipio'),
                'municipio': get_text(roteiro, 'municipio'),
                'id_localidade': get_int(roteiro, 'id_localidade'),
                'cod_localidade': get_int(roteiro, 'cod_localidade'),
                'localidade': get_text(roteiro, 'localidade'),
                'localidade_abrev': get_text(roteiro, 'localidade_abrev'),
                'cod_bairro': get_int(roteiro, 'cod_bairro'),
                'bairro': get_text(roteiro, 'bairro'),
                'cod_lograd': get_int(roteiro, 'cod_lograd'),
                'nome_lograd': get_text(roteiro, 'nome_lograd'),
                'id_tipo_lograd': get_int(roteiro, 'id_tipo_lograd'),
                'tipo_lograd': get_text(roteiro, 'tipo_lograd'),
                'tipo_lograd_abrev': get_text(roteiro, 'tipo_lograd_abrev'),
                'id_titulo': get_int(roteiro, 'id_titulo'),
                'titulo': get_text(roteiro, 'titulo'),
                'titulo_abrev': get_text(roteiro, 'titulo_abrev'),
                'cep': get_text(roteiro, 'cep')
            }
            roteiros.append(rot)
        
        return roteiros

    @staticmethod
    def parse_tipos_imovel(file_path: str) -> List[Dict]:
        """Parse tipos_imovel.xml file"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        tipos = []
        for tipo in root.findall('Tipo_de_Imovel'):
            t = {
                'id_tipo': int(tipo.get('id')),
                'tipo_imovel': tipo.get('tipo_imovel'),
                'abrev': tipo.get('abrev'),
                'arg_obrig': tipo.get('arg_obrig'),
                'visibilidade': tipo.get('visibilidade')
            }
            tipos.append(t)
        
        return tipos

    @staticmethod
    def parse_zonas(file_path: str) -> List[Dict]:
        """Parse zonas.xml file"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        zonas = []
        for zona in root.findall('zona'):
            z = {
                'codigo': zona.get('codigo'),
                'nome': zona.get('nome')
            }
            zonas.append(z)
        
        return zonas