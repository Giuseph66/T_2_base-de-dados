import requests

class IndiceKP:
    def __init__(self):
        self.data = None
    def get_data(self):
        if self.data is None:
            response = requests.get("https://services.swpc.noaa.gov/json/planetary_k_index_1m.json")
            if response.status_code == 200:
                self.data = response.json()
            else:
                print(f"Error: {response.text}")
                raise Exception(f"Failed to fetch data: {response.status_code}")
        return self.data
    