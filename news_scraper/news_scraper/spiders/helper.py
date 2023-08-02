import sqlite3


def sqlite_query(sql):
    conn = sqlite3.connect('news-scraper.db')
    cursor = conn.cursor()

    cursor.execute(sql)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data


def proces_text(text):
    data = text.split()
    data = [t for t in data]
    data = ' '.join(data)
    return data
