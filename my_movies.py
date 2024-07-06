import re
import utils


class MyMovies:
    def __init__(self, country, season, config_path='configs.yaml'):
        self.configs = utils.get_configs(config_path)
        self.headers = {'User-Agent': self.configs['USER_AGENT']}
        self.country = country
        self.season = season


    def __get_rank(self, row):
        return int(row.find('strong').text.strip())

    def __get_url_review(self, row):
        return row.find('a').get('href')

    def __get_title(self, row):
        return row.find('a').text.strip()

    def __get_original_title(self, row):
        return row.find_all('strong')[1].find_previous_sibling('br').previous_sibling.strip().replace('(', '').replace(
            ')',
            '')

    def __get_register(self, row):
        return row.find_all('strong')[1].text.strip().replace(', ', ',').split(',')

    def __get_revenue(self, row):
        return row.find_all('strong')[2].text.strip().split()[-1]

    def __get_genre_from_row(self, genere_region_year):
        return genere_region_year.split(' - ')[0]

    def __get_region_from_row(self, genere_region_year):
        return genere_region_year.split(' - ')[1].split(', ')[:-1]

    def __get_year_from_row(self, genere_region_year):
        return genere_region_year.split(' - ')[1].split(', ')[-1]

    def __get_genre_region_year(self, row):
        return row.find_all('strong')[2].find_previous_sibling('br').previous_sibling.strip()

    def __get_rating_quantity(self, url_review):
        soup = utils.get_soup(url_review)
        try:
            target_div = soup.find("div", class_="display-dettagli-cast")
            critica_td = target_div.find("a", string=lambda text: "critica" in text if text else False)
            rating = float(critica_td.previous_sibling.previous_sibling.get_text().replace(',', '.'))
            quantity = int(re.search(r'\d+', critica_td.previous_sibling.get_text()).group())
        except:
            rating = None
            quantity = None
        return rating, quantity

    def get_film_informations(self, row):
        film = {}

        title = self.__get_title(row)
        if title != "":
            film['title'] = title

        original_title = self.__get_original_title(row)
        if original_title != "":
            film['original_title'] = original_title

        register = self.__get_register(row)
        if all(item != '' for item in register):
            if len(register) == 1:
                register = register[0]
            film['register'] = register

        genere_region_year = self.__get_genre_region_year(row)

        genere = self.__get_genre_from_row(genere_region_year)
        if genere != "":
            film['genere'] = genere

        region = self.__get_region_from_row(genere_region_year)

        if all(item != '' for item in region):
            if len(region) == 1:
                region = region[0]
            film['region'] = region

        year = self.__get_year_from_row(genere_region_year)
        if year != "":
            film['year'] = int(year)

        film['box_office'] = {}
        film['box_office'][self.country] = {}

        rank = self.__get_rank(row)
        if rank != "":
            film['box_office'][self.country]['rank'] = rank

        revenue = self.__get_revenue(row)
        if revenue != "":
            film['box_office'][self.country]['revenue'] = int(revenue.replace(".", ""))

        film['box_office'][self.country]['season'] = self.season

        film['review'] = {}
        film['review']['MyMovies'] = {}
        url_review = self.__get_url_review(row)

        if url_review != "":
            film['review']['MyMovies']['url_review'] = url_review

        rating, quantity = self.__get_rating_quantity(url_review)
        if rating is not None:
            film['review']['MyMovies']['rating'] = rating
        if quantity is not None:
            film['review']['MyMovies']['quantity'] = quantity

        return film
