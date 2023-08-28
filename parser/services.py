from typing import Dict
from storage import *
from selenium.webdriver.common.by import By
from parser.models import *

import time
import os
import pickle
import re


def save_coockies(category : str, accept_button_class: str):
    """сохранение и запись в файл coockies"""
    try:
        driver.get(category)
        sleep_driver(driver, 10)
        driver.find_element(by=By.XPATH,
                            value=accept_button_class).click()
        time.sleep(5)
        driver.implicitly_wait(5)
        pickle.dump(driver.get_cookies(), open("cookies", "wb"))

    except Exception as ex:
        return ex

def parse(category: Dict[str, dict]):
    """Парсит переданную категорию и сохраняет ее в БД"""
    for cookie in pickle.load(open("cookies", "rb")):
        driver.add_cookie(cookie)

    driver.refresh()
    sleep_driver(driver, 5)
    first_page = True
    try:
        while True:
            data_cards = driver.find_elements(by=By.XPATH, value=category['wrapper'])

            for card in data_cards:
                save_all_data({'price': card.find_element(by=By.XPATH, value=category["price"]).text,
                                'title': card.find_element(by=By.XPATH, value=category['title']).text,
                                 'country': card.find_element(by=By.XPATH,
                                                        value=category['country-date']).text.split('\n')[0],
                                 'date': card.find_element(by=By.XPATH,
                                                        value=category['country-date']).text.split('\n')[1],
                                 'url': card.get_attribute('href'),
                               'id_item': re.search("\d{8,}", card.get_attribute('href')).group()})

            sleep_driver(driver, 1)
            if first_page:
                next_page = driver.find_element(by=By.XPATH, value=category['next_page']).click()
                first_page = False
            else:
                # вперед и назад одинаковые классы, берем второй
                next_page = driver.find_elements(by=By.XPATH, value=category['next_page'])
                next_page[1].click()

            sleep_driver(driver, 5)

    except Exception as ex:
        return ex
    finally:
        driver.close()
        driver.quit()
        return True


def sleep_driver(driver, sec):
    time.sleep(sec)
    driver.implicitly_wait(sec)

def save_all_data(data: dict):
    KufarItems.objects.create(id_item=data['id_item'], price=data['price'], title=data['title'],
                              country=data['country'], date=data['date'], url=data['url'])


if __name__ == '__main__':
    if not os.path.exists('cookies'):
        save_coockies(categories['kufar_notebooks']['url'],
                      accept_button_class=categories['kufar_notebooks']['accept_button_class'])

    parse(categories['kufar_notebooks'])