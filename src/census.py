import pandas as pd
import numpy as np

def calc_moe(array,how='sum'):
    """Helper function for generating Margins of Error from a numpy array of MOEs and Estimates. Used for groupby aggregation.

    Args:
        array (list-like): A list of margins of error to propogate over. If how = proportion, the arrays must be inputted in the following order:
               1. The denominators of the proportion.
               2. The proportions themselves.
               3. The margins of error of the numerator.
               4. The margins of error of the denominator.

        how (str, optional): Either sum or mean, the methodology used for calculating the MOE. Defaults to 'sum'.

    Returns:
        float: The propogated margion of error.
    """

    if how=='sum':
         result = np.round(np.sqrt(np.sum(np.power(array,2))),0)
    elif how == 'mean':
         result = np.round(np.sqrt(np.sum(np.power([0.5*a for a in array],2))),0)
    elif how == 'proportion':
          y_reciprocal = np.divide(1,array[0])
          prop = array[1]
          x_moe = array[2]
          y_moe = array[3]

          term_2 = np.power(x_moe,2) - np.power(prop,2)*np.power(y_moe,2)
          term_2[term_2 < 0] = np.power(x_moe[term_2 < 0],2) + np.power(prop[term_2 < 0],2)*np.power(y_moe[term_2 < 0],2)

          result = y_reciprocal * np.sqrt(term_2)
    else:
         raise Exception("You fool! How must be either 'sum', 'mean', or 'proportion'.")
    return result