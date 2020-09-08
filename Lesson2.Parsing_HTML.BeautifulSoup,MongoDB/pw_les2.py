import requests
import pandas as pd
from bs4 import BeautifulSoup as bs

def restruct_compensation(compensation: str):
    """Функция обработки укзателя зарплаты для
    разделения на минимальную, максимальную 
    и денежную единицу измерения 
    с использованием регулярных выражений
    (функция содержит import re)

    Args:
        compensation (str):
        тестировалось на выражениях:
            ['30000-70000 руб.', 'до 96000 руб.', 'от 150000 руб.',
             'от 150000 руб. до 200000 руб.', '200000-450000 KZT',
             '2500-4000 USD', '3000000'
            ]

    Returns:
        result (dict):
            result.keys(): ['min_compensation',
                            'max_compensation',
                            'currency_compensation'
                           ]
    """
    import re
    if compensation.isdigit():
        result = {'min_compensation' : int(compensation),
                  'max_compensation': int(compensation),
                  'currency_compensation' : None
                 }
        return result

    elif re.search(r'^до',compensation):
        re_compensation = re.search(r'().*?(\d{1,}).*?(\w{3}).*?', compensation)
    elif '-'in compensation or ('от' in compensation and 'до' in compensation):
        re_compensation = re.search(r'.*?(\d{1,}).*?(\d{1,}).*?(\w{3}).*?', compensation)
    elif 'от' in compensation and 'до' not in compensation:
        re_compensation = re.search(r'.*?(\d{1,}).*?()(\w{3}).*?', compensation)
    
    result = {'min_compensation' : re_compensation.group(1),
              'max_compensation': re_compensation.group(2),
              'currency_compensation' : re_compensation.group(3)
             }
    
    return result



def parser_vacancy_item(required_vacancy:'bs4.element.Tag', website: str, parser_params: dict):
    """[summary]

    Args:
        required_vacancy (bs4.element.Tag): [description]
        website (str): [https://spb.hh.ru or https://www.superjob.ru]
        parser_params (dict): 
        [Описание для hh.ru]: {'vacancy_header_blok' : ['div', 'class', 'vacancy-serp-item__row_header'],
                               'vacancy_info' : ['div', 'class', 'vacancy-serp-item__info'],
                               'vacancy_sidebar_compensation' : ['div', 'class', 'vacancy-serp-item__sidebar'],
                               'vacancy_link' : ['a', 'class', 'bloko-link'],
                               'company_metainfo' : ['div', 'class', 'vacancy-serp-item__meta-info'],
                               'company_link' : ['a', 'data-qa', 'vacancy-serp__vacancy-employer'],
                               'company_name' : ['a', 'data-qa', 'vacancy-serp__vacancy-employer'],
                               'company_location' : ['span', 'data-qa', 'vacancy-serp__vacancy-address']
                              }  

    Returns:
        [type]: [description]
    """
    vacancy_data={}
    vacancy_data['website'] = website
    vacancy_header_blok = required_vacancy.find(parser_params['vacancy_header_blok'][0],
                                                {parser_params['vacancy_header_blok'][1]:
                                                 parser_params['vacancy_header_blok'][2]})
    vacancy_info = vacancy_header_blok.find(parser_params['vacancy_info'][0],
                                            {parser_params['vacancy_info'][1]:
                                             parser_params['vacancy_info'][2]})
    vacancy_sidebar_compensation = vacancy_header_blok.find(parser_params['vacancy_sidebar_compensation'][0],
                                                            {parser_params['vacancy_sidebar_compensation'][1]:
                                                             parser_params['vacancy_sidebar_compensation'][2]})
    vacancy_name = vacancy_info.getText()
    vacancy_link = vacancy_info.find(parser_params['vacancy_link'][0],
                                     {parser_params['vacancy_link'][1]
                                     : parser_params['vacancy_link'][2]}).get('href')
    
    vacancy_data['name'] = vacancy_name
    
    if website == 'hh.ru':
        vacancy_data['link'] = vacancy_link
        website = 'https://' + website
        company_metainfo = required_vacancy.find_all(parser_params['company_metainfo'][0],
                                                     {parser_params['company_metainfo'][1]
                                                     :parser_params['company_metainfo'][2]})
    elif website == 'superjob.ru':
        website = 'https://www.' + website
        vacancy_data['link'] = website + vacancy_link
        company_metainfo = required_vacancy.find(parser_params['company_metainfo'][0],
                                                 {parser_params['company_metainfo'][1]
                                                 :parser_params['company_metainfo'][2]})
        company_metainfo = company_metainfo.find_all(parser_params['company_metainfo'][3],
                                                     {parser_params['company_metainfo'][4]
                                                     :parser_params['company_metainfo'][5]})
        
    try:
        company_link = company_metainfo[0].find(parser_params['company_link'][0],
                                                {parser_params['company_link'][1]
                                                : parser_params['company_link'][2]}).get('href')
        vacancy_data['company_link'] = website + company_link 
        
    except:
        vacancy_data['company_link'] = None        
    try: 
        company_name = company_metainfo[0].find(parser_params['company_name'][0],
                                                {parser_params['company_name'][1]
                                                : parser_params['company_name'][2]}).getText()
        vacancy_data['company_name'] = company_name
    except:
        vacancy_data['company_name'] = None
    try:
        company_location = company_metainfo[1].find(parser_params['company_location'][0],
                                                    {parser_params['company_location'][1]
                                                    : parser_params['company_location'][2]}).getText()
        vacancy_data['company_location'] = company_location
    except:
        vacancy_data['company_location'] = None
    try:
        vacancy_compensation = vacancy_sidebar_compensation.getText()
        vacancy_compensation = vacancy_compensation.replace('\xa0', '')
        vacancy_compensation = restruct_compensation(vacancy_compensation)
        vacancy_data['min_compensation'] = vacancy_compensation['min_compensation']
        vacancy_data['max_compensation'] = vacancy_compensation['max_compensation']
        vacancy_data['currency_compensation'] = vacancy_compensation['currency_compensation']
    except:
        vacancy_data['min_compensation'] = None
        vacancy_data['max_compensation'] = None
        vacancy_data['currency_compensation'] = None
            
    return vacancy_data


