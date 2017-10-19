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
movies_all_df = pd.read_sql("""SELECT * from movies""", conn)
movies_df = movies_all_df.loc[:, ["movieid", "movierow", "title", "year"]]
factorised_movies = movies_all_df.loc[:, ["latent1", "latent2", "latent3", "latent4", "latent5"]]
# Something wrong with diag table, so just hard-coding for now.
# factorised_diag = pd.read_sql("""SELECT * from diag""", conn)
diag = [9883.73108477146, 2604.8114716088617, 2046.7390225565089, 1836.1311790775487, 1428.3956754378983]

# Set up recommender.
m = MovieLensRecommender(factorised_movies=factorised_movies.as_matrix(),
                         factorised_diag=diag, # Should be: diag_df.as_matrix().transpose()
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
