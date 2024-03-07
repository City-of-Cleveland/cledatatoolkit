import pandas as pd
import numpy as np

def calc_moe(array,how='sum'):
    """Helper function for developing margins of error (MOEs) for aggregations of sample estimates. 
    This is recommended for when you are summing, or taking the proportion of multiple ACS estimates. 
    This function implements the American Community Survey's documented methodology for calculating Margins of Error.

    Args:
        array (list-like): A list of margins of error to propogate over. If how = proportion, the arrays must be inputted in the following order:
               1. The denominators of the proportion.
               2. The proportions themselves.
               3. The margins of error of the numerator.
               4. The margins of error of the denominator.

        how (str, optional): Either 'sum' or 'proportion'. The aggregation methodology used for calculating the MOE. Defaults to 'sum'.

    Returns:
        float: The aggregated margin of error for the inputted array if `how`='sum'.
        numpy.array: The aggregated margins of error for the inputted array(s) if `how`='proportion'.
    """
    #Convert to numpy array
    array = np.array(array)

    if how=='sum':
         result = np.round(np.sqrt(np.sum(np.power(array,2))),0)

    elif how == 'proportion':
          y_reciprocal = np.divide(1,array[0])
          prop = array[1]
          x_moe = array[2]
          y_moe = array[3]

          term_2 = np.power(x_moe,2) - np.power(prop,2)*np.power(y_moe,2)
          term_2[term_2 < 0] = np.power(x_moe[term_2 < 0],2) + np.power(prop[term_2 < 0],2)*np.power(y_moe[term_2 < 0],2)

          result = y_reciprocal * np.sqrt(term_2)
    else:
         raise Exception("'How' argument must be either 'sum', 'mean', or 'proportion'.")
    return result
