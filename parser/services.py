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

from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


def start_chrome_driver():
    # fake useragent
    useragent = UserAgent()
    options = webdriver.ChromeOptions()
    options.add_argument(f'--user-agent={useragent.random}')
    options.add_argument('--no-sandbox')
    options.add_argument('--headless=new')  # Безоконный режим
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-crash-reporter')
    options.add_argument('user-data-dir=./profile')  # Создание профиля для адблок
    # options.add_argument('window-size=1920,1080')
    options.add_argument('--blink-settings=imagesEnabled=false')  # Настройки хрома
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('useAutomationExtension', False)
    # off errors in console
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('excludeSwitches', ["enable-logging"])

    # driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    category = Category.objects.get(pk=1)
    if not os.path.exists('cookies'):
        save_cookies(driver, accept_button_class=category.accept_button)
        driver.refresh()
    if os.path.exists('cookies'):
        logger.info('Open www.kufar.by/l')
        driver.get('https://www.kufar.by/l')
        logger.info('Load cookies')
        for cookie in pickle.load(open('cookies', 'rb')):
            driver.add_cookie(cookie)
    driver.refresh()
    return driver


@background(schedule=60)
def get_new_updates_in_categories():
    logger.info('Start get_new_updates_in_categories')
    driver = start_chrome_driver()
    all_cats = Category.objects.all()
    update = True

    for cat in all_cats:
        parse_web_page(driver=driver, update=update, category=cat.__dict__, cat_id=cat.id, url=cat.url_used)
        time.sleep(1)
        parse_web_page(driver=driver, update=update, category=cat.__dict__, cat_id=cat.id, url=cat.url_new)
    driver.close()
    driver.quit()
    time.sleep(3)  # По неизвестной причине не освобождается память.
    logger.info('Finish get_new_updates_in_categories')


@background(schedule=60)
def get_all_data_in_category(category: dict, cat_id: int):
    cat = Category.objects.get(pk=cat_id)
    logger.info('Start DRIVER')
    driver = start_chrome_driver()

    logger.info(f'Start get_all_data_in_category {category["name"]}')
    status = 'RESCHEDULE'

    res = parse_web_page(driver=driver, category=category, cat_id=cat_id, url=cat.url_used)
    time.sleep(1)
    if res[0] and not res[1]:  # [0] статус выполнения True/False, [1] True/False новые или б/у
        res = parse_web_page(driver=driver, category=category, cat_id=cat_id, url=cat.url_new)
    if res[0]:
        status = 'SUCCESS'
        update_sold_items_in_category(cat_id)

    driver.close()
    driver.quit()
    time.sleep(2)  # Иногда, по неизвестной причине не успевала освободиться память.
    logger.info(f'{status} get_all_data_in_category {category["name"]}')


def get_test_data(category: dict, cat_id: int, test_conn: bool):
    driver = start_chrome_driver()
    return parse_web_page(driver=driver, category=category, cat_id=cat_id, test_conn=test_conn,
                          url=category['url_used'])


def save_cookies(driver, accept_button_class: str):
    """ Cохранение и запись в файл cookies """
    driver.get('https://www.kufar.by/l')
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                                                                    accept_button_class))).click()
    except Exception as ex:
        logger.debug(f'Error in save_cookies {ex}')
    finally:
        pickle.dump(driver.get_cookies(), open('cookies', 'wb'))
        logger.info('Save cookies success')


