import logging
import os
import pickle
import re
import time
from parser.models import Category, KufarItems
from background_task import background

from typing import Dict

from bs4 import BeautifulSoup

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

logger = logging.getLogger(__name__)


def start_chrome_driver():
    # fake useragent
    useragent = UserAgent()
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-agent={useragent.random}")
    # options.headless = True  # Безоконный режим
    options.add_argument("user-data-dir=./profile")
    options.add_argument("window-size=1920,1080")
    options.add_argument("start-maximized")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("useAutomationExtension", False)
    # off errors in console
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # driver
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    return driver


@background(schedule=60)
def get_new_updates_in_categories():
    driver = start_chrome_driver()
    all_cats = Category.objects.all()
    update = True
    for cat in all_cats:
        parse_web_page(driver=driver, update=update, category=cat.__dict__, cat_id=cat.id)
    driver.close()
    driver.quit()
    logger.debug('Finish get_new_updates_in_categories')


@background(schedule=60)
def get_all_data_in_category(category: dict, cat_id: int):
    driver = start_chrome_driver()
    parse_web_page(driver=driver, category=category, cat_id=cat_id)
    logger.debug('Finish get_all_data_in_category')


def get_test_data(category: dict, cat_id: int, test_conn: bool):
    driver = start_chrome_driver()
    return parse_web_page(driver=driver, category=category, cat_id=cat_id, test_conn=test_conn)


def save_cookies(driver, category: str, accept_button_class: str):
    """сохранение и запись в файл cookies"""
    driver.get(category)
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                                                                    accept_button_class))).click()
    except Exception as ex:
        logger.error(ex)
    finally:
        pickle.dump(driver.get_cookies(), open('cookies', 'wb'))
        logger.debug('save cookies success')


def parse_web_page(driver,
                   category: Dict[str, dict],
                   cat_id: int,
                   update: bool = False,
                   test_conn: bool = False,
                   ):
    first_page = True
    cat = Category.objects.get(pk=cat_id)

    if not os.path.exists('cookies'):
        save_cookies(driver, category=category['url'], accept_button_class=category['accept_button'])

    if not update:
        if not cat.process_parse_url:
            driver.get(category['url'])
            if not test_conn:
                KufarItems.objects.filter(cat_id=cat_id).update(deleted=True)
        else:
            driver.get(cat.process_parse_url)
            logger.debug('parse_web_page load process_parse_url')
    else:
        driver.get(category['url'])

    if os.path.exists('cookies'):
        for cookie in pickle.load(open('cookies', 'rb')):
            driver.add_cookie(cookie)

    driver.refresh()

    try:
        while True:
            time.sleep(1.2)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            all_items = soup.find_all('a', class_=category['wrapper'])

            for item in all_items[:-8]:
                price = item.find('p', class_=category['price']).text
                title = item.find('h3', class_=category['title']).text
                city_date = item.find('div', class_=category['city_date'])
                city = city_date.find('p').text
                date = city_date.find('span').text

                item_in_card = {'price': price,
                                'title': title,
                                'city': city,
                                'date': date,
                                'url': item.get('href'),
                                'id_item': re.search("\d{8,}", item.get("href")).group()}
                if test_conn:
                    return item_in_card

                update_data(item_in_card, cat_id)

            if not update and not test_conn:
                if first_page and not cat.process_parse_url:  # Переход на след. страницу.
                    logger.debug('First page Next Page')
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, category['next_page']))).click()
                    first_page = False
                else:
                    logger.debug('Next Page')
                    # назад и вперед одинаковые классы, берем второй
                    next_page = WebDriverWait(driver, 10).until(
                        EC.visibility_of_all_elements_located((By.XPATH, category['next_page'])))
                    # Для запуска парсера после ошибки
                    # сохраняем в бд ссылку на текущую страницу.
                    cat.process_parse_url = driver.current_url
                    cat.save(update_fields=['process_parse_url'])
                    next_page[1].click()
            else:
                return

    except IndexError as ex:
        cat.process_parse_url = None
        cat.save(update_fields=['process_parse_url'])
        logger.error(f'Error in parse_web_page func {ex}')
        driver.close()
        driver.quit()

    except Exception as ex:
        logger.error(f'Error in parse_web_page func {ex}')
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