def get_pars_response(website: str, required_vacancy: str, headers: dict, num_area: int = 0, page:str = ''):
    if website == 'hh.ru':
        main_link = 'https://hh.ru'
        second_link = '/search/vacancy'
        params_link =  {'fromSearchLine': 'true',
                        'L_is_autosearch':'false',
                        'area': num_area,
                        'enable_snippets':'true',
                        'salary': '',
                        'st':'searchVacancy',
                        'text': required_vacancy,
                        'page': page}
    elif website == 'superjob.ru':
        main_link = 'https://www.superjob.ru'
        second_link ='/vacancy/search/'
        params_link = {'keywords': required_vacancy,
                       'noGeo': '1',
                       'page': page
                      }
    
    full_link = main_link + second_link
    return requests.get(full_link, params=params_link, headers=headers)


def get_vacancies(website: str, required_vacancy: str, headers: dict, parser_params: dict, num_area: int = 0):
    """[summary]

    Args:
        website (str): 'hh.ru', 'superjob.ru'
        required_vacancy (str): [description]
        num_area (int, optional): [description]. Defaults to 0.
        parser_params (dict) = {'pages_blok': ['div', 'data-qa', 'pager-block'],
                                'pages_list': ['a', 'class', 'bloko-button'],
                                'vacancies_serp': ['div', 'class', 'vacancy-serp', 'vacancy-serp-item'],
                                'vacancy_header_blok' : ['div', 'class', 'vacancy-serp-item__row_header'],
                                'vacancy_info' : ['div', 'class', 'vacancy-serp-item__info'],
                                'vacancy_sidebar_compensation' : ['div', 'class', 'vacancy-serp-item__sidebar'],
                                'vacancy_link' : ['a', 'class', 'bloko-link'],
                                'company_metainfo' : ['div', 'class', 'vacancy-serp-item__meta-info'],
                                'company_link' : ['a', 'data-qa', 'vacancy-serp__vacancy-employer'],
                                'company_name' : ['a', 'data-qa', 'vacancy-serp__vacancy-employer'],
                                'company_location' : ['span', 'data-qa', 'vacancy-serp__vacancy-address']
                               } - for hh.ru
        parser_params (dict) = {'vacancy_header_blok' : ['div', 'class', 'jNMYr GPKTZ _1tH7S'],
                                'vacancy_info' : ['div', 'class', '_3mfro PlM3e _2JVkc _3LJqf'],
                                'vacancy_sidebar_compensation' : ['span', 'class', '_1OuF_ _1qw9T f-test-text-company-item-salary'],
                                'vacancy_link' : ['a', 'target', '_blank'],
                                'company_metainfo' : ['div', 'class', '_3_eyK _3P0J7 _9_FPy', 'div', 'class', '_2g1F-'],
                                'company_link' : ['a', 'target', '_self'],
                                'company_name' : ['a', 'target', '_self'],
                                'company_location' : ['span', 'class', '_3mfro f-test-text-company-item-location _9fXTd _2JVkc _2VHxz'],
                                'pages_blok': ['div', 'class', '_3zucV L1p51 undefined _1Fty7 _2tD21 _3SGgo'],
                                'pages_list': ['a', 'target', '_self'],
                                'vacanies_serp': ['div', 'class', '_1ID8B', 'Fo44F QiY08 LvoDO']
                               } - for superjob.ru

    Returns:
        [type]: [description]
    """
    
    vacancies_data = []
    response_page = get_pars_response(website , required_vacancy , headers, num_area = num_area)
    if response_page.ok:
        soup = bs(response_page.text,'html.parser')
        try:
            pages_blok = soup.find(parser_params['pages_blok'][0],
                                   {parser_params['pages_blok'][1]
                                   : parser_params['pages_blok'][2]})
            pages_list = pages_blok.find_all(parser_params['pages_list'][0],
                                             {parser_params['pages_list'][1]
                                             : parser_params['pages_list'][2]})
            last_page_number = int(pages_list[-2].getText())
        except:
            last_page_number = 1
        

    for page in range(last_page_number):
        response_page = get_pars_response(website , required_vacancy , headers, num_area = num_area, page=page)
        if response_page.ok:
            soup = bs(response_page.text,'html.parser')
    
            vacancies_serp = soup.find(parser_params['vacancies_serp'][0],
                                       {parser_params['vacancies_serp'][1]
                                       : parser_params['vacancies_serp'][2]})
            vacancies_serp = vacancies_serp.find_all(parser_params['vacancies_serp'][0],
                                                     {parser_params['vacancies_serp'][1]
                                                     : parser_params['vacancies_serp'][3]})
            for vacancy in vacancies_serp:
                vacancies_data.append(parser_vacancy_item(vacancy,parser_params=parser_params, website=website))
    
    return vacancies_data