def parse_web_page(driver,
                   category,
                   cat_id: int,
                   url: str,
                   update: bool = False,
                   test_conn: bool = False,
                   ):

    cat = Category.objects.get(pk=cat_id)
    count_ad = cat.count_ad  # Сколько объявлений прошел парсер
    count_ads = 0  # Количество объявлениий данной категории
    page_number = 1
    first_page = True

    if not update:
        if not cat.process_parse_url:
            driver.get(url)
        else:
            driver.get(cat.process_parse_url)
            logger.info('parse_web_page load process_parse_url')
    else:
        driver.get(url)

    item_state = False if 'cnd=1' in driver.current_url else True  # cnd=1 - б/у, cnd=2 - новые.
    state = SearchItems.objects.filter(category=cat_id, state=item_state)
    all_null = SearchItems.objects.filter(category=cat_id, state__isnull=True)  # null - любое состояние.
    search_items = state | all_null
    is_search_items = search_items.exists()

    if not update:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, category['count_ads'])))
        try:
            res = driver.find_element(
                By.XPATH, category['count_ads']).text
            res1 = ''.join(res.split()[:-1])
            count_ads = int(res1)
        except TypeError:
            logger.error('\n---------------------------------------------'
                         '\nException in parse_web_page TypeError count_ads'
                         '\n---------------------------------------------')
            raise Exception
        except Exception as ex:
            logger.error('\n----------------------------------------------'
                         f'\nException in parse_web_page find count_ads {ex}'
                         '\n----------------------------------------------')
            raise Exception

    try:
        while True:
            time.sleep(0.3)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            all_items = soup.find_all('a', class_=category['wrapper'])

            for item in all_items:
                url_item = item.get('href')
                if 'rank=' in url_item:  # Фильтр последних рекламных объявлений
                    try:
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
                    except Exception as ex:  # Пропуск рекламного товара с некорректными данными
                        logger.info(f'{ex}')
                        continue
                    else:
                        item_in_card = {'price': price,
                                        'title': title,
                                        'city': city,
                                        'date': date,
                                        'url': url_item,
                                        'id_item': re.search("\d{8,}", item.get("href")).group(),
                                        'photo': photo,
                                        'item_state': item_state}
                else:
                    continue

                if test_conn:
                    return item_in_card

                count_ad += 1
                update_data(data=item_in_card,
                            cat_id=cat_id,
                            is_search_items=is_search_items,
                            search_items=search_items)

                logger.info(f'№ {count_ad}')

            if not update and not test_conn:
                if first_page and not cat.process_parse_url:  # Переход на след. страницу.
                    try:
                        cat.process_parse_url = driver.current_url
                        WebDriverWait(driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, category['next_page']))).click()
                        first_page = False
                        logger.info('First page Next Page')
                    except Exception as ex:
                        logger.exception('\n---------------------------------------------------------------------------'
                                         f'\nException in parse_web_page first_page -> next_page element not located {ex}'
                                         f'\nRaise IndexError -> {category["name"]}'
                                         '\n---------------------------------------------------------------------------')
                        raise IndexError
                else:
                    try:
                        next_page = WebDriverWait(driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, category['next_page'])))

                    except Exception as ex:
                        logger.exception('\n--------------------------------------------------------------------------'
                                         f'\nException in parse_web_page -> Error in next_page, element not located {ex}'
                                         f'\nCategory -> {category["name"]}'
                                         '\n--------------------------------------------------------------------------')
                        raise IndexError
                    else:
                        cat.process_parse_url = driver.current_url
                        cat.count_ad = count_ad
                        cat.save(update_fields=['process_parse_url', 'count_ad'])
                        if page_number == 380:
                            # Перезапуск парсера во избежание
                            # большого потребления памяти chrome.
                            logger.error(f'Max page achieved. Reschedule parser {cat.name}')
                            raise IndexError
                        next_page.click()
                        logger.info('Next Page')
                        page_number += 1
                        logger.info(f'PAGE NUMBER {page_number}')
            else:
                return

    except IndexError as ex:
        # Доп. проверка что парсер дошел до конца категории объявлений
        if count_ad >= count_ads:
            logger.info(f'Всего объявлений: {count_ads}')
            cat.process_parse_url = None
            cat.count_ad = 0
            cat.save(update_fields=['process_parse_url', 'count_ad'])
            logger.exception('\n---------------------------------------------'
                             f'\nExcept IndexError in parse_web_page func: {ex}'
                             '\n---------------------------------------------')
            return True, item_state
        else:
            logger.info(f'Всего объявлений: {count_ads}')
            logger.exception('\n--------------------------------------------------------------------------------------'
                             f'\nException in parse_web_page -> Error in IndexError > (count_ad) condition not pass {ex}'
                             f'\nRESCHEDULE parse_web_page -> {category["name"]}'
                             '\n--------------------------------------------------------------------------------------')
            get_all_data_in_category(category=category, cat_id=cat_id, priority=1)
            return False, item_state

    except Exception as ex:
        driver.close()
        driver.quit()
        time.sleep(2)
        logger.exception('\n---------------------------------------------------------'
                         f'\nException in parse_web_page func, Global Exception -> {ex}'
                         '\n---------------------------------------------------------')
        return False, item_state


def update_data(data, cat_id: int, is_search_items: bool, search_items):
    """
    Функция ищет распарсенный объект в бд по уникальному id товара,
    если не находит, сохранет его, иначе обновляет данные товара
    """
    res = convert_price_str_to_int(data)

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
        logger.info('Update_data save new_price success')

    obj.title = res['title']
    obj.date = res['date']
    obj.deleted = False
    obj.state = res['item_state']
    obj.time_update = timezone.now()
    obj.photo_url = res['photo']
    obj.save()
    logger.info('Update_data Update success')


def convert_price_str_to_int(data: dict[str, any]):
    """ Преобразует price и item_id в коллекции к int """
    if isinstance(data['price'], str) and isinstance(data['id_item'], str):
        price = ''.join(data['price'].strip(". pр").split())
        try:
            data['price'] = int(price)  # преобразуем в число или возвращаем 0 если цена "Договорная"
            try:
                data['id_item'] = int(data['id_item'])
            except ValueError as ex:
                logger.error(f'{data["id_item"]} Ошибка формата входных данных: {ex}')
        except ValueError:
            data['price'] = 0
    return data


