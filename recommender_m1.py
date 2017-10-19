from recommender import Recommender
import numpy as np
import pandas as pd

class MovieLensRecommender:

    def __init__(self, factorised_movies, factorised_diag, movie_df):
        """
            Args:
                factorised_movies: u x r matrix.
                factorised_diag: r x 1 matrix.
                movie_df: pandas DataFrame with u rows. Must have these columns: movierow, title, year. 
                          May have other columns too. 
        """
        self.movie_df = movie_df.copy()
        self.recommender = Recommender(U = factorised_movies.copy(),
                                    S = factorised_diag.copy())

    def ratings_dict_to_column(self, x):
        """Convert movie titles and ratings to column vector that can be passed to the recommender.
            Args:
                x: dict. Keys are movie titles, values are ratings.
            Return: Vector with same length as self.recomender.U.
        """
        # Convert dict to data frame.
        x_df = pd.DataFrame.from_dict(x, orient='index')
        x_df = x_df.assign(Title=x_df.index, rating=x_df[0])
        # Merge to get MovieRows.
        x_df = x_df.merge(self.movie_df, on='title')
        # Create column vector, with entries corresponding to MovieRows as appropriate ratings
        # and nans elsewhere.
        ratings_col = np.empty(len(self.movie_df))
        ratings_col[:] = np.nan
        ratings_col[list(x_df['movierow'] - 1)] = x_df['rating'] # MovieRow is 1-indexed.
        return ratings_col

    def get_predictions(self, new_user_ratings):
        """
            Args:
                new_new_ratings: dict. Keys are titles, values are ratings.
        """
        # Make a prediction.
        new_user_ratings_column = self.ratings_dict_to_column(new_user_ratings)
        predictions = self.recommender.predict_for_new_v(new_user_ratings_column)
        # predictions is a vector corresponding to MovieRow.
        # Convert to title.
        return self.movie_df.copy().assign(prediction=predictions)
		
