from my_movies import MyMovies
from coming_soon import ComingSoon
from imdb import IMDb
import argparse
from tqdm import tqdm
import utils


# Process film information using MyMovies, ComingSoon, and IMDb scrapers.
def process_film(film, country, season):
    film = MyMovies(country, season).get_film_informations(film)
    film = ComingSoon().get_film_informations(film)
    film = IMDb().get_film_informations(film)
    return film


# Scrape data for a specific season and store it in the collection.
def scrape_season(country, season, collection, url_base):
    print(f"Scraping {season}...")

    rows, indices = utils.create_ordered_box_office(url=f"{url_base}/{country}/{season}/")

    for i in tqdm(indices, desc=f"Processing films for {season} in {country}"):
        try:
            film = process_film(rows[i], country, season)
            collection.insert_one(film)
        except Exception as e:
            print(f"Error processing film at index {i}: {e}")

    print(f"Scraping {season} completed.")


# Scrape film data for the given country and seasons, and store it in the database.

def scrape_country_seasons(country, seasons):
    configs = utils.get_configs()
    collection = utils.initialize_database(configs['MONGODB_COLLECTION_NAME'])

    for season in seasons:
        scrape_season(country, season, collection, configs['URL_MYMOVIES_BOXOFFICE'])


# Main function to parse arguments and initiate scraping.

def main():
    parser = argparse.ArgumentParser(description="Scrape box office data and save to MongoDB.")
    parser.add_argument("country", type=str, default="usa", help="Country code for the box office data.")
    parser.add_argument("seasons", type=int, nargs='+', default=[2023], help="Seasons to scrape data for.")
    args = parser.parse_args()
    scrape_country_seasons(args.country, args.seasons)


if __name__ == "__main__":
    main()
