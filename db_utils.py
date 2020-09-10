import db


def get_brand_id(brand):
    q = db.i_request(f'SELECT id FROM brands WHERE LOWER(name) = LOWER(\'{brand}\')')
    if q:
        return q[0][0]
    else:
        return 0


def get_model_id(model):
    # SELECT * FROM models WHERE regexp_replace(name,'-','','g') ~* 'Brother HL1030';
    # q = db.i_request(f"SELECT id FROM models WHERE LOWER(name) "
    #                  f"SIMILAR TO LOWER(concat('%' || regexp_replace('{model}', '-', '', 'g') || '%'))")
    q = db.i_request(f"SELECT id FROM models WHERE LOWER(name) = LOWER('{model}')")
    if q:
        return q[0][0]
    else:
        return 0


def get_models(model):
    return db.i_request(f"SELECT * FROM models WHERE LOWER(regexp_replace(name,'-','','g')) SIMILAR TO LOWER('{model}')")


def insert_model(model, brand_id):
    q = db.i_request(f"WITH s as (SELECT id FROM models "
                     f"WHERE LOWER(concat('%' || regexp_replace(name,'-','','g') || '%')) SIMILAR TO "
                     f"LOWER({model})), i as "
                     f"(INSERT INTO models (name, brand_id) SELECT '{model}', {brand_id} "
                     f"WHERE NOT EXISTS (SELECT 1 FROM s) RETURNING id) SELECT id FROM i UNION ALL SELECT id FROM s")

    if q:
        return q[0][0]
    else:
        return 0


def insert_model_spr_details(model):
    q = db.i_request(f"WITH s as (SELECT id FROM spr_details "
                     f"WHERE LOWER(name) SIMILAR TO "
                     f"LOWER(concat('%' || regexp_replace('{model}', '-', '', 'g') || '%'))), i as "
                     f"(INSERT INTO spr_details (name) SELECT '{model}' "
                     f"WHERE NOT EXISTS (SELECT 1 FROM s) RETURNING id) SELECT id FROM i UNION ALL SELECT id FROM s")
    if q:
        return q[0][0]
    else:
        return 0


def link_models_spr_details(model_id, spr_detail_id):
    db.i_request(f"WITH s as (SELECT id FROM details "
                 f"WHERE model_id = {model_id} AND spr_detail_id = {spr_detail_id}), i as "
                 f"(INSERT INTO details (model_id, spr_detail_id) SELECT {model_id}, {spr_detail_id} "
                 f"WHERE NOT EXISTS (SELECT 1 FROM s) RETURNING id) SELECT id FROM i UNION ALL SELECT id FROM s")


def update_model_image(path, model_id):
    db.i_request(f"UPDATE models SET main_image = '{path}' WHERE id = {model_id}")


def get_option_id(name):
    q = db.i_request(f"WITH s as (SELECT id FROM spr_detail_options WHERE name = '{name}'), "
                     f"i as (INSERT INTO spr_detail_options (name) SELECT '{name}' "
                     f"WHERE NOT EXISTS (SELECT 1 FROM s) RETURNING id) SELECT * FROM i UNION ALL SELECT * FROM s")
    if q:
        return q[0][0]
    else:
        return 0


def insert_detail_options(caption_spr_id, detail_option_spr_id):
    q = db.i_request(f"WITH s as (SELECT id FROM detail_options WHERE "
                     f"caption_spr_id = {caption_spr_id} AND detail_option_spr_id = {detail_option_spr_id}), "
                     f"i as (INSERT INTO detail_options (caption_spr_id, detail_option_spr_id, parent_id) "
                     f"SELECT {caption_spr_id}, {detail_option_spr_id}, 1 "
                     f"WHERE NOT EXISTS (SELECT 1 FROM s) returning id) SELECT id FROM i UNION ALL SELECT id FROM s")

    return q[0][0]


def get_partcode_id(partcode):
    q = db.i_request(f"SELECT id FROM partcodes WHERE code = '{partcode}'")
    if q:
        return q[0][0]
    else:
        return 0


