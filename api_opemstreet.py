import requests

def buscar_endereco_por_coordenadas(lat, lon):
    """
    Faz uma requisição à API Nominatim do OpenStreetMap e retorna dados do endereço a partir da latitude e longitude.
    """
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        'lat': lat,
        'lon': lon,
        'format': 'json',
        'addressdetails': 1,
        'accept-language': 'pt-BR'
    }

    headers = {
        'User-Agent': 'PythonReverseGeocoder/1.0 (seu-email@dominio.com)'
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        endereco = data.get('address', {})
        
        return {
            'cep': endereco.get('postcode'),
            'logradouro': endereco.get('road') or endereco.get('residential') or endereco.get('pedestrian'),
            'bairro': endereco.get('suburb') or endereco.get('neighbourhood'),
            'municipio': endereco.get('city') or endereco.get('town') or endereco.get('village'),
            'localidade': endereco.get('state'),
            'uf': endereco.get('state')
        }
    else:
        raise Exception(f"Erro ao consultar coordenadas: {response.status_code} - {response.text}")
