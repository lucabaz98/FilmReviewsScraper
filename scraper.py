from pymongo import MongoClient, errors
import importlib
import box_office_scraper
import coming_soon_votes
from imdb_votes import IMDb
import argparse
from tqdm import tqdm
# import subprocess

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


def scrape(country, seasons, collection):
    unique_titles = set()
    collection.create_index([('title', 1)], unique=True)
    for season in seasons:
        print(f"Scraping {season}...")
        url = f"https://www.mymovies.it/boxoffice/{country}/{season}/"
    
        soup = box_office_scraper.get_soup(url)
        rows = soup.find_all('tr', attrs={'valign': 'top'})
        number_of_films = len(rows)
        indices = create_ordered_box_office(number_of_films)
        
        for i in tqdm(indices, desc=f"Processing films for {season} in {country}"):
            film = box_office_scraper.film_informations(rows[i], country, season)
            
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
        print(f"Scraping {season} completed.")        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape box office data and save to MongoDB.")
    parser.add_argument("--countries", type=str, nargs='+', required=True, default=["usa"], help="List of countries for box office data. usa or ita")
    parser.add_argument("--seasons", type=int, nargs='+', required=True, default=[2023], help="List of seasons (years) to scrape data for. >200")

    args = parser.parse_args()
    
    collection = db_connection()
    
    for country in args.countries:
        print(f"Scraping box office data for {country}...")
        scrape(country, args.seasons, collection)
        print(f"Scraping box office data for {country} completed.")
    
    print("Scraping completed.")
    
    # seasons = list(range(2021, 2024))
    # countries = ["usa"]
    # for country in countries:
    #     box_office_scraper = scrape(country, seasons, db_connection())
        
    # sleep_command = 'osascript -e "tell application \\"System Events\\" to sleep"'
    # subprocess.run(sleep_command, shell=True)