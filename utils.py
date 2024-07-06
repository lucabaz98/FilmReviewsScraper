from selenium import webdriver
import yaml
import requests
from bs4 import BeautifulSoup
import pymongo


def get_configs(configs_filename: str = "configs.yaml"):
    with open(configs_filename, 'r') as file:
        return yaml.safe_load(file)


# def get_configs(configs_filename: str = "configs.yaml") -> dict:
#     config_path = Path(Path(__file__).resolve().parent, configs_filename)
#     with config_path.open('r', encoding='utf-8') as f:
#         if config_path.suffix == '.yaml':
#             configs = yaml.safe_load(f)
#         elif config_path.suffix == '.json':
#             configs = json.load(f)
#         else:
#             raise NotImplementedError(
#                 f"Provided config file has extension {config_path.suffix} which is not supported")
#     print(f"Configs at '{config_path.as_posix()}' are:\n{pformat(configs)}")
#     return configs


def get_soup(url, config_path='configs.yaml'):
    configs = get_configs(config_path)
    try:
        response = requests.get(url, headers={'User-Agent': configs['USER_AGENT']}, allow_redirects=False)
        response.encoding = 'latin1'
        return BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.TooManyRedirects as e:
        print(e)
        return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None


# Creates a Selenium WebDriver with specified options.
def create_driver():
    configs = get_configs()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    options.add_argument(configs['USER_AGENT'])
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1024, 768)
    return driver


# Create an ordered list of indices for scraping film because the website lists films in a specific order
def create_ordered_box_office(url):
    soup = get_soup(url)
    rows = soup.find_all('tr', attrs={'valign': 'top'})
    n = len(rows)
    first_half = list(range(n // 2))
    second_half = list(range(n // 2, n))
    return rows, [item for pair in zip(first_half, second_half) for item in pair]


def initialize_database(collection_name):
    config = get_configs()
    client = pymongo.MongoClient(config['MONGODB_HOST'], config['MONGODB_PORT'])
    db = client[config['MONGODB_DB_NAME']]
    collection = db.get_collection(collection_name)
    collection.create_index([('title', 1)], unique=True)
    return collection
