import logging
import os
import pickle
import re
import time
from parser.models import Category, KufarItems
from typing import Dict

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)


def save_cookies(driver, category: str, accept_button_class: str):
    """сохранение и запись в файл cookies"""
    try:
        driver.get(category)
        time.sleep(5)
        driver.find_element(by=By.XPATH,
                            value=accept_button_class).click()
        time.sleep(2)
        pickle.dump(driver.get_cookies(), open("cookies", "wb"))
        logger.debug('save cookies success')

    except Exception as ex:
        logger.error(ex)


def parse_web_page(category: Dict[str, dict],
                   cat_id: int,
                   update_db: bool = False,
                   test_conn: bool = False,
                   ):
    """Парсит переданную категорию и сохраняет ее в БД"""

    first_page = True
    cat = Category.objects.get(pk=cat_id)

    driver = start_chrome_driver()
    if not os.path.exists('cookies'):
        save_cookies(driver, category=category['url'], accept_button_class=category['accept_button'])

    if not cat.process_parse_url:
        driver.get(category['url'])
        KufarItems.objects.filter(cat_id=cat_id).update(deleted=True)
        logger.debug('parse_web_page get process_parse_url')
    else:
        driver.get(cat.process_parse_url)

    if os.path.exists('cookies'):
        for cookie in pickle.load(open("cookies", "rb")):
            driver.add_cookie(cookie)

    driver.refresh()

    try:
        while True:
            data_cards = WebDriverWait(driver, 15).until(
                EC.visibility_of_all_elements_located((By.XPATH, category["wrapper"])))
            time.sleep(1.2)
            for card in data_cards[:-8]:
                city_date = card.find_element(by=By.CLASS_NAME, value=category["country_date"]).text.split('\n')
                item_in_card = {'price': card.find_element(by=By.CLASS_NAME, value=category["price"]).text,
                                'title': card.find_element(by=By.CLASS_NAME, value=category["title"]).text,
                                'city': city_date[0],
                                'date': city_date[1],
                                'url': card.get_attribute('href'),
                                'id_item': re.search("\d{8,}", card.get_attribute("href")).group()}

                if test_conn:
                    return item_in_card
                # if not update_db:
                #     if not save_data(item_in_card, cat_id):  # Возвращается False если найден дубль.
                #         double_item_count += 1
                #         if double_item_count > 20:  # Если найдено больше 20 дублей в бд завершает работу
                #             raise Exception('Превышено заданное количество дублей')

                else:
                    update_data(item_in_card, cat_id)

            if first_page and not cat.process_parse_url:  # Переход на след. страницу.
                logger.debug('First page Next Page')
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, category['next_page']))).click()
                first_page = False
            else:
                logger.debug('Next Page')
                # назад и вперед одинаковые классы, берем второй
                next_page = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, category['next_page'])))
                # Для запуска парсера после ошибки
                # сохраняем в бд ссылку на текущую страницу.
                cat.process_parse_url = driver.current_url
                cat.save(update_fields=['process_parse_url'])
                next_page[1].click()

    except IndexError as ex:
        cat.process_parse_url = None
        cat.save(update_fields=['process_parse_url'])
        logger.error(f'Error in parse_web_page func {ex}')

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


def save_data(data: Dict[str, ...], cat_id: int):
    """Сохраняет распарсенные данные в бд"""
    res = convert_str_to_int(data)
    try:
        KufarItems.objects.create(id_item=res['id_item'], title=res['title'], base_price=res['price'],
                                  city=res['city'], date=res['date'], url=res['url'], cat_id=cat_id)
    except Exception as ex:
        logger.debug(f'Error in save_data func {ex}')
        return False

    logger.debug('save_data success')
    return True


def update_data(data: Dict[str, ...], cat_id: int):
    res = convert_str_to_int(data)

    try:
        obj = KufarItems.objects.get(id_item=res['id_item'])
    except ObjectDoesNotExist as ex:
        save_data(data=data, cat_id=cat_id)
        logger.debug(f'update_data except {ex}')
        return

    if not obj.base_price == res['price']:
        obj.new_price = res['price']
        logger.debug('update_data add new_price success')

    obj.title = res['title']
    obj.city = res['city']
    obj.date = res['date']
    obj.deleted = False
    obj.time_update = timezone.now()
    obj.save()
    logger.debug('update_data save success')


def start_chrome_driver():
    # fake useragent
    useragent = UserAgent()
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-agent={useragent.random}")
    # options.headless = True  # Безоконный режим
    options.add_argument("user-data-dir=C:\\profile")
    options.add_argument("window-size=1440,900")
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument("--disable-blink-features=AutomationControlled")
    # off errors in console
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # driver
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    return driver
