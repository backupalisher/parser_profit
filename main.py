import os
import re
import glob
import time
import pandas
import get_proxy
import html_utils as hu
import file_utils as fu

import db_utils as db


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


def load_files_list():
    path = r'parse'
    d = []
    for root, dirs, files in os.walk(path):
        for file in files:
            d.append([f'{root}\\{file}', file])
    return d


def add_db():
    # data = pandas.read_csv('parse\\brother\\Brother DCP-110C_parts.csv', sep=';', header=None)
    # print(data)
    # parts = data.values.tolist()
    # for p in parts:
    #     print(p)
    files = load_files_list()

    for file in files:
        file_name = re.sub(r'(^.*\\)|(MFP)$|(\s{2,})|(_spec).+$|(_part).+$', '', file[1])
        brand_name = re.sub(r'\s.*$', '', file_name)
        brand_id = db.get_brand_id(brand_name)
        if brand_id < 1:
            print(brand_name)
            df = pandas.DataFrame([brand_name])
            df.to_csv('no_model', index=False, mode='a', header=False, sep=";")

        model_id = db.get_model_id(file_name)
        if model_id < 1:
            model = re.search('^.*\d', file_name)
            if model:
                model_id = db.get_model_id(model.group(0))
                if model_id < 1:
                    model_id = db.insert_model(model.group(0), brand_id)
                    spr_details_id = db.insert_spr_details(model.group(0))
                    db.link_models_spr_details(model_id, spr_details_id)

        if model_id > 0 and re.search('_parts', file[1]):
            path = re.sub(r'(parse\\)|(_parts)|(\.csv)', '', file[1])
            brand_name = re.sub(r'\s.*$', '', path).lower()
            path = f'{brand_name}/{path}.jpg'
            db.update_model_image(path, model_id)

        if model_id < 1:
            df = pandas.DataFrame([file_name])
            df.to_csv('no_model', index=False, mode='a', header=False, sep=";")
            print('', end='\n')
            print(file_name, model_id, end='\n')
        elif re.search(r'(_part)', file[1]):
            data = []
            try:
                data = pandas.read_csv(file[0], sep=';', header=None).values.tolist()
            except:
                pass

            print('', end='\n')
            print(file_name, model_id, end='\n')

            if data:
                for d in data:
                    det = re.sub(r'.*(\s-\s)|^\([^)]*\)', '', d[2])
                    if re.search(r'Ресурс:', det):
                        det = re.sub(r'\([^)]*\)', '', det)

                    print(f'\r', d[0], d[1], det, end='')
                    partcode_id = db.get_partcode_id(d[1])

                    if partcode_id > 0:
                        db.update_module_name(d[0], partcode_id)
                        db.update_spr_detail_name(d[1], det)

                    if model_id > 0 and partcode_id > 0:
                        db.insert_partcode_model_analogs(model_id, partcode_id)

                    # part = re.sub(r'.*(\s-\s)', '', d[2])
                    # part = re.search(r'^\([^)]*\)', part)
                    # if part:
                    #     part = re.sub('\(|\)', '', part.group(0))
                    #     print(part)

                    if d[3]:
                        d3 = re.sub(r'\[|\]|\'', '', d[3])
                        d3 = d3.split(',')
                        for i, n in enumerate(d3):
                            a_model_id = db.get_model_id(n.strip())
                            if partcode_id > 0:
                                if a_model_id < 1:
                                    a_brand_name = re.sub(r'\s.*$', '', n.strip())
                                    a_brand_id = db.get_brand_id(a_brand_name)

                                    a_model_id = db.insert_model(n.strip(), a_brand_id)
                                    spr_details_id = db.insert_spr_details(n.strip())
                                    db.link_models_spr_details(a_model_id, spr_details_id)

                            if a_model_id > 0 and partcode_id > 0:
                                db.insert_partcode_model_analogs(a_model_id, partcode_id)

                    if d[4] is float("nan"):
                        path = re.sub(r'E:\\Projects\\PycharmProjects\\parser_profit\\images\\', '', d[4])
                        if model_id > 0 and path:
                            db.update_partcode_image(path, model_id)


def main():
    add_db()


if __name__ == '__main__':
    main()
