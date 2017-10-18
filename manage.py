#!/usr/bin/env python

from flask import Flask, render_template, jsonify, request
import os, psycopg2
from urllib import parse
import pandas as pd
from recommender_m1 import MovieLensRecommender

# Get database connection.
parse.uses_netloc.append("postgres")
url = parse.urlparse(os.environ["DATABASE_URL"])
conn = psycopg2.connect(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)
cur = conn.cursor()
# Try to get something from database.
movies_df = pd.DataFrame(columns=["movieid", "movierow", "title", "year", "genre"])
cur.execute("""SELECT movieid, movierow, title, year, genre from movies""")
movie_rows = cur.fetchall()
for row in movie_rows:
	factorised_movies = factorised_movies.append(row[0:5])

factorised_movies = pd.DataFrame(columns=["movieid", "movierow", "title", "year", "genre"])
cur.execute("""SELECT movieid, movierow, title, year, genre from movies""")
movie_rows = cur.fetchall()
for row in movie_rows:
	factorised_movies = factorised_movies.append(row[0:5])

factorised_diag = pd.DataFrame(columns=["diag"])
cur.execute("""SELECT * from diag""")
diag_rows = cur.fetchall()
for row in diag_rows:
	factorised_diag = factorised_diag.append(row[0])

# Set up recommender.
m = MovieLensRecommender(factorised_movies=factorised_movies,
                         factorised_diag=factorised_diag,
                         movie_df=movies_df)
new_user_ratings = {'Die Hard':5, 'Terminator':5, 'Speed':5}
predictions_df = m.get_predictions(new_user_ratings)

app = Flask(__name__)

@app.route('/')
def static_page():
    return render_template('index.html')

@app.route('/search/', methods=['GET'])
def test_reply():
	try:
		value = request.args.get('value', "DEFAULT VALUE", type=str)
		return_value = value.upper()
		predictions_string = predictions_df.sort_values('prediction', ascending=False).head()
		return jsonify(result = "JS said: " + value + " and Flask replied: " + return_value +
				"First row of movies table: " + str(movie_rows[0]) +
				". New ratings: " + str(new_user_ratings) +
				". Predictions: " + str(predictions_string))
	except Error as e:
		print(e)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
