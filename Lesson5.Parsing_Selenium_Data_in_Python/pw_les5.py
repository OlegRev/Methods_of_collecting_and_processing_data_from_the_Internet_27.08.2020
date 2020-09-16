"""1) Написать программу, которая собирает входящие письма
из своего или тестового почтового ящика и сложить данные
о письмах в базу данных (от кого, дата отправки,
тема письма, текст письма полный)
    Логин тестового ящика: study.ai_172@mail.ru
    Пароль тестового ящика: NextPassword172
2) Написать программу, которая собирает «Хиты продаж»
с сайта техники mvideo и складывает данные в БД.
Магазины можно выбрать свои.
Главный критерий выбора:
динамически загружаемые товары
"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
import time
chrome_options = Options()
chrome_options.add_argument('start-maximized')


def get_element(driver, class_name, text=True):
    if text:
        return WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME , class_name))).text
    else:
        return WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME , class_name)))

def get_element_by_css(driver, css_selector, text=False):
    if text:
        return WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR , css_selector))).text
    else:
        return WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR , css_selector)))


def get_info_email(driver):
    """Функция сбора данных о письме для mail.ru

    Args:
        driver (selenium.webdriver.chrome.webdriver.WebDriver): 

    Returns:
        dict: Информацио о сообщении
            (тема письма, от кого, дата отправки,текст письма полный)
    """
    info_email={}
    info_email['subject_messege'] = get_element(driver, class_name="thread__subject")
    info_email['contact_messege'] = get_element(driver, class_name="letter-contact")
    info_email['date_messege'] = get_element(driver, class_name="letter__date")
    info_email['text_content_mesege'] = get_element(driver, class_name="letter-body__body")
    
    return info_email

    
def get_info_m_email(driver):
    """Функция сбора данных о письме для mail.ru

    Args:
        driver (selenium.webdriver.chrome.webdriver.WebDriver): 

    Returns:
        dict: Информацио о сообщении
            (тема письма, от кого, дата отправки,текст письма полный)
    """
    info_email={}
    info_email['subject_messege'] = get_element(driver, class_name="readmsg__theme")
    info_email['contact_messege'] = get_element(driver, class_name="readmsg__addressed-word")
    info_email['date_messege'] = get_element(driver, class_name="readmsg__mail-date")
    info_email['text_content_mesege'] = get_element_by_css(driver, 'div[id="readmsg__body"]', text=True)  
    return info_email

# 1
DATABASE = 'messeges_db'
client = MongoClient('127.0.0.1:27017',
                     username='admin_messeges',
                     password='password_db',
                     authSource='messeges_db',
                     authMechanism='SCRAM-SHA-1')
db = client[DATABASE]
collection = db['mail_ru']


driver = webdriver.Chrome('/home/oleg_rev/education/Faculty_of_Artificial_Intelligence/'
                          'Methods_of_collecting_and_processing_data_from_the_Internet/'
                          'Lesson5.Parsing_Selenium_Data_in_Python/chromedriver',options=chrome_options)
main_links = {"mobile_link": "https://m.mail.ru/login", "desktop_link": "https://mail.ru/"}

main_link = main_links["mobile_link"]
driver.get(main_link)

if main_link == main_links['desktop_link']:
    login = driver.find_element_by_id('mailbox:login-input')
    login.send_keys('study.ai_172@mail.ru')
    login.send_keys(Keys.RETURN)

    time.sleep(3)
    passw = driver.find_element_by_id('mailbox:password-input')
    passw.send_keys('NextPassword172')
    passw.send_keys(Keys.RETURN)

    mesege_0 = get_element(driver, class_name="llc", text=False) 
    mesege_0.click()

    while WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-title-shortcut="Ctrl+↓"]'))):
        
        collection.insert_one(get_info_email(driver=driver))
        next_email_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-title-shortcut="Ctrl+↓"]')))
        next_email_button.click()

elif main_link == main_links['mobile_link']:

    login = get_element_by_css(driver, 'input[name="Login"]')
    login.send_keys('study.ai_172@mail.ru')
    passw = get_element_by_css(driver, 'input[name="Password"]')
    passw.send_keys('NextPassword172')
    passw.send_keys(Keys.RETURN)

    mesege_0 = get_element_by_css(driver, 'a[class="messageline__link"]')
    mesege_0.click()

    while get_element_by_css(driver, 'a[class="readmsg__text-link"]'):
        
        collection.insert_one(get_info_m_email(driver=driver))
        next_email_button = get_element_by_css(driver, 'div[class="readmsg__horizontal-block__right-block"]')
        next_email_button.click()
    else:
        driver.close()
    
# 2   
DATABASE = 'products_db'
client = MongoClient('127.0.0.1:27017',
                     username='admin_products',
                     password='password_db',
                     authSource='products_db',
                     authMechanism='SCRAM-SHA-1')
db = client[DATABASE]
collection = db['mvideo_ru']


chrome_options = Options()
chrome_options.add_argument('start-maximized')
   

driver = webdriver.Chrome('/home/oleg_rev/education/Faculty_of_Artificial_Intelligence/'
                          'Methods_of_collecting_and_processing_data_from_the_Internet/'
                          'Lesson5.Parsing_Selenium_Data_in_Python/chromedriver',options=chrome_options)


driver.get("https://www.mvideo.ru/")
# bestsellers = get_element_by_xpath(driver, '//div[contains(text(), "Хиты продаж")]/../..//following-sibling::div[@class="gallery-layout sel-hits-block "]')
next_button = get_element_by_xpath(driver, '//div[contains(text(), "Хиты продаж")]/../..//following-sibling::div[@class="gallery-layout sel-hits-block "]//a[@class="next-btn sel-hits-button-next"]')
pages = driver.find_elements_by_xpath('//div[contains(text(),  "Хиты продаж")]/../..//following-sibling::div[@class="gallery-layout sel-hits-block "]//div[@class="carousel-paging"]/a[@href="#"]')

for page in range(len(pages)):
    sleep(5)
    
    next_button.click()
else:
    data_prods = []
    description_prods = {}
    description_prods['name'] = driver.find_elements_by_xpath('//div[contains(text(), "Хиты продаж")]/../..//following-sibling::div[@class="gallery-layout sel-hits-block "]//h4')
    description_prods['link'] = driver.find_elements_by_xpath('//div[contains(text(), "Хиты продаж")]/../..//following-sibling::div[@class="gallery-layout sel-hits-block "]//a[@class="sel-product-tile-title"]')
    description_prods['price'] = driver.find_elements_by_xpath('//div[contains(text(), "Хиты продаж")]/../..//following-sibling::div[@class="gallery-layout sel-hits-block "]//div[@class="c-pdp-price__current"]')
    for itm in range(len(description_prods['name'])):
        info_prod = {} 
        info_prod['name'] = description_prods['name'][itm].get_attribute('title')
        info_prod['link'] = description_prods['link'][itm].get_attribute('href')
        info_prod['price'] = description_prods['price'][itm].text
        collection.insert_one(info_prod)
        data_prods.append(info_prod)
        
    