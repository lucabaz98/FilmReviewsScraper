import time
import random
import utils
import re
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class ComingSoon:
    def __init__(self, config_path='configs.yaml'):
        self.configs = utils.get_configs(config_path)
        self.headers = {'User-Agent': self.configs['USER_AGENT']}

    def __get_film_informations_by_scraping(self, title):
        title_unicode = re.sub(r'[^A-Za-z0-9\s]', ' ', title)
        time.sleep(random.uniform(1, 3))
        query = f"{title_unicode} comingsoon"  #  film {film['register']} {film['year']}
        url = f"https://www.google.com/search?q={query}"

        return utils.get_soup(url)

    def __get_url_review(self, soup):
        url_review = None
        try:
            url_review = soup.find('a', href=lambda href: href and href.startswith('https://www.comingsoon.it/film'))
            url_review = url_review['href']
        finally:
            return url_review

    def __get_rating_quantity(self, soup):
        try:
            span = soup.find('span', string=lambda text: text and "Valutazione" in text)
            rating = float(span.text.strip().replace("Valutazione: ", "").replace(',', '.'))
        except:
            rating = None
        try:
            quantity = int(span.find_next_sibling('span').text.strip().replace(" voti", "").replace(".", ""))
        except:
            quantity = None
        return rating, quantity

    # Extracts the vote data from the film page.
    def __extract_vote_data(self, wait):
        rating, quantity = None, None
        try:
            vote_text = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='mrl']/span"))).text
            vote_data = re.findall(r"(\d+(?:\.\d+)?)", vote_text)
            rating, quantity = float(vote_data[0]), int(vote_data[2])
        except TimeoutException:
            print("Vote not found")
        finally:
            return rating, quantity

    def __scrape_archive(self, film_title):
        driver = utils.create_driver()
        wait = WebDriverWait(driver, 5)

        driver.get("https://www.comingsoon.it/film/")
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="ACCETTO"]'))).click()
        except TimeoutException:
            pass  # No cookie banner to accept.

        driver.execute_script("window.location = 'https://www.comingsoon.it/film/';")

        try:
            button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-target='#findFilmSml']")))
            driver.execute_script("arguments[0].click();", button)
        except TimeoutException:
            print("No search button to click.")

        try:
            wait.until(EC.element_to_be_clickable((By.ID, 'form-film-title'))).send_keys(film_title)
            search_film = wait.until(EC.element_to_be_clickable((By.ID, 'form-film-submit')))
            driver.execute_script("arguments[0].click();", search_film)
        except TimeoutException:
            print("No search form to fill.")

        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, '//b[text()="CHIUDI X"]'))).click()
        except TimeoutException:
            pass  # No pop-up window to close.

        try:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".col-xs-12.col-md-6 > a"))).click()
        except TimeoutException:
            print("No film found.")

        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, '//b[text()="CHIUDI X"]'))).click()
        except TimeoutException:
            pass  # No pop-up window to close.

        rating, quantity = self.__extract_vote_data(wait)

        url_review = driver.current_url
        # print(f"Rating: {rating}, Quantity: {quantity}")
        driver.quit()
        return url_review, rating, quantity

    def __fetch_data(self, title, film):
        # Scraping Google search results
        soup = self.__get_film_informations_by_scraping(title)
        url_review = self.__get_url_review(soup)
        if url_review:
            film['review']['ComingSoon'] = {
                'url_review': url_review
            }
            rating, quantity = self.__get_rating_quantity(soup)
            if rating:
                film['review']['ComingSoon']['rating'] = rating
            if quantity:
                film['review']['ComingSoon']['quantity'] = quantity
        # Selenium search in the archive
        else:
            url_review, rating, quantity = self.__scrape_archive(title)
            if url_review:
                film['review']['ComingSoon'] = {
                    'url_review': url_review
                }
                if rating:
                    film['review']['ComingSoon']['rating'] = rating
                if quantity:
                    film['review']['ComingSoon']['quantity'] = quantity
            else:
                print(f"ComingSoon: Error: No review found for {title}")
        return film

    def get_film_informations(self, film):
        title = film.get('original_title') or film.get('title')
        if title:
            film = self.__fetch_data(title, film)
            # If the original title search yields no results, try the regular title
            if 'ComingSoon' not in film['review']:
                title = film.get('title')
                if title:
                    film = self.__fetch_data(title, film)
        else:
            print("Error: No title found for the film")
        return film
