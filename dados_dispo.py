import requests

class dispositivo:
    def get_dados(self):
        try:
            response = requests.get("https://ipinfo.io/json")
            if response.status_code == 200:
                dados = response.json()
                
                if 'loc' in dados:
                    latitude, longitude = dados['loc'].split(',')
                    dados['latitude'] = latitude
                    dados['longitude'] = longitude
                    del dados['loc'] 
                
                return dados
            else:
                print(f"Error: {response.text}")
                raise Exception(f"Failed to fetch data: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            raise
