import os
import re
import sys
from datetime import datetime

import pandas
from termcolor import colored

import db_utils as db


def query_yes_no(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:

        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def get_model(model_name, brand_id):
    model_name = re.sub(r'\([^)]*\)|\+|(^.*\\)|(MFP)$|(\s{2,})', '', model_name)
    model_id = db.get_model_id(model_name.replace('-', ''))
    if model_id < 1:
        model = re.search('.*\d', model_name)
        if model:
            model_id = db.get_model_id(model.group(0))
            if model_id < 1:
                print(colored(f'The {model_name} model is missing', 'magenta'))
                df = pandas.DataFrame([model_name])
                df.to_csv('no_model', index=False, mode='a', header=False, sep=";")
                model_id = 0
                # models = db.get_models(model.group(0))
                # if models:
                #     for v in models:
                #         print(v)
                # if query_yes_no(colored(f'Insert new model, {model_name}?', 'red'), 'no'):
                #     model_id = db.insert_model(model_name, brand_id)
                #     spr_details_id = db.insert_model_spr_details(model_name)
                #     db.link_models_spr_details(model_id, spr_details_id)
                # else:
                #     model_id = 0
    return model_id


def add_db():
    files = load_files_list()
    try:
        miss_files = pandas.read_csv('miss_models', sep=';', header=None)
        miss_files = miss_files.values.tolist()
    except:
        miss_files = []

    for file in files:
        miss_file = False
        for miss in miss_files:
            if re.search(fr'{miss[0]}', file[1]):
                miss_file = True
                break
        if miss_file:
            continue

        file_name = re.sub(r'(_spec).+$|(_part).+$', '', file[1])
        brand_name = re.sub(r'\s.*$', '', file_name)
        brand_id = db.get_brand_id(brand_name)
        if brand_id < 1:
            print(brand_name)
            df = pandas.DataFrame([brand_name])
            df.to_csv('no_model', index=False, mode='a', header=False, sep=";")

        model_id = get_model(file_name, brand_id)

        if model_id > 0 and re.search('_parts', file[1]):
            path = re.sub(r'(parse\\)|(_parts)|(\.csv)', '', file[1])
            brand_name = re.sub(r'\s.*$', '', path).lower()
            path = f'{brand_name}/{path}.jpg'
            db.update_model_image(path, model_id)

        if model_id < 1:
            df = pandas.DataFrame([file_name])
            df.to_csv('no_model', index=False, mode='a', header=False, sep=";")
            print('', end='\n')
            print(colored(file_name, 'blue'), colored(model_id, 'cyan'), end='\n')
        elif re.search(r'(_part)', file[1]):
            data = []
            try:
                data = pandas.read_csv(file[0], sep=';', header=None).values.tolist()
            except:
                pass

            print('', end='\n')
            print(colored(datetime.now().strftime("%X"), 'magenta'), colored(file_name, 'blue'),
                  colored(model_id, 'cyan'), end='\n')

            # HP Color LaserJet Enterprise Flow MFP M680dn
            if data:
                for d in data:
                    detail_option_id = 0
                    module_id = 0
                    spr_details_id = 0
                    detail_id = 0

                    det = re.sub(r'^.*([A-Za-z0-9])\w+.*-\s', '', d[2])
                    det = re.sub(r'^\([^)]*\)', '', det)
                    if re.search(r'Ресурс:', det):
                        res = re.search(r'(Ресурс:).+(стр.)', det).group(0)
                        res_id = db.get_option_id('Ресурс')
                        res_val_id = db.get_option_id(re.sub(r'[^\d]', '', res))
                        detail_option_id = db.insert_detail_options(res_id, res_val_id)

                        det = re.sub(r'\([^)]*\)|\'|\"|\`', '', det)
                    det = det.strip()

                    print(f'\r', colored(d[0], 'green'), colored(d[1], 'red'), colored(d[2], 'yellow'), end='')
                    partcode_id = db.get_partcode_id(d[1])

                    if partcode_id > 0:
                        # обновить нимаенование модуля в spr_detail
                        # не требуется, меняет не корректно, решил менять в ручную
                        # db.update_module_name(d[0], partcode_id)

                        # обновить нимаенование детали в spr_detail
                        db.update_spr_detail_name(d[1], det)
                    else:
                        # добавить модуль в spr_details (name)
                        # добавить парткод в partcode (code)
                        # добавить наименование детали в spr_details (name)
                        # добавить линковку в details (partcode_id, model_id, module_id, spr_detail_id)
                        module_id = db.insert_spr_modules(d[0].strip())
                        partcode_id = db.insert_partcodes(d[1])
                        spr_details_id = db.insert_detail_spr_details(det)

                        if partcode_id > 0 and model_id > 0 and module_id > 0 and spr_details_id > 0:
                            detail_id = db.link_part_model_module_spr(partcode_id, model_id, module_id, spr_details_id)

                    if model_id > 0 and partcode_id > 0:
                        # создть линковку парт кода и модели
                        db.link_partcode_model_analogs(model_id, partcode_id)

                    if partcode_id > 0 and model_id > 0 and module_id > 0 and spr_details_id > 0:
                        detail_id = db.link_part_model_module_spr(partcode_id, model_id, module_id, spr_details_id)

                    if detail_id > 0 and detail_option_id > 0:
                        db.link_detail_options(detail_id, detail_option_id)

                    # ищем и добавляем совместимые детали
                    part = re.sub(r'^.*([A-Za-z0-9])\w+.*-\s', '', d[2])
                    part = re.search(r'^\([^)]*\)', part)
                    if part:
                        part = re.sub('\(|\)', '', part.group(0))
                        if part:
                            s_partcode_id = db.insert_partcodes(d[1].strip())
                            if str(d[4]) != 'nan':
                                path = re.sub(r'E:\\Projects\\PycharmProjects\\parser_profit\\images\\',
                                              '', d[4]).replace('\\', '/')
                                if partcode_id > 0 and path:
                                    db.update_partcode_image(path, s_partcode_id)

                    # содаем таблицу аналогов моделей, к конкретной детали
                    if d[3]:
                        d3 = re.sub(r'\[|\]|\'', '', d[3])
                        d3 = d3.split(',')
                        for i, n in enumerate(d3):
                            a_model_id = db.get_model_id(n.replace('+', '').strip())
                            if partcode_id > 0:
                                if a_model_id < 1:
                                    a_brand_name = re.sub(r'\s.*$', '', n.replace('+', '').strip())
                                    a_brand_id = db.get_brand_id(a_brand_name)
                                    if a_brand_id > 0:
                                        a_model_id = get_model(n.strip(), a_brand_id)

                            if a_model_id > 0 and partcode_id > 0:
                                db.link_partcode_model_analogs(a_model_id, partcode_id)

                    # добавляем картинку к детали
                    if str(d[4]) != 'nan':
                        path = re.sub(r'E:\\Projects\\PycharmProjects\\parser_profit\\images\\', '', d[4])
                        if partcode_id > 0 and path:
                            db.update_partcode_image(path, partcode_id)
    files = load_files_list()


def load_files_list():
    path = r'parse'
    miss_brands = ['brother', 'canon', 'dell', 'epson']
    d = []

    for root, dirs, files in os.walk(path):
        for file in files:

            miss_brand = False

            for miss in miss_brands:
                if re.search(fr"parse\\{miss}", root):
                    miss_brand = True
            if miss_brand:
                continue

            d.append([f'{root}\\{file}', file])
    return d