def save_data(data: Dict[str, any], cat_id: int, is_search_items: bool, search_items):
    """ Сохраняет распарсенные данные в бд """
    try:
        obj = KufarItems.objects.create(base_price=data['price'], cat_id=cat_id, city=data['city'],
                                        date=data['date'], id_item=data['id_item'], state=data['item_state'],
                                        title=data['title'], photo_url=data['photo'], url=data['url'],
                                        )
        if is_search_items:  # Если прустствует запрос поиска товара в данной категории
            send_users_msg_search_items(search_items, obj=obj)
    except Exception as ex:
        logger.exception('\n--------------------------------'
                         f'\nException in save_data func: {ex}'
                         '\n--------------------------------')
        logger.info('Save_data Create FAIL')
    else:
        logger.info('Save_data Create Success')


def update_sold_items_in_category(cat_id: int):
    """
    Обновляет статус продано или нет товара в бд по временной дельте.
    Если товар не обновлялся более 5 часов считаем его проданным
    Если товар был продан в промежутке между обновлениями, его статус time_update = null
    сохраниться, считаем его проданным
    """

    delta = timezone.now() - timedelta(hours=5)
    qs1 = KufarItems.objects.filter(cat_id=cat_id,
                                    deleted=False,
                                    time_update__lt=delta)
    qs2 = KufarItems.objects.filter(cat_id=cat_id,
                                    deleted=False,
                                    time_create__lt=delta,
                                    time_update__isnull=True)
    qs = qs1 | qs2
    if qs.exists():
        send_users_msg_sold_items(qs)
        qs.update(deleted=True)
        logger.info(f'Update_sold_items_in_category SUCCESS, Delta {delta}')
    else:
        logger.info('Update_sold_items_in_category FALSE, no one obj in QuerySet')


def send_users_msg_sold_items(qs):
    """ Отправляем сообщение пользователю/ям что объект, добавленный в избранное, продан """
    qs_fav = qs.filter(in_favorites=True)
    if qs_fav.exists():
        for obj in qs_fav:
            try:
                send_users_msg_fav_items(obj, sold=True)
                obj.save(update_fields=['in_favorites'])
                logger.info('Send_users_msg_sold_items Success')
            except Exception as ex:
                logger.exception('\n-------------------------------------------'
                                 f'\nException in send_users_msg_sold_items: {ex}'
                                 '\n-------------------------------------------')


def send_users_msg_fav_items(obj, update=False, sold=False):
    """
    Отправляем сообщение пользователю/ям что у объекта,
    добавленного в избранное, изменилась цена или он продан.
    """

    try:
        for pk in FavoritesItems.objects.filter(pk_item=obj.pk):
            send_message(pk.bot_user.telegram_id, obj=obj, update_fav_message=update, sold_item_message=sold)
            logger.info('Send_message SUCCESS in send_user_msg_fav_items func')
    except Exception as ex:
        logger.exception('\n---------------------------------------------------------'
                         f'\nException in send_users_msg_fav_items (send_message): {ex}'
                         '\n---------------------------------------------------------')


def send_users_msg_search_items(search_items, obj):
    """
    Отправляем сообщение пользователю/ям что у найден товар, добавленный в поиск
    """

    for obj_search in search_items:
        find_status = [False, False, False]
        try:
            if obj_search.title:
                res = []
                search_title = obj_search.title.lower().split()
                if len(search_title) > 1:
                    obj_title = obj.title.lower().split()
                    for x in search_title:
                        if x.isdigit():
                            stat = [True if c == x else False for c in obj_title]
                            res.append(True if any(stat) else False)

                        elif x in obj.title.lower():
                            res.append(True)
                        else:
                            res.append(False)
                    if all(res):
                        find_status[0] = True
                elif search_title[0] in obj.title.lower():
                    find_status[0] = True
                else:
                    find_status[0] = False
            else:
                find_status[0] = True
        except Exception as ex:
            logger.exception('\n--------------------------------------------------------'
                             f'\nException in send_usr_msg_search_items step (title): {ex}'
                             '\n--------------------------------------------------------')
        try:
            if obj_search.min_price and obj_search.max_price:
                if obj_search.min_price <= obj.base_price <= obj_search.max_price:
                    find_status[1] = True
            else:
                find_status[1] = True
        except Exception as ex:
            logger.exception('\n--------------------------------------------------------'
                             f'\nException in send_usr_msg_search_items step (price): {ex}'
                             '\n--------------------------------------------------------')
        try:
            if obj_search.city:
                if obj_search.city in obj.city:
                    find_status[2] = True
            else:
                find_status[2] = True
        except Exception as ex:
            logger.exception('\n-------------------------------------------------------'
                             f'\nException in send_usr_msg_search_items step (city): {ex}'
                             '\n-------------------------------------------------------')
        if all(find_status):
            try:
                send_message(user_id=obj_search.bot_user.telegram_id, obj=obj, search_item_message=True)
            except Exception as ex:
                logger.exception('\n------------------------------------------------------------------'
                                 f'\nException in send_users_msg_search_items step (send_message):  {ex}'
                                 '\n------------------------------------------------------------------')
