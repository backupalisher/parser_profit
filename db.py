import psycopg2

con = psycopg2.connect(
    database="part4_new",
    user="part4",
    password="part4_GfhjkzYtn321",
    # host="198.245.61.187",
    host="localhost",
    port="5432"
)

cur = con.cursor()


def i_request(q):
    try:
        cur.execute(q)
        data = cur.fetchall()
    except psycopg2.DatabaseError as err:
        if err.pgerror:
            print("Error: ", err)
            print("Error: ", q)
    else:
        return data
    finally:
        con.commit()