def get_vacancies_list(website_list: list ,
                       required_vacancy: str,
                       headers: dict,
                       num_area: int = 0):
    """Функция преобразования в датафрейм полученых вакансий  с сайтов:
        'hh.ru', 'superjob.ru'

    Args:
        website_list (list): ['hh.ru', 'superjob.ru']
        required_vacancy (str): [description]
        headers (dict): [description]
        num_area (int, optional): [description]. Defaults to 0.

    Returns:
        vacancies_data (list): [description]
    """
   
    vacancies_data = []
    hh_parser_params = {'pages_blok': ['div', 'data-qa', 'pager-block'],
                        'pages_list': ['a', 'class', 'bloko-button'],
                        'vacancies_serp': ['div', 'class', 'vacancy-serp', 'vacancy-serp-item'],
                        'vacancy_header_blok' : ['div', 'class', 'vacancy-serp-item__row_header'],
                        'vacancy_info' : ['div', 'class', 'vacancy-serp-item__info'],
                        'vacancy_sidebar_compensation' : ['div', 'class', 'vacancy-serp-item__sidebar'],
                        'vacancy_link' : ['a', 'class', 'bloko-link'],
                        'company_metainfo' : ['div', 'class', 'vacancy-serp-item__meta-info'],
                        'company_link' : ['a', 'data-qa', 'vacancy-serp__vacancy-employer'],
                        'company_name' : ['a', 'data-qa', 'vacancy-serp__vacancy-employer'],
                        'company_location' : ['span', 'data-qa', 'vacancy-serp__vacancy-address']
                       } 
    sj_parser_params = {'company_location' : ['span', 'class', '_3mfro f-test-text-company-item-location _9fXTd _2JVkc _2VHxz'],
                        'pages_blok': ['div', 'class', '_3zucV L1p51 undefined _1Fty7 _2tD21 _3SGgo'],
                        'pages_list': ['a', 'target', '_self'],
                        'vacancies_serp': ['div', 'class', '_1ID8B', 'Fo44F QiY08 LvoDO'],
                        'vacancy_header_blok' : ['div', 'class', 'jNMYr GPKTZ _1tH7S'],
                        'vacancy_info' : ['div', 'class', '_3mfro PlM3e _2JVkc _3LJqf'],
                        'vacancy_sidebar_compensation' : ['span', 'class', '_1OuF_ _1qw9T f-test-text-company-item-salary'],
                        'vacancy_link' : ['a', 'target', '_blank'],
                        'company_metainfo' : ['div', 'class', '_3_eyK _3P0J7 _9_FPy', 'div', 'class', '_2g1F-'],
                        'company_link' : ['a', 'target', '_self'],
                        'company_name' : ['a', 'target', '_self']
                       }
    for website in website_list:
        if website == 'hh.ru':
            parser_params = hh_parser_params
        elif  website == 'superjob.ru':
            parser_params = sj_parser_params
        vacancies_data.extend(get_vacancies(website, required_vacancy, headers, parser_params, num_area=num_area))
    return vacancies_data
    

required_vacancy = 'Data Scientist'
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
           'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
          }
vacancies = get_vacancies_list(website_list=['hh.ru', 'superjob.ru'],
                              required_vacancy=required_vacancy,
                              headers=headers)
df = pd.DataFrame(vacancies)
print(vacancies[:3])