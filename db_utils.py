import db


def get_brand_id(brand):
    q = db.i_request(f'SELECT id FROM brands WHERE LOWER(name) = LOWER(\'{brand}\')')
    if q:
        return q[0][0]
    else:
        return 0


def link_models_spr_details(model_id, spr_detail_id):
    db.i_request(f'WITH s as (SELECT id FROM details '
                 f'WHERE model_id = {model_id} AND spr_detail_id = {spr_detail_id}), i as '
                 f'(INSERT INTO details (model_id, spr_detail_id) SELECT {model_id}, {spr_detail_id} '
                 f'WHERE NOT EXISTS (SELECT 1 FROM s) RETURNING id) SELECT id FROM i UNION ALL SELECT id FROM s')


def update_spr_detail_name(partcode, name_ru):
    db.i_request(f'UPDATE spr_details SET name_ru = \'{name_ru}\' '
                 f'FROM (SELECT spr_detail_id FROM details, (SELECT id FROM partcodes WHERE code = \'{partcode}\') pc '
                 f'WHERE partcode_id = pc."id" GROUP BY spr_detail_id) sd WHERE sd.spr_detail_id = id')


def get_model_id(model):
    # SELECT * FROM models WHERE regexp_replace(name,'-','','g') ~* 'Brother HL1030';
    q = db.i_request(f'SELECT id FROM models WHERE LOWER(regexp_replace(name,\'-\', \'\', \'g\')) '
                     f'SIMILAR TO LOWER(concat(\'%\' || regexp_replace(\'{model}\',\'-\', \'\', \'g\') || \'%\'))')
    if q:
        return q[0][0]
    else:
        return 0


def insert_model(model, brand_id):
    q = db.i_request(f'WITH s as (SELECT id FROM models '
                     f'WHERE LOWER(regexp_replace(name,\'-\', \'\', \'g\')) SIMILAR TO '
                     f'LOWER(concat(\'%\' || regexp_replace(\'{model}\',\'-\', \'\', \'g\') || \'%\'))), i as '
                     f'(INSERT INTO models (name, brand_id) SELECT \'{model}\', \'{brand_id}\' '
                     f'WHERE NOT EXISTS (SELECT 1 FROM s) RETURNING id) SELECT id FROM i UNION ALL SELECT id FROM s')
    return q[0][0]


def insert_spr_details(model):
    q = db.i_request(f'WITH s as (SELECT id FROM spr_details '
                     f'WHERE LOWER(regexp_replace(name,\'-\', \'\', \'g\')) SIMILAR TO '
                     f'LOWER(concat(\'%\' || regexp_replace(\'{model}\',\'-\', \'\', \'g\') || \'%\'))), i as '
                     f'(INSERT INTO spr_details (name) SELECT \'{model}\' '
                     f'WHERE NOT EXISTS (SELECT 1 FROM s) RETURNING id) SELECT id FROM i UNION ALL SELECT id FROM s')
    return q[0][0]


def insert_partcode_model_analogs(model_id, partcode_id):
    db.i_request(f'WITH s as (SELECT 1 FROM link_partcode_model_analogs '
                 f'WHERE model_id = {model_id} AND partcode_id = {partcode_id}), '
                 f'i as (INSERT INTO link_partcode_model_analogs (model_id, partcode_id) '
                 f'SELECT {model_id}, {partcode_id} WHERE NOT EXISTS (SELECT 1 FROM s) RETURNING 0) '
                 f'SELECT * FROM i UNION ALL SELECT * FROM s')

# def insert_spr_details(model):
#     q = db.i_request(f'WITH s as (SELECT id FROM spr_details '
#                      f'WHERE LOWER(regexp_replace(name,\'-\', \'\', \'g\')) SIMILAR TO '
#                      f'LOWER(concat(\'%\' || regexp_replace(\'{model}\',\'-\', \'\', \'g\') || \'%\'))), i as '
#                      f'(INSERT INTO spr_details (name) SELECT \'{model}\' '
#                      f'WHERE NOT EXISTS (SELECT 1 FROM s) RETURNING id) SELECT id FROM i UNION ALL SELECT id FROM s')
#     return q[0][0]


# def insert_spr_modules(module_name):
#     q = db.i_request(f'WITH s as (SELECT id FROM spr_modules '
#                      f'WHERE LOWER(name_ru) = LOWER(\'{module_name}\')), i as '
#                      f'(INSERT INTO spr_modules (name_ru) SELECT \'{module_name}\' '
#                      f'WHERE NOT EXISTS (SELECT 1 FROM s) RETURNING id) SELECT id FROM i UNION ALL SELECT id FROM s')
#     return q[0][0]


# def insert_partcodes(partcode):
#     q = db.i_request(f'WITH s as (SELECT id FROM partcodes '
#                      f'WHERE LOWER(code) = LOWER(\'{partcode}\')), i as '
#                      f'(INSERT INTO partcodes (code) SELECT \'{partcode}\' '
#                      f'WHERE NOT EXISTS (SELECT 1 FROM s) RETURNING id) SELECT id FROM i UNION ALL SELECT id FROM s')
#     return q[0][0]


def get_partcode_id(partcode):
    q = db.i_request(f'SELECT id FROM partcodes WHERE code = \'{partcode}\'')
    if q:
        return q[0][0]
    else:
        return 0


def update_module_name(module_name, partcode_id):
    db.i_request(f'UPDATE spr_modules SET name_ru = \'{module_name}\' '
                 f'FROM (SELECT module_id FROM details WHERE partcode_id = {partcode_id} '
                 f'GROUP BY module_id) mo WHERE mo.module_id = id')


def update_model_image(path, model_id):
    db.i_request(f'UPDATE models SET main_image = \'{path}\' WHERE id = {model_id}')


def update_partcode_image(path, partcode_id):
    db.i_request(f'UPDATE partcodes SET images = \'{path}\' WHERE id = {partcode_id}')


# def get_module_id(partcode):
#     q = db.i_request(f'SELECT mo.id FROM partcodes pc '
#                      f'LEFT JOIN details d on pc.id = d.partcode_id '
#                      f'LEFT JOIN spr_modules mo on d.module_id = mo.id '
#                      f'WHERE pc.code SIMILAR TO \'%{partcode}%\' GROUP BY mo.id')
#     if q:
#         return q[0][0]
#     else:
#         return 0


# -----------------------------
# INSERT OR UPDATE spr_modules
# -----------------------------

# WITH sm_update as (UPDATE spr_modules SET name_ru = 'Подача и захват бумаги'
# FROM (SELECT module_id FROM details, (SELECT id FROM partcodes WHERE code = 'LF4812001') pc
# WHERE partcode_id = pc."id" GROUP BY module_id) mo WHERE mo.module_id = id RETURNING id),
# sm_insert as (INSERT INTO spr_modules (name_ru) SELECT 'Подача и захват бумаги'
# WHERE NOT EXISTS (SELECT 1 FROM sm_update) RETURNING id)
# SELECT id FROM sm_insert UNION ALL SELECT id FROM sm_update
