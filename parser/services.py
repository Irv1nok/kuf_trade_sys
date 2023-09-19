# import os
# import pickle
import logging
import re
import time
from parser.models import KufarItems
from typing import Dict

from django.core.exceptions import ObjectDoesNotExist

from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)


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


def parse_web_page(category: Dict[str, dict],
                   cat_id: int,
                   update_db: bool = False,
                   test_conn: bool = False,
                   ):
    """Парсит переданную категорию и сохраняет ее в БД"""

    if update_db:
        KufarItems.objects.filter(cat_id=cat_id).update(deleted=True)  # Сброс к дефолтным зн.бд.

    driver = start_chrome_driver()
    # if not os.path.exists('cookies'):
    #     save_cookies(driver, category=category['url'], accept_button_class=category['accept_button'])

    driver.get(category['url'])
    # for cookie in pickle.load(open("cookies", "rb")):
    #     driver.add_cookie(cookie)

    # driver.refresh()
    sleep_driver(driver, 7)
    first_page = True
    double_item_count = 0  # Найденные дубли в бд

    try:
        while True:
            data_cards = driver.find_elements(by=By.XPATH, value=category["wrapper"])

            for card in data_cards[:-8]:
                item_in_card = {'price': card.find_element(by=By.CLASS_NAME,
                                                           value=category["price"]).text,
                                'title': card.find_element(by=By.CLASS_NAME,
                                                           value=category["title"]).text,
                                'city': card.find_element(by=By.CLASS_NAME,
                                                          value=category["country_date"]).text.split('\n')[0],
                                'date': card.find_element(by=By.CLASS_NAME,
                                                          value=category["country_date"]).text.split('\n')[1],
                                'url': card.get_attribute('href'),
                                'id_item': re.search("\d{8,}", card.get_attribute("href")).group()}
                if test_conn:
                    return item_in_card
                if not update_db:
                    if not save_data(item_in_card, cat_id):  # Возвращается False если найден дубль.
                        double_item_count += 1
                        if double_item_count > 20:  # Если найдено больше 20 дублей в бд завершает работу
                            return

                else:
                    update_data(item_in_card, cat_id)

            time.sleep(1)
            if first_page:  # Переход на след. страницу.
                driver.find_element(by=By.XPATH, value=category['next_page']).click()
                first_page = False
            else:
                # назад и вперед одинаковые классы, берем второй
                next_page = driver.find_elements(by=By.XPATH, value=category['next_page'])
                next_page[1].click()

            sleep_driver(driver, 3)

    except Exception as ex:
        logger.error(f'Error in parse_web_page func {ex}')
    finally:
        driver.close()
        driver.quit()


def convert_str_to_int(data: dict[str, str]):
    """преобразует price и item_id в коллекции к int"""
    if isinstance(data['price'], str) and isinstance(data['id_item'], str):
        price = ''.join(data['price'].strip(". pр").split())
        try:
            data['price'] = int(price)  # преобразуем в число или возвращаем 0 если цена "Договорная"
            try:
                data['id_item'] = int(data['id_item'])
            except ValueError as ex:
                logger.error(f'{data["id_item"]} ошибка формата входных данных {ex}')
        except ValueError:
            data['price'] = 0
    return data


def sleep_driver(driver, sec):
    time.sleep(sec)
    driver.implicitly_wait(sec)


def save_data(data: Dict[str, ...], cat_id: int):
    """Сохраняет распарсенные данные в бд"""
    res = convert_str_to_int(data)
    try:
        KufarItems.objects.create(id_item=res['id_item'], title=res['title'], base_price=res['price'],
                                  city=res['city'], date=res['date'], url=res['url'], cat_id=cat_id)
    except Exception as ex:
        logger.debug(f'Error in save_data func {ex}')
        return False

    logger.debug('save_success')
    return True


def update_data(data: Dict[str, ...], cat_id: int):
    res = convert_str_to_int(data)

    try:
        obj = KufarItems.objects.get(id_item=res['id_item'])
    except Exception:
        save_data(data=data, cat_id=cat_id)
        logger.debug('saved')
        return

    if not obj.base_price == res['price']:
        obj.new_price = res['price']
    obj.title = res['title']
    obj.deleted = False
    obj.save(update_fields=['new_price', 'title', 'deleted'])
    logger.debug('updated')


def start_chrome_driver():
    # fake useragent
    useragent = UserAgent()
    # options
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-agent={useragent.random}")
    # options.headless = True  # Безоконный режим
    options.add_argument("user-data-dir=C:\\profile")
    options.add_argument("--start-maximized")
    options.add_argument("window-size=1400,600")
    options.add_argument(f"--disable-blink-features=AutomationControlled")
    # off errors in console
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # driver
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    return driver


if __name__ == '__main__':
    parse_web_page(category={None}, cat_id=1)
