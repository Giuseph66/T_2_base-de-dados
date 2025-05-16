import requests

class climinha:
    def __init__(self, longitude, latitude):
        self.longitude = longitude
        self.latitude = latitude
    def get_clima(self):
        url = f"https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current_weather": True
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  
            dados = response.json()
            return dados
        except requests.exceptions.RequestException as e:
            print(f"Erro ao obter dados climáticos: {e}")
            return None
        
if __name__ == "__main__":
    latitude = -23.5505
    longitude = -46.6333

    clima = climinha(longitude, latitude)
    dados_climaticos = clima.get_clima()
    if dados_climaticos:
        print("Dados climáticos atuais:")
        print(f"Temperatura: {dados_climaticos['current_weather']['temperature']}°C")
        print(f"Velocidade do vento: {dados_climaticos['current_weather']['windspeed']} km/h")
        print(f"Direção do vento: {dados_climaticos['current_weather']['winddirection']}°")