import os
import re

import pandas

import file_utils as fu
import get_proxy
import html_utils as hu


def get_links():
    brands = hu.get_brands_link(hu.get_html('http://www.profit-msk.ru/goods/zip/index.html'))
    for brand in brands:
        models = hu.get_models_link(hu.get_html(brand))

        df = pandas.DataFrame(models)
        df.to_csv('models', index=False, mode='a', header=False, sep=";")


def parser_site():
    # data = pandas.read_csv('models', sep=';')
    data = fu.load_file('models')
    # models = data.values.tolist()
    for model in data:
        if model:
            proxy = {'http': 'http://' + get_proxy.get_proxies_list()}
            useragent = {'User-Agent': get_proxy.get_useregent_list()}

            soup = hu.get_html(model[1], useragent, proxy)

            if soup == 404:
                continue

            brand_name, model_name, device_spec, device_data = hu.model_parser(soup, model[0])

            model_name = re.sub('/', ' ', model_name)
            base_dir = os.path.dirname(__file__)
            base_dir = f'{base_dir}\\parse\\{brand_name}'
            if not os.path.exists(base_dir):
                os.mkdir(base_dir)

            df = pandas.DataFrame(device_spec)
            df.to_csv(f'{base_dir}\\{model_name}_spec.csv', index=False, header=False, sep=";")
            df = pandas.DataFrame(device_data)
            df.to_csv(f'{base_dir}\\{model_name}_parts.csv', index=False, header=False, sep=";")