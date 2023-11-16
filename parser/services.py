import logging
import os
import pickle
import re
import time
from datetime import timedelta
from parser.models import Category, KufarItems
from typing import Dict

from background_task import background

from bot.models import FavoritesItems, SearchItems
from bot.services import send_message

from bs4 import BeautifulSoup

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

no_advertising_cats = [19, ]  # Категории без рекламы проходятся без среза последних 8 объявлений
logger = logging.getLogger(__name__)


def start_chrome_driver():
    # fake useragent
    useragent = UserAgent()
    options = webdriver.ChromeOptions()
    options.add_argument(f'--user-agent={useragent.random}')
    options.add_argument('--headless=new')  # Безоконный режим
    options.add_argument('user-data-dir=./profile')  # Создание профиля для адблок
    options.add_argument('window-size=1920,1080')
    options.add_argument('start-maximized')
    options.add_argument('--blink-settings=imagesEnabled=false')  # Настройки хрома
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument('--disable-blink-features')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('useAutomationExtension', False)
    # off errors in console
    options.add_experimental_option('excludeSwitches', ["enable-logging"])

    # driver
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    return driver


@background(schedule=60)
def get_new_updates_in_categories():
    logger.info('Start get_new_updates_in_categories')
    driver = start_chrome_driver()
    all_cats = Category.objects.all()
    update = True
    for cat in all_cats:
        parse_web_page(driver=driver, update=update, category=cat.__dict__, cat_id=cat.id)
    driver.close()
    driver.quit()
    logger.info('Finish get_new_updates_in_categories')


@background(schedule=60)
def get_all_data_in_category(category: dict, cat_id: int):
    logger.info(f'Start get_all_data_in_category {category["name"]}')
    driver = start_chrome_driver()
    parse_web_page(driver=driver, category=category, cat_id=cat_id)
    logger.info(f'Finish get_all_data_in_category {category["name"]}')


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
        logger.debug(ex)
    finally:
        pickle.dump(driver.get_cookies(), open('cookies', 'wb'))
        logger.info('Save cookies success')


def parse_web_page(driver,
                   category: Dict[str, any],
                   cat_id: int,
                   update: bool = False,
                   test_conn: bool = False,
                   ):
    first_page = True
    cat = Category.objects.get(pk=cat_id)
    count_ad = cat.count_ad

    search_items = SearchItems.objects.filter(category=cat_id)
    is_search_items = search_items.exists()

    if not os.path.exists('cookies'):
        save_cookies(driver, category=category['url'], accept_button_class=category['accept_button'])

    if not update:
        if not cat.process_parse_url:
            driver.get(category['url'])
        else:
            driver.get(cat.process_parse_url)
            logger.info('parse_web_page load process_parse_url')
    else:
        driver.get(category['url'])

    if os.path.exists('cookies'):
        for cookie in pickle.load(open('cookies', 'rb')):
            driver.add_cookie(cookie)

    driver.refresh()

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, category['count_ads'])))
    try:
        while True:
            time.sleep(0.5)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            all_items = soup.find_all('a', class_=category['wrapper'])
            try:
                res = soup.find('span', class_='styles_counter__NSFh7').text
                res1 = ''.join(res.split()[:-1])
                count_ads = int(res1)
            except Exception as ex:
                logger.error(f'Exception in parse_web_page while {ex}')
                raise Exception

            for item in all_items[:-8 if cat_id not in no_advertising_cats else None]:
                price = item.find('p', class_=category['price']).text
                title = item.find('h3', class_=category['title']).text
                city_date = item.find('div', class_=category['city_date'])
                city = city_date.find('p').text
                date = city_date.find('span').text
                try:
                    photo = item.find('div', class_=category['photo']).find('img')['src']
                except Exception as ex:
                    logger.info(f'Error in cycle while -> photo {ex}')
                    photo = None

                item_in_card = {'price': price,
                                'title': title,
                                'city': city,
                                'date': date,
                                'url': item.get('href'),
                                'id_item': re.search("\d{8,}", item.get("href")).group(),
                                'photo': photo}

                if test_conn:
                    return item_in_card

                count_ad += 1
                update_data(item_in_card, cat_id, is_search_items, search_items)
                logger.info(f'№ {count_ad}')

            if not update and not test_conn:
                if first_page and not cat.process_parse_url:  # Переход на след. страницу.
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, category['next_page']))).click()
                    first_page = False
                    logger.info('First page Next Page')
                else:
                    try:
                        next_page = WebDriverWait(driver, 10).until(
                            EC.visibility_of_all_elements_located((By.XPATH, category['next_page'])))
                    except Exception as ex:
                        logger.exception(f'Exception in parse_web_page -> next_page element not located {ex}'
                                         f'\nRESCHEDULE task -> {category["name"]}')
                        get_all_data_in_category(category=category,
                                                 cat_id=cat_id,
                                                 schedule=10,
                                                 priority=5)
                    # После ошибки, для продолжения работы с текущей страницы
                    # сохраняем в бд ссылку на текущую страницу.
                    cat.process_parse_url = driver.current_url
                    cat.count_ad = count_ad
                    cat.save(update_fields=['process_parse_url', 'count_ad'])

                    next_page[1].click()  # Raise IndexError когда доходит до последней страницы
                    # назад и вперед одинаковые классы, берем второй
                    logger.info('Next Page')
            else:
                return

    except IndexError as ex:
        # Доп. проверка что парсер дошел до конца категории объявлений
        if count_ad >= count_ads:
            logger.info(f'Всего объявлений: {count_ads}')
            cat.process_parse_url = None
            cat.count_ad = 0
            cat.save(update_fields=['process_parse_url', 'count_ad'])
            update_sold_items_in_category(cat_id)
            logger.exception(f'IndexError in parse_web_page func {ex}')
            driver.close()
            driver.quit()
        else:
            logger.exception(f'Exception in parse_web_page -> Error in Kufar get nex_page {ex}'
                             f'\nRESCHEDULE task -> {category["name"]}')
            get_all_data_in_category(category=category,
                                     cat_id=cat_id,
                                     schedule=10,
                                     priority=5)
    except Exception as ex:
        logger.exception(f'Exception in parse_web_page func {ex}')
        driver.close()
        driver.quit()


