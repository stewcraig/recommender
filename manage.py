#!/usr/bin/env python

import os
from urllib import parse
from flask import Flask, render_template, jsonify, request
import psycopg2
import pandas as pd
from recommender_m1 import MovieLensRecommender

# Get database connection.
parse.uses_netloc.append("postgres")
url = parse.urlparse(os.environ["DATABASE_URL"])
conn = psycopg2.connect(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)
cur = conn.cursor()

# Form a dataframe of movie information.
movies_df = pd.DataFrame(columns=["movieid", "movierow", "title", "year", "genre"])
cur.execute("""SELECT movieid, movierow, title, year, genre from movies""")
movie_rows = cur.fetchall()
for row in movie_rows:
    movies_df = movies_df.append(row[0:5])
# Make sure it is in order.
movies_df = movies_df.sort_values("movieid")

# Form a dataframe of factorised movie coordinates for recommender.
# Get movieid as well so we can make sure it is in same order as movies_df.
factorised_movies = pd.DataFrame(columns=["movieid", "latent1", "latent2", "latent3", "latent4", "latent5"])
cur.execute("""SELECT movieid, latent1, latent2, latent3, latent4, latent5 from movies""")
movie_rows = cur.fetchall()
for row in movie_rows:
    factorised_movies = factorised_movies.append(row[0:6])
# Make sure it is in order, then drop movieid.
factorised_movies = factorised_movies.sort_values("movieid").drop("movieid", axis=1)

# Form a dataframe of the factorisation diagonal for the recommender.
factorised_diag = pd.DataFrame(columns=["diag"])
cur.execute("""SELECT diag from diag""")
diag_rows = cur.fetchall()
for row in diag_rows:
    factorised_diag = factorised_diag.append(row[0])

# Set up recommender.
m = MovieLensRecommender(factorised_movies=factorised_movies.as_matrix(),
                         factorised_diag=factorised_diag.as_matrix(),
                         movie_df=movies_df)

# Make some recommendations for a fixed new user.
new_user_ratings = {'Die Hard':5, 'Terminator':5, 'Speed':5}
predictions_df = m.get_predictions(new_user_ratings)

# Set up app.
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
                "\nFirst row of movies table: " + str(movie_rows[0]) +
                ".\n New ratings: " + str(new_user_ratings) +
                ".\n Predictions: " + str(predictions_string))
    except Error as e:
        print(e)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
