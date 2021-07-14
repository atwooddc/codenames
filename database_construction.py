import sqlite3
from sqlite3 import Error
import requests as req
from ratelimiter import RateLimiter

names = ['soul', 'shark', 'knife', 'trip', 'watch', 'hospital', 'green', 'smuggler', 'ice', 'racket', 'band',
         'millionaire', 'pitch', 'bow', 'lock', 'dinosaur', 'car', 'pole', 'horseshoe', 'fire', 'cliff', 'pipe',
         'leprechaun', 'knight', 'drill']


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def build_database():
    con = create_connection("codenames.db")

    create_names_table = """
    CREATE TABLE IF NOT EXISTS names (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
    );
    """
    execute_query(con, create_names_table)

    cur = con.cursor()


    for n in names:
        cur.execute("INSERT INTO names (name) VALUES ('%s')" % n)
    cur.execute("SELECT * FROM names")
    print(cur.fetchall())

    create_related_table = """
    CREATE TABLE IF NOT EXISTS related (
    related_word TEXT,
    name_id INTEGER,
    FOREIGN KEY(name_id) REFERENCES names(id)
    );
    """
    execute_query(con, create_related_table)

    for i in range(25):
        relationX = "relation_" + str(i + 1)
        execute_query(con, " ALTER TABLE related ADD '%s' DOUBLE(4,3);" % relationX)


def add_entries():
    con = create_connection("../codenames_test.db")
    cur = con.cursor()

    # names is list of all 25 codenames on board
    id = 1
    for n in names:
        url = 'http://api.conceptnet.io/query?node=/c/en/' + n
        resp = req.get(url).json()
        num = 0
        acc = 0
        while num < 20 and acc < len(resp['edges']):
            start = resp['edges'][acc]['start']
            end = resp['edges'][acc]['end']
            # only accept one word edges, or edges where the only add'l words are articles
            if 'language' in start and 'language' in end and start['language'] == 'en' and end['language'] == 'en' \
                    and '_' not in start['@id'] and '_' not in end['@id']:
                if n not in end['label']:
                    rel = end['label'].lower()
                else:
                    rel = start['label'].lower()
                countSpace = 0
                for i in range(len(rel)):
                    if rel[i] == " ":
                        countSpace += 1
                if countSpace == 0 or (countSpace == 1 and rel != removeArticles(rel)):
                    if countSpace == 1:
                        rel = removeArticles(rel)
                    if rel not in n and n not in rel and findRelatedness(n,
                                                                         rel) > 0.1:  # not cur.execute("SELECT * FROM related WHERE related_word=\"" +rel + "\"") and
                        relatednesses = []
                        for m in names:
                            r = round(findRelatedness(m, rel), 3)
                            if r < 0.05:
                                r = 0
                            relatednesses.append(str(r))
                        # cur.execute("INSERT INTO related VALUES ('%s','%s','%s')" % (rel, str(id), ",".join(relatednesses)))
                        exec_str = " INSERT INTO related VALUES (\"" + rel + "\"," + str(id) + "," + ",".join(relatednesses) + ");"
                        cur.execute(exec_str)
                        print(exec_str)
                        con.commit()
                        num = num + 1
            acc = acc + 1
        id = id + 1
    cur.execute("SELECT * FROM related")
    print(cur.fetchall())

# delete repeats from table
def delete_duplicates():
    con = create_connection("/Users/davidatwood/Documents/compsci/petprojects/codenames2.db")
    cur = con.cursor()
    # add primary key_id
    # cur.execute("ALTER TABLE related ADD PRIMARY KEY (related_id);")
    # con.commit()
    # group by related_word and name_id
    # cur.execute("""SELECT *
    #     FROM related
    #     GROUP BY related_word, name_id
    # """)
    cur.execute("""DELETE FROM related
    WHERE rowid NOT IN
    (
        SELECT MAX(rowid)
        FROM related
        GROUP BY related_word, 
            name_id
    );""")
    con.commit()


def removeArticles(text):
    articles = {'a': '', 'an': '', 'and': '', 'the': ''}
    rest = []
    for word in text.split():
        if word not in articles:
            rest.append(word)
    return ' '.join(rest)


# From ConceptNet website:
# "You can make 3600 requests per hour to the ConceptNet API, with bursts of 120 requests per minute allowed.
# The /related and /relatedness endpoints count as two requests when you call them.
# This means you should design your usage of the API to average less than 1 request per second."
@RateLimiter(max_calls=1, period=2)
def findRelatedness(w1, w2):
    if w1 != '' and w2 != '':
        url = 'http://api.conceptnet.io//relatedness?node1=/c/en/' + w1 + '&node2=/c/en/' + w2
        resp = req.get(url).json()
        return resp['value']
    else:
        return 0


build_database()
add_entries()
delete_duplicates()