def update_data(data: Dict[str, ...], cat_id: int, is_search_items: bool, search_items):
    """Функция ищет распарсенный объект в бд по уникальному id товара,
    если не находит, сохранет его, иначе обновляет данные товара"""
    res = convert_str_to_int(data)

    try:
        obj = KufarItems.objects.get(id_item=res['id_item'], cat_id=cat_id)
    except ObjectDoesNotExist as ex:
        save_data(data=res, cat_id=cat_id, is_search_items=is_search_items, search_items=search_items)
        logger.debug(f'Exception in update_data func {ex}')
        return

    if not obj.base_price == res['price'] and not obj.new_price == res['price']:
        obj.new_price = res['price']
        logger.info('update_data save new_price')
        # Отправляем сообщения всем пользователям у кого данный товар в избранном.
        if obj.in_favorites:  # Если присутствует запрос отслеживания товара
            send_users_msg_fav_items(obj=obj, update=True)
        logger.info('update_data save new_price success')

    obj.title = res['title']
    obj.city = res['city']
    obj.date = res['date']
    obj.deleted = False
    obj.time_update = timezone.now()
    obj.photo_url = res['photo']
    obj.save()
    logger.info('update_data Update success')


def convert_str_to_int(data: dict[str, any]):
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


def save_data(data: Dict[str, any], cat_id: int, is_search_items: bool, search_items):
    """Сохраняет распарсенные данные в бд"""
    try:
        obj = KufarItems.objects.create(id_item=data['id_item'], title=data['title'], base_price=data['price'],
                                        city=data['city'], date=data['date'], url=data['url'], photo_url=data['photo'],
                                        cat_id=cat_id)
        if is_search_items:  # Если прустствует запрос поиска товара в данной категории
            send_users_msg_search_items(search_items, obj=obj)
    except Exception as ex:
        logger.error(f'Exception in save_data func {ex}')
    logger.info('save_data Create Success')


def update_sold_items_in_category(cat_id: int):
    delta = timezone.now() - timedelta(hours=6)
    qs = (KufarItems.objects.filter(cat_id=cat_id,
                                    deleted=False,
                                    time_update__lt=delta) & KufarItems.objects.filter(cat_id=cat_id,
                                                                                       deleted=False,
                                                                                       time_update__isnull=True))
    if qs.exists():
        send_users_msg_sold_items(qs)
        qs.update(deleted=True)
        logger.info(f'delta {delta}, update_sold_items_in_category SUCCESS')
    else:
        logger.info('update_sold_items_in_category FALSE, no one obj in QuerySet')


def send_users_msg_sold_items(qs):
    qs_fav = qs.filter(in_favorites=True)
    if qs_fav.exists():
        for obj in qs_fav:
            try:
                send_users_msg_fav_items(obj, sold=True)
                obj.in_favorites = False
                obj.save(update_fields=['in_favorites'])
                logger.info('Send_users_msg_fav_items Success')
            except Exception as ex:
                logger.error(f'Exception in update_sold_items_in_category {ex}')


def send_users_msg_fav_items(obj, update=False, sold=False):
    try:
        for pk in FavoritesItems.objects.filter(pk_item=obj.pk):
            send_message(pk.bot_user.telegram_id, obj=obj, update_fav_message=update, sold_item_message=sold)
            logger.info('send_message success in update_data func')
    except Exception as ex:
        logger.error(f'Exception in update_data func send_message Error {ex}')


def send_users_msg_search_items(search_items, obj):
    find_status = [False, False, False]
    for obj_search in search_items:
        if obj_search.title:
            if len(obj_search.title.split()) > 1:
                res = [True if x in obj.title.lower() else False for x in obj_search.title.lower().split()]
                if all(res):
                    find_status[0] = True
            elif obj_search.title.lower() in obj.title.lower():
                find_status[0] = True
        else:
            find_status[0] = True

        if obj_search.min_price and obj_search.max_price:
            if obj_search.min_price <= obj.base_price <= obj_search.max_price:
                find_status[1] = True
        else:
            find_status[1] = True

        if obj_search.city:
            if obj_search.city in obj.city:
                find_status[2] = True
        else:
            find_status[2] = True

        if all(find_status):
            try:
                send_message(user_id=obj_search.bot_user.telegram_id, obj=obj, search_item_message=True)
            except Exception as ex:
                logger.error(f'Exception in send_users_msg_search_items func send_message Error {ex}')
