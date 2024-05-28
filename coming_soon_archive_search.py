from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re

# Creates a Selenium WebDriver with specified options.
def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1024, 768)
    return driver

# Extracts the vote data from the film page.
def extract_vote_data(wait):
    rating, quantity = None, None
    try:
        vote_text = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='mrl']/span"))).text
        vote_data = re.findall(r"(\d+(?:\.\d+)?)", vote_text)
        rating, quantity = float(vote_data[0]), int(vote_data[2])
    except TimeoutException:
        print("Vote not found")
    finally:
        return rating, quantity
    

def scrape_archive(film_title):
    driver = create_driver()
    wait = WebDriverWait(driver, 5)

    driver.get("https://www.comingsoon.it/film/")
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="ACCETTO"]'))).click()
    except TimeoutException:
        pass # No cookie banner to accept.
    
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
        pass # No pop-up window to close.
        
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".col-xs-12.col-md-6 > a"))).click()
    except TimeoutException:
        print("No film found.")
        
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, '//b[text()="CHIUDI X"]'))).click()
    except TimeoutException:
        pass # No pop-up window to close.
       
    rating, quantity = extract_vote_data(wait)
    
    url_review = (driver.current_url)
    # print(f"Rating: {rating}, Quantity: {quantity}")
    driver.quit()
    return url_review, rating, quantity
