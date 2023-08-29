from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent

# categories urls
categories = {'kufar_videocards': {
    'url': r"https://www.kufar.by/l/r~belarus?ar=&ot=1&query=%D0%B2%D0%B8%D0%B4%D0%B5%D0%BE%D0%BA%D0%B0%D1%80%D1%82%D1%8B&rgn=all",
    'wrapper': '//a[styles_wrapper__G_0_A]',
    'title': '//h1[styles_brief_wrapper__title__x59rm]',
    'price': '//span[styles_price--main__VMpTN]',
    'country-date': '//span[styles_brief_wrapper__date__FfOke]'},

    'kufar_notebooks': {'url': r"https://www.kufar.by/l/noutbuki?cmp=0&sort=lst.d",
                        'wrapper': '//a[@class="styles_wrapper__5FoK7"]',
                        # 'title': '//h3[@class="styles_title__F3uIe"]', # XPATH
                        'title': "styles_title__F3uIe",
                        # 'price': '//p[@class="styles_price__G3lbO"]', # XPATH
                        'price': 'styles_price__G3lbO',
                        # 'country-date': '//div[@class="styles_secondary__MzdEb"]', # XPATH
                        'country-date': "styles_secondary__MzdEb",
                        'next_page': '//a[@class="styles_link__8m3I9 styles_arrow__LNoLG"]',
                        'accept_button_class': "//button[@class='styles_button__oKUgO styles_secondary__MiBIC styles_submit_button__T_qS1']"}
}

# fake useragent
useragent = UserAgent()
# options
options = webdriver.ChromeOptions()
options.add_argument(f"--user-agent={useragent.random}")
# options.headless = True # Безоконный режим
options.add_argument("user-data-dir=C:\\profile")
options.add_argument("--start-maximized")
options.add_argument(f"--disable-blink-features=AutomationControlled")
# off errors in console
options.add_experimental_option('excludeSwitches', ['enable-logging'])

# driver
service = Service()
driver = webdriver.Chrome(service=service, options=options)
