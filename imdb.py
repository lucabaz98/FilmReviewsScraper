import requests
import re
import sys
from utils import get_configs


class IMDb:
    def __init__(self, config_path='configs.yaml'):
        self.config = get_configs(config_path)
        self.api_key = self.config['IMDB_API_KEY']
        # self.title = title  #re.sub(r'[^A-Za-z0-9\s]', ' ', title)
        # self.year = year

    # Make a request to the IMDb API
    def _make_request(self, title, year):
        url = "https://www.omdbapi.com/"
        params = {
            'apikey': self.api_key,
            't': title,
            'type': 'movie',
            'y': year,
            'plot': 'short'
        }
        return requests.get(url, params=params)

    # Parse the IMDb API response and update the film dictionary
    def _parse_response(self, data, film):
        film['review']['IMDb'] = {}
        if data.get('imdbRating') != 'N/A':
            film['review']['IMDb']['rating'] = float(data.get('imdbRating'))
        if data.get('imdbVotes') != 'N/A':
            film['review']['IMDb']['quantity'] = int(data.get('imdbVotes').replace(',', ''))
        if data.get('imdbID') != '':
            film['review']['IMDb']['url_review'] = f"https://www.imdb.com/title/{data.get('imdbID')}"

    # Fetch and update film data with IMDb information
    def __fetch_data(self, film, title):
        response = self._make_request(title, film.get('year'))
        if response.status_code == 200:
            data = response.json()
            if data.get('Response') != 'False':
                self._parse_response(data, film)
            # else:
            #     print(f"IMDB: {title} {data.get('Error')}")
        else:
            if response.status_code == 401:
                print("API Key is invalid. Exiting...")
                print("Please provide a valid API Key")
                sys.exit(1)
            # else:
            #     print(f"IMDB: Error: {response.status_code}")
        return film

    def get_film_informations(self, film):
        title = film.get('original_title') or film.get('title')
        if title:
            # Try the original title first
            film = self.__fetch_data(film, title)
            if 'IMDb' not in film['review']:
                # If the original title search yields no results, remove special characters and try again
                title = re.sub(r'[^A-Za-z0-9\s]', ' ', title)
                film = self.__fetch_data(film, title)

                if 'IMDb' not in film['review']:
                    # If the original title search yields no results, try the regular title
                    title = film.get('title')
                    film = self.__fetch_data(film, title)
                    if 'IMDb' not in film['review']:
                        # If the regular title search yields no results, remove special characters and try again
                        title = re.sub(r'[^A-Za-z0-9\s]', ' ', title)
                        film = self.__fetch_data(film, title)

        return film
