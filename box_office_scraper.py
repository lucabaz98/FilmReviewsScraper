import requests
from bs4 import BeautifulSoup
import json
import os
import re


def get_soup(url):
    try:
        headers = {'User-Agent': 'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}
        response = requests.get(url, headers, allow_redirects=False)
        response.encoding = 'latin1'
        return BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.TooManyRedirects as e:
        print(e)
        return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None

def get_rank(row):
    return int(row.find('strong').text.strip())

def get_url_review(row):
    return row.find('a').get('href')

def get_title(row):
    return row.find('a').text.strip()

def get_original_title(row):
    return row.find_all('strong')[1].find_previous_sibling('br').previous_sibling.strip().replace('(', '').replace(')', '')

def get_register(row):
    return row.find_all('strong')[1].text.strip().replace(', ',',').split(',')

def get_revenue(row):
    return row.find_all('strong')[2].text.strip().split()[-1]

def get_genre_from_row(genere_region_year):
    return genere_region_year.split(' - ')[0]

def get_region_from_row(genere_region_year):
    return genere_region_year.split(' - ')[1].split(', ')[:-1]

def get_year_from_row(genere_region_year):
    return genere_region_year.split(' - ')[1].split(', ')[-1]

def get_genre_region_year(row):
    return row.find_all('strong')[2].find_previous_sibling('br').previous_sibling.strip()

def get_rating_quantity(url_review):
  soup = get_soup(url_review)
  try:
    target_div = soup.find("div", class_="display-dettagli-cast")
    critica_td = target_div.find("a", string=lambda text: "critica" in text if text else False)
    rating = float(critica_td.previous_sibling.previous_sibling.get_text().replace(',', '.'))
    quantity = int(re.search(r'\d+', critica_td.previous_sibling.get_text()).group())
  except:
    rating = None
    quantity = None
  return rating, quantity

def save_json(doc, dir_name, file_name):
    dir_path = os.path.join("Data/Box_Office", dir_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    with open(f'{dir_path}/{file_name}', 'w') as f:
        json.dump(doc, f, indent=4, ensure_ascii=False)
        print(f"File {file_name} written successfully")
        
def film_informations(row, country, season):
    film = {}
    
    title = get_title(row)
    if title != "":
        film['title'] = title
    
    original_title = get_original_title(row)
    if  original_title != "":
        film['original_title'] = original_title
        
    register = get_register(row)
    if all(item != '' for item in register):
        if len(register) == 1:
            register = register[0]
        film['register'] = register

    genere_region_year = get_genre_region_year(row)
    
    genere = get_genre_from_row(genere_region_year)
    if genere != "":
        film['genere'] = genere
        
    region = get_region_from_row(genere_region_year)

    if all(item != '' for item in region):
        if len(region) == 1:
            region = region[0]
        film['region'] = region
        
    year = get_year_from_row(genere_region_year)
    if year != "":
        film['year'] = int(year)
            
    film['box_office'] = {}
    film['box_office'][country] = {}
    
    rank = get_rank(row)
    if rank != "":
        film['box_office'][country]['rank'] = rank
        
    revenue = get_revenue(row)
    if revenue != "":
        film['box_office'][country]['revenue'] = int(revenue.replace(".", ""))
    
    film['box_office'][country]['season'] = season
    
    film['review'] = {}
    film['review']['MyMovies'] = {}
    url_review = get_url_review(row)
    
    if url_review != "":
        film['review']['MyMovies']['url_review'] = url_review 
    
    rating, quantity = get_rating_quantity(url_review)
    if rating != None:
        film['review']['MyMovies']['rating'] = rating
    if quantity != None:
        film['review']['MyMovies']['quantity'] = quantity
        
    return film