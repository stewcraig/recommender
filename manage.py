#!/usr/bin/env python

import os
from urllib import parse
import toolz
from flask import Flask, render_template, jsonify, request
import psycopg2
import pandas as pd
from recommender_m1 import MovieLensRecommender

# Get database connection.
parse.uses_netloc.append("postgres")
try:
  url = parse.urlparse(os.environ["DATABASE_URL"])
  conn = psycopg2.connect(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)
  cur = conn.cursor()

  # Form a dataframe of movie information.
  movies_all_df = pd.read_sql("""SELECT * from movies""", conn)
  movies_df = movies_all_df.loc[:, ["movieid", "movierow", "title", "year"]]
  movie_titles = movies_all_df.title.tolist()
  factorised_movies = movies_all_df.loc[:, ["latent1", "latent2", "latent3", "latent4", "latent5"]]
  # Something wrong with diag table, so just hard-coding for now.
  # factorised_diag = pd.read_sql("""SELECT * from diag""", conn)
  diag = [9883.73108477146, 2604.8114716088617, 2046.7390225565089, 1836.1311790775487, 1428.3956754378983]

  # Set up recommender.
  m = MovieLensRecommender(factorised_movies=factorised_movies.as_matrix(),
                           factorised_diag=diag, # Should be: diag_df.as_matrix().transpose()
                           movie_df=movies_df)
  # Set recommender function.
  make_predictions = lambda new_user_ratings: m.get_predictions(new_user_ratings).sort_values('prediction', ascending=False).head()
except KeyError:
  # Probably couldn't access the database. Create a 'recommender' that always reports failure.
  make_predictions = lambda x: "Could not access database."
  # Create an empty list of movie titles for autocompletion.
  movie_titles = []
  
# Set up app.
app = Flask(__name__)

@app.route('/')
def static_page():
    return render_template('index.html')

@app.route('/search/', methods=['GET'])
def test_reply():
    try:
        movie_rating_string = request.args.get('value', "DEFAULT VALUE", type=str)
        print("Got: " + movie_rating_string)
        # movie_rating_string is of form "movie1+rating1+movie2+rating2+".
        # Convert to dict.
        parsed_movie_ratings = dict(toolz.itertoolz.partition(2, movie_rating_string.split("+")))
        print("Parsed: " + str(parsed_movie_ratings))
        predictions_string = str(make_predictions(parsed_movie_ratings)) 
        print("Predictions: " + str(predictions_string))
        jsonified = jsonify(result="Your ratings: " + str(parsed_movie_ratings) + "\n\n" +
                	"Predictions: " + predictions_string)
        print("Going to return: " + str(jsonified))
        return jsonified
    except Error as e:
        print(e)

@app.route('/movies/', methods=['GET'])
def autocomplete():
    try:
        auto_comp_string = request.args.get('search', 'DEFAULT VALUE', type=str)
        print('Got:' + str(auto_comp_string))
        print("Movie titles: ")
        print(movie_titles[0:4])
        matching_movie_titles = [x for x in movie_titles if auto_comp_string in x]
        return jsonify(matching_movie_titles)
    except Error as e:
        print(e)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
