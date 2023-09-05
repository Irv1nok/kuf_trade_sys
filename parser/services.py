import os
import pickle
import re
import time
from parser.models import KufarItems
from typing import Dict

from django.core.exceptions import ObjectDoesNotExist

from fake_useragent import UserAgent

import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


# def save_cookies(driver, category: str, accept_button_class: str):
#     """сохранение и запись в файл cookies"""
#     try:
#         driver.get(category)
#         sleep_driver(driver, 10)
#         driver.find_element(by=By.XPATH,
#                             value=accept_button_class).click()
#         time.sleep(5)
#         driver.implicitly_wait(5)
#         pickle.dump(driver.get_cookies(), open("cookies", "wb"))
#
#     except Exception as ex:
#         print(ex)


def parse_web_page(category: Dict[str, dict], cat_id: int, update_db: bool = False, test_conn: bool = False):
    """Парсит переданную категорию и сохраняет ее в БД"""
    driver = start_chrome_driver()
    # if not os.path.exists('cookies'):
    #     save_cookies(driver, category=category['url'], accept_button_class=category['accept_button'])

    driver.get(category['url'])
    # for cookie in pickle.load(open("cookies", "rb")):
    #     driver.add_cookie(cookie)

    driver.refresh()
    sleep_driver(driver, 10)
    first_page = True
    obj_count = 0

    try:
        while True:
            data_cards = driver.find_elements(by=By.XPATH, value=category["wrapper"])

            for card in data_cards[:-8]:
                item_in_card = {'price': card.find_element(by=By.CLASS_NAME, value=category["price"]).text,
                                'title': card.find_element(by=By.CLASS_NAME, value=category["title"]).text,
                                'country': card.find_element(by=By.CLASS_NAME,
                                                             value=category["country_date"]).text.split('\n')[0],
                                'date': card.find_element(by=By.CLASS_NAME,
                                                          value=category["country_date"]).text.split('\n')[1],
                                'url': card.get_attribute('href'),
                                'item_id': re.search("\d{8,}", card.get_attribute("href")).group()}
                if test_conn:
                    return item_in_card
                if not update_db:
                    save_data(item_in_card, cat_id)
                else:
                    update_data(item_in_card, cat_id)
                    obj_count += 1
                    if obj_count == 45:
                        return

            sleep_driver(driver, 1)
            if first_page:
                driver.find_element(by=By.XPATH, value=category['next_page']).click()
                first_page = False
            else:
                # назад и вперед одинаковые классы, берем второй
                next_page = driver.find_elements(by=By.XPATH, value=category['next_page'])
                next_page[1].click()

            sleep_driver(driver, 5)

    except Exception as ex:
        print('Error in object', ex)
    finally:
        driver.close()
        driver.quit()


def convert_int_to_str(data: dict[str, str]):
    """преобразует price и item_id в коллекции к int"""
    if isinstance(data['price'], str) and isinstance(data['item_id'], str):
        price = ''.join(data['price'].strip(". pр").split())
        try:
            data['price'] = int(price)  # преобразуем в число или возвращаем 0 если цена "Договорная"
            try:
                data['item_id'] = int(data['item_id'])
            except ValueError as ex:
                print(ex, f'{data["item_id"]} ошибка формата входных данных')
        except ValueError:
            data['price'] = 0
    return data


def sleep_driver(driver, sec):
    time.sleep(sec)
    driver.implicitly_wait(sec)


def save_data(data: Dict[str, ...], cat_id: int):
    res = convert_int_to_str(data)
    obj = KufarItems.objects.create(id_item=res['id_item'], title=res['title'],
                                    country=res['country'], date=res['date'], url=res['url'], cat_id=cat_id)

    obj.price.def_price = data['price']
    obj.save()


def update_data(data: Dict[str, ...], cat_id: int):
    try:
        obj = KufarItems.objects.get(data['id_item'])
    except ObjectDoesNotExist:
        save_data(data, cat_id)
        return

    if not obj.price.def_price == data['price']:
        obj.price.new_price = data['price']
        obj.title = data['title']
        obj.save(update_fields=['price', 'title'])


def check_delete_or_sold_obj(cat_id: int):
    qs = KufarItems.objects.filter(cat_id=cat_id) & KufarItems.objects.filter(deleted=False)
    for q in qs:
        res = requests.get(q.url)
        if res.status_code == 404:
            q.deleted = True
            q.save()


def start_chrome_driver():
    # fake useragent
    useragent = UserAgent()
    # options
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-agent={useragent.random}")
    # options.headless = True # Безоконный режим
    options.add_argument("user-data-dir=C:\\profile")
    options.add_argument("--headless")
    options.add_argument("--start-maximized")
    options.add_argument(f"--disable-blink-features=AutomationControlled")
    # off errors in console
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # driver
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    return driver


if __name__ == '__main__':
    parse_web_page(category={None}, cat_id=1)
