#db.py
import os
import pymysql
import json

# db_user = os.environ.get('CLOUD_SQL_USERNAME')
# db_password = os.environ.get('CLOUD_SQL_PASSWORD')
# db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
# db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

def open_connection():
    try:
        conn = pymysql.connect(host='34.123.92.221',
                            user='root',
                            port= 3306,
                            password='vegefinder1234',                             
                            db='vegefinder-db-dev',
                            charset='utf8mb4',
                            cursorclass=pymysql.cursors.DictCursor) 
    except pymysql.MySQLError as e:
        print(e)

    return conn


def get_detail_vegetable(class_name):
    conn = open_connection()
    with conn.cursor() as cursor:
        # Query 1
        query1 = "SELECT * FROM `vegetables` WHERE `class_name` = %s LIMIT 1"
        cursor.execute(query1, (class_name,))
        vegetable = cursor.fetchall()

        if len(vegetable) > 0:
            get_vegetable = vegetable[0]

            # Query 2
            query2 = '''
            SELECT `id`, `name`, `type_group_id`
            FROM `types` 
            INNER JOIN `vegetables_types` 
            ON `types`.`id` = `vegetables_types`.`type_id` 
            WHERE `vegetables_types`.`vegetable_id` = %s
            '''
            cursor.execute(query2, (get_vegetable['id'],))
            types = cursor.fetchall()

            # Query 3
            query3 = "SELECT `id`, `name` FROM `type_groups` WHERE `type_groups`.`id` IN (%s, %s, %s)"
            type_group_ids = (1, 2, 3)
            cursor.execute(query3, type_group_ids)
            type_groups = {type_group['id']: type_group for type_group in cursor.fetchall()}

            for type in types:
                type['type_group'] = type_groups.get(type['type_group_id'])

            get_vegetable['types'] = types
            get_vegetable['images'] = array = json.loads( get_vegetable['images'] )
            get_vegetable['is_saved'] = True
        else:
            get_vegetable = 'No vegetable in DB'

    conn.close()
    return get_vegetable
