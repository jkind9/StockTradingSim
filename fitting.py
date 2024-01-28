import numpy as np 
from sklearn.linear_model import LinearRegression

def fit_quadratic_polynomial(x, y):
    """
    Fit a quadratic polynomial (y = ax^2 + bx + c) to the given data points.

    :param x: Array-like, independent variable.
    :param y: Array-like, dependent variable.
    :return: Coefficients of the quadratic polynomial.
    """
    # Fit the quadratic polynomial
    coefficients = np.polyfit(x, y, 2)

    # Return the coefficients (a, b, c)
    return coefficients

def linear_regression(x,y):
    x=np.array(x)
    y = np.array(y)
    # Reshape the data (needed when you have a single feature)
    x = x.reshape(-1, 1)

    # Create a linear regression model
    model = LinearRegression()

    # Fit the model to the data
    model.fit(x, y)

    # Get the coefficients (slope and intercept)
    slope = model.coef_[0]
    intercept = model.intercept_
    return slope, intercept
