#!/usr/bin/env python

from flask import Flask, render_template, jsonify, request
import os, psycopg2
from urllib import parse

# Get database connection.
parse.uses_netloc.append("postgres")
url = parse.urlparse(os.environ["DATABASE_URL"])
conn = psycopg2.connect(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)
cur = conn.cursor()
# Try to get something from database.
cur.execute("""SELECT title from movies""")
movie_rows = cur.fetchall()
		
app = Flask(__name__)

@app.route('/')
def static_page():
    return render_template('index.html')

@app.route('/search/', methods=['GET'])
def test_reply():
	try:
		value = request.args.get('value', "DEFAULT VALUE", type=str)
		return_value = value.upper() + " and movie title: " + str(movie_rows[0])
		return jsonify(result = "JS said: " + value + " and Flask replied: " + return_value)
	except Error as e:
		print(e)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
