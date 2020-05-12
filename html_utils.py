import os
import re
import time
from time import sleep
from random import uniform
import shutil
import requests
from bs4 import BeautifulSoup as bs


def get_html(url, useragent=None, proxy=None):
    t = uniform(3, 8)
    sleep(t)
    session = requests.Session()
    request = session.get(url=url, headers=useragent, proxies=proxy)
    if request.status_code == 200:
        soup = bs(request.text, 'lxml')
        return soup
    else:
        print("Error " + str(request.status_code))
        return request.status_code


def parse(soup):
    data = []
    contents = soup.findAll(None, class_="post-title-link")
    for i, content in enumerate(contents):
        text = content.text
        href = content['href']
        data.append([
            i,
            text,
            href,
        ])

    return data


def get_brands_link(soup):
    brands_link = []
    brands = soup.find_all('div', class_='spotlight')
    for brand in brands:
        href = re.sub(r'(^..+?(?==)..)|(.$)', '', brand['onclick'])
        brands_link.append(
            href
        )
    return brands_link


def get_models_link(soup):
    models_link = []
    models = soup.find_all('div', class_='tbltsttt')
    for model in models:
        href = re.sub(r'(^..+?(?==)..)|(.$)', '', model['onclick'])
        brand_name = re.search(r'^.+?(?=/).', href).group(0)
        brand_name = re.sub(r'\W', '', brand_name)
        models_link.append([
            brand_name,
            'https://profit-msk.ru' + href,
        ])
    return models_link


def model_parser(soup, brand_name):
    full_data = soup.find('div', class_='full-article')
    model_name = full_data.find('span').text
    print(model_name)
    img_path = ''
    try:
        img_url = full_data.find('a', title=model_name)['href']
        img_path = save_img('https://profit-msk.ru' + img_url, brand_name, model_name)
    except:
        pass

    table_body = full_data.find_next('table')

    device_spec = [img_path]
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [re.sub(r'\n', '', ele.text.strip()) for ele in cols]
        for i, col in enumerate(cols[2:]):
            if i % 2 == 0:
                device_spec.append([col, cols[i + 3]])

    data = full_data.find('div', class_='jwts_tabbertab')
    tables = data.find_all('table', cellspacing='0')
    device_data = []
    module_name = ''
    part_code = ''
    part_name = ''

    for table in tables[1:]:
        models_list = []
        img_path = ''
        try:
            module_name = table.find('td', attrs={'class': 'zip_t_caption brdimg', 'colspan': '4'}).text
            continue
        except:
            pass
        try:
            part_code = table.find('span', class_='pbld').text
            part_names = table.find_all('td', class_='brdimg')
            part_name = re.sub(r'^\n', '', part_names[1].text).strip()
        except:
            pass
        try:
            img_url = full_data.find('a', title=part_code)['href']
            img_path = save_img('https://profit-msk.ru' + img_url, brand_name, part_code)
        except:
            pass
        try:
            models = table.find_all('td', class_='tztdclass')
            for model in models[1:]:
                if model.text:
                    models_list.append(model.text)
        except:
            pass
        if module_name and part_code:
            device_data.append({
                'module': module_name,
                'part_code': part_code,
                'part_name': part_name,
                'models_list': models_list,
                'image': img_path
            })

    return brand_name, model_name, device_spec[1:], device_data


def save_img(url, brand_name, model_name):
    file_name = ''
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        timestamp = str(round(time.time()))

        base_dir = os.path.dirname(__file__)
        base_dir = f'{base_dir}\\images\\{brand_name}'
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
        file_name = f'{base_dir}\\{model_name}.jpg'

        with open(file_name, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

    return file_name
