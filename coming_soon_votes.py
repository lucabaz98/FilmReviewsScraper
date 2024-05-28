import requests
from bs4 import BeautifulSoup
import time
import random
import re
import coming_soon_archive_search
    
def get_soup(url):
    try:
        headers = {'User-Agent': 'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.encoding = 'latin1'
        return BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(e)
        return None
    
def film_informations(title):
    title_unicode = re.sub(r'[^A-Za-z0-9\s]', ' ', title)
    time.sleep(random.uniform(1, 3))
    query = f"{title_unicode} comingsoon" #  film {film['register']} {film['year']}
    url = f"https://www.google.com/search?q={query}"
 
    return get_soup(url)
    

def get_url_review(soup):
    url_review = None
    try:
        url_review = soup.find('a', href=lambda href: href and href.startswith('https://www.comingsoon.it/film'))
        url_review = url_review['href']
    finally:
        return url_review

def get_rating_quantity(soup):
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


def coming_soon_informations(film, title):
    soup = film_informations(title)
    
    url_review = get_url_review(soup)
    if url_review:
        film['review']['ComingSoon'] = {
            'url_review': url_review
        }
        # film['review']['ComingSoon']['url_review'] = url_review
        rating, quantity = get_rating_quantity(soup)
        if rating:
            film['review']['ComingSoon']['rating'] = rating
        if quantity:
            film['review']['ComingSoon']['quantity'] = quantity
     
    else:
        url_review, rating, quantity = coming_soon_archive_search.scrape_archive(title)
        if url_review:
            film['review']['ComingSoon'] = {}
            film['review']['ComingSoon']['url_review'] = url_review
            if rating:
                film['review']['ComingSoon']['rating'] = rating
            if quantity:
                film['review']['ComingSoon']['quantity'] = quantity
        else:
            print(f"ComingSoon: Error: No review found for {title}")
                
    return film
