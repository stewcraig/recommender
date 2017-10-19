import numpy as np

class Recommender:

    def __init__(self, U, S):
        """
            Args:
                U: Matrix.
                S: Vector.
        """
        self.U = np.matrix(U.copy())
        self.diag_S = np.diag(S.copy())

    def predict_for_new_v(self, new_v):
        """Using method from Brand 'Fast online SVD revisions for lightweight recommender systems',
        Section B.1.

            Args:
                new_v: Vector representing ratings for new column of ratings matrix. Can have missing values.
        """
        if len(new_v) != len(self.U):
            raise ValueError("new_v (length " + str(len(new_v)) + ") have same length as rows of U (which is " + str(len(self.U)) + ").")
        c = np.matrix(new_v).transpose() # Column matrix.
        mask_nas = np.isnan(new_v)
        # Following notation in paper:
        # c_closed (filled circle): vector of known values in c.
        # c_open (open circle): vector of unknown values in c.
        # U_closed, U_open: corresponding rows of U.
        c_closed = c[~mask_nas, :] # Shape: n_non_missing x 1.
        c_open = c[mask_nas, :] # Shape: n_missing x 1.
        U_closed = self.U[~mask_nas, :] # Shape: n_non_missing x r.
        U_open = self.U[mask_nas, :] # Shape: n_missing x r.
        # Impute missing values of c.
        c_hat_open = U_open * self.diag_S * np.linalg.pinv(U_closed * self.diag_S) * c_closed
        c_imputed = c.copy()
        c_imputed[mask_nas, :] = c_hat_open
        return c_imputed