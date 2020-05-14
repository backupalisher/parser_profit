import os
import re

import pandas

import db_utils as db


def add_db():
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
                    spr_details_id = db.insert_model_spr_details(model.group(0))
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
                    detail_option_id = 0
                    module_id = 0
                    spr_details_id = 0
                    detail_id = 0

                    det = re.sub(r'^.*([A-Za-z0-9])\w+.*-\s', '', d[2])
                    det = re.sub(r'^\([^)]*\)', '', det)
                    if re.search(r'Ресурс:', det):
                        res = re.search(r'\([^)]*\)', det).group(0)
                        res_id = db.get_option_id('Ресурс')
                        res_val_id = db.get_option_id(re.sub(r'[^\d]', '', res))
                        detail_option_id = db.insert_detail_options(res_id, res_val_id)

                        det = re.sub(r'\([^)]*\)', '', det)
                    det = det.strip()

                    print(f'\r', d[0], d[1], d[2], end='')
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
                            a_model_id = db.get_model_id(n.strip())
                            if partcode_id > 0:
                                if a_model_id < 1:
                                    a_brand_name = re.sub(r'\s.*$', '', n.strip())
                                    a_brand_id = db.get_brand_id(a_brand_name)

                                    a_model_id = db.insert_model(n.strip(), a_brand_id)
                                    spr_details_id = db.insert_model_spr_details(n.strip())
                                    db.link_models_spr_details(a_model_id, spr_details_id)

                            if a_model_id > 0 and partcode_id > 0:
                                db.link_partcode_model_analogs(a_model_id, partcode_id)

                    # добавляем картинку к детали
                    if str(d[4]) != 'nan':
                        path = re.sub(r'E:\\Projects\\PycharmProjects\\parser_profit\\images\\', '', d[4])
                        if partcode_id > 0 and path:
                            db.update_partcode_image(path, partcode_id)


def load_files_list():
    path = r'parse'
    d = []
    for root, dirs, files in os.walk(path):
        for file in files:
            d.append([f'{root}\\{file}', file])
    return d
