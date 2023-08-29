from typing import Dict
from storage import *
from selenium.webdriver.common.by import By
from parser.models import *

import time
import os
import pickle
import re


def save_cookies(category: str, accept_button_class: str):
    """сохранение и запись в файл cookies"""
    try:
        driver.get(category)
        sleep_driver(driver, 10)
        driver.find_element(by=By.XPATH,
                            value=accept_button_class).click()
        time.sleep(5)
        driver.implicitly_wait(5)
        pickle.dump(driver.get_cookies(), open("cookies", "wb"))

    except Exception as ex:
        print(ex)


def parse(category: Dict[str, dict], cat_id: int, update_db=False):
    """Парсит переданную категорию и сохраняет ее в БД"""
    if not os.path.exists('cookies'):
        save_cookies(category=categories['url'], accept_button_class=categories['accept_button_class'])

    driver.get(category['url'])
    for cookie in pickle.load(open("cookies", "rb")):
        driver.add_cookie(cookie)

    driver.refresh()
    sleep_driver(driver, 5)
    first_page = True
    try:
        while True:
            data_cards = driver.find_elements(by=By.XPATH, value=category["wrapper"])

            for card in data_cards[:-8]:
                item_in_card = {'price': card.find_element(by=By.CLASS_NAME, value=category["price"]).text,
                                'title': card.find_element(by=By.CLASS_NAME, value=category["title"]).text,
                                'country': card.find_element(by=By.CLASS_NAME,
                                                             value=category["country-date"]).text.split('\n')[0],
                                'date': card.find_element(by=By.CLASS_NAME,
                                                          value=category["country-date"]).text.split('\n')[1],
                                'url': card.get_attribute('href'),
                                'item_id': re.search("\d{8,}", card.get_attribute("href")).group()}

                if not update_db:
                    save_all_data(item_in_card, cat_id)
                else:
                    update_data(item_in_card)

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
        print(ex)
    finally:
        driver.close()
        driver.quit()
        return True


def sleep_driver(driver, sec):
    time.sleep(sec)
    driver.implicitly_wait(sec)


def save_all_data(data: Dict[str, str], cat_id: int):
    if type(data['price']) == str and data['id_item'] == str:
        price = ''.join(data['price'].strip(". pр").split())
        try:
            price = int(price)  # преобразуем в число или 0 если цена "Договорная"
            try:
                id_item = int(data['id_item'])
            except ValueError:
                raise ValueError(f'{data["id_item"]} ошибка формата входных данных')
        except ValueError:
            price = 0

    # print(price, data['title'], data['country'], data['date'], data['url'], int(data['item_id']))
    KufarItems.objects.create(price=price, id_item=id_item, title=data['title'],
                              country=data['country'], date=data['date'], url=data['url'], cat_id=cat_id)


def update_data(data: Dict[str, str], cat_id: int):
    pass


if __name__ == '__main__':
    parse(category=categories['kufar_notebooks'], cat_id=1)
