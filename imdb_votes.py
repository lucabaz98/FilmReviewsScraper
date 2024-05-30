import requests
import re
import sys

class IMDb:
    def __init__(self, api_key, title, year):
        self.api_key = api_key
        self.title = re.sub(r'[^A-Za-z0-9\s]', ' ', title)
        self.year = year
        
    def _make_request(self):
        url = "https://www.omdbapi.com/"
        params = {
            'apikey': self.api_key,
            't': self.title,
            'type': 'movie',
            'y': self.year,
            'plot': 'short'
        }
        response = requests.get(url, params=params)
        return response
    
    def _parse_response(self, data, film):
        film['review']['IMDb'] = {}
        if data.get('imdbRating') != 'N/A':
            film['review']['IMDb']['rating'] = float(data.get('imdbRating'))
        if data.get('imdbVotes') != 'N/A':
            film['review']['IMDb']['quantity'] = int(data.get('imdbVotes').replace(',', ''))
        if data.get('imdbID') != '':
            film['review']['IMDb']['url_review'] = f"https://www.imdb.com/title/{data.get('imdbID')}"
        
        

    def fetch_data(self, film):
        response = self._make_request()
        if response.status_code == 200:
            data = response.json()
            if data.get('Response') != 'False':
                self._parse_response(data, film)   
            else:
                print(f"IMDB: {self.title} {data.get('Error')}")
        else:
            if response.status_code == 401:
                print("API Key is invalid")
                print("Exiting...")
                print("Please provide a valid API Key")
                sys.exit(1)
            else:
                print(f"IMDB: Error: {response.status_code}")
        return film

# if __name__ == "__main__":
#     tit = "The Transporter"
#     #tit = "Borat - Studio culturale sull'America a beneficio della gloriosa nazione del Kazakistan"
#     film = {
#         'title': tit,
#         'year': 2009,
#         'review': {}
#     }
#     film = IMDb(api_key="6b18b613", title = film.get('title'), year = film.get('year')).fetch_data(film)
#     print(film)