def update_spr_detail_name(partcode, name_ru):
    db.i_request(f"UPDATE spr_details SET name_ru = '{name_ru}' "
                 f"FROM (SELECT spr_detail_id FROM details, (SELECT id FROM partcodes WHERE code = '{partcode}') pc "
                 f'WHERE partcode_id = pc."id" GROUP BY spr_detail_id) sd WHERE sd.spr_detail_id = id')


def insert_spr_modules(module_name):
    q = db.i_request(f"WITH s as (SELECT id FROM spr_modules "
                     f"WHERE LOWER(name_ru) = LOWER('{module_name}')), i as "
                     f"(INSERT INTO spr_modules (name_ru) SELECT '{module_name}' "
                     f"WHERE NOT EXISTS (SELECT 1 FROM s) RETURNING id) SELECT id FROM i UNION ALL SELECT id FROM s")
    if q:
        return q[0][0]
    else:
        return 0


def insert_partcodes(partcode):
    q = db.i_request(f"WITH s as (SELECT id FROM partcodes "
                     f"WHERE LOWER(code) = LOWER('{partcode}')), i as "
                     f"(INSERT INTO partcodes (code) SELECT '{partcode}' "
                     f"WHERE NOT EXISTS (SELECT 1 FROM s) RETURNING id) SELECT id FROM i UNION ALL SELECT id FROM s")
    if q:
        return q[0][0]
    else:
        return 0


def insert_detail_spr_details(detail):
    q = db.i_request(f"WITH s as (SELECT id FROM spr_details "
                     f"WHERE LOWER(name_ru) SIMILAR TO "
                     f"LOWER(concat('%' || '{detail}' || '%'))), i as "
                     f"(INSERT INTO spr_details (name_ru) SELECT '{detail}' "
                     f"WHERE NOT EXISTS (SELECT 1 FROM s) RETURNING id) SELECT id FROM i UNION ALL SELECT id FROM s")
    if q:
        return q[0][0]
    else:
        return 0


def link_part_model_module_spr(partcode_id, model_id, module_id, spr_detail_id):
    q = db.i_request(f"WITH s as (SELECT 1 FROM details "
                     f"WHERE partcode_id = {partcode_id} AND model_id = {model_id} AND module_id = {module_id} AND "
                     f"spr_detail_id = {spr_detail_id}), i as "
                     f"(INSERT INTO details (partcode_id, model_id, module_id, spr_detail_id) "
                     f"SELECT {partcode_id}, {model_id}, {module_id}, {spr_detail_id} WHERE NOT EXISTS "
                     f"(SELECT 1 FROM s) RETURNING 0) SELECT * FROM i UNION ALL SELECT * FROM s")
    if q:
        return q[0][0]
    else:
        return 0


def link_partcode_model_analogs(model_id, partcode_id):
    db.i_request(f"WITH s as (SELECT 1 FROM link_partcode_model_analogs "
                 f"WHERE model_id = {model_id} AND partcode_id = {partcode_id}), "
                 f"i as (INSERT INTO link_partcode_model_analogs (model_id, partcode_id) "
                 f"SELECT {model_id}, {partcode_id} WHERE NOT EXISTS (SELECT 1 FROM s) RETURNING 0) "
                 f"SELECT * FROM i UNION ALL SELECT * FROM s")


def link_detail_options(detail_id, detail_option_id):
    db.i_request(f"WITH s as (SELECT 1 FROM link_details_options "
                 f"WHERE detail_id = {detail_id} AND detail_option_id = {detail_option_id}), i as "
                 f"(INSERT INTO link_details_options (detail_id, detail_option_id) "
                 f"SELECT {detail_id}, {detail_option_id} "
                 f"WHERE NOT EXISTS (SELECT 1 FROM s) RETURNING 0) select * from i union all select * from s")


def update_partcode_image(path, partcode_id):
    db.i_request(f"UPDATE partcodes SET images = '{path}' WHERE id = {partcode_id}")

