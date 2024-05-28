from pymongo import MongoClient, errors
import importlib
import box_office_scraper
import coming_soon_votes
from imdb_votes import IMDb

def db_connection():
    client = MongoClient("localhost", 27017)
    db = client["db_Films"]
    collection = db["Film"]
    return collection

# Ordered rank list
def create_ordered_box_office(n):
    first_half = list(range(n // 2))
    second_half = list(range(n // 2, n))
    interleaved_list = []
    for i in range(n // 2):
        interleaved_list.append(first_half[i])
        interleaved_list.append(second_half[i])
    return interleaved_list


def scrape(country, seasons, indices, collection):
    unique_titles = set()
    collection.create_index([('title', 1)], unique=True)
    for season in seasons:
        print(f"Scraping {season}...")
        soup = box_office_scraper.get_soup(f"https://www.mymovies.it/boxoffice/{country}/{season}/")
        rows = soup.find_all('tr', attrs={'valign': 'top'})
        
        for i in indices:
            film = box_office_scraper.film_informations(rows[i], country, season)
            print(i, film['title'])
            if film['title'] not in unique_titles:
                unique_titles.add(film['title'])
    
                if film.get('original_title'):
                    film = coming_soon_votes.coming_soon_informations(film, film.get('original_title'))
                    film = IMDb(api_key="6b18b613", title = film.get('original_title'), year = film.get('year')).fetch_data(film)
                else:
                    film = coming_soon_votes.coming_soon_informations(film, film.get('title'))
                    film = IMDb(api_key="6b18b613", title = film.get('title'), year = film.get('year')).fetch_data(film)
                    
                try:
                    collection.insert_one(film)
                except errors.DuplicateKeyError:
                    print(f"Duplicate film found: {film['title']}. Skipping insertion.")
            else:   
                print(f"Duplicate film found: {film['title']}. Skipping insertion. {season}")
                



if __name__ == "__main__":
    number_of_films = 100
    rank_list = create_ordered_box_office(number_of_films) 
    seasons = list(range(2004, 2010))
    countries = ["usa"]
    for country in countries:
        box_office_scraper = scrape(country, seasons, rank_list, db_connection())