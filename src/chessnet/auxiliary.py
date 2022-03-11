from typing import Union, Literal, Sequence, Tuple

import numpy as np


def powerlaw(
    X: Union[float, np.ndarray], a: float, c: float
) -> Union[float, np.ndarray]:
    return c * X**a


def linear_regression(
    xvalues: Union[np.ndarray, Sequence],
    yvalues: Union[np.ndarray, Sequence],
    scale: Literal["loglog", "logx", "logy", "linear"] = "loglog",
    t: float = 1.96,
) -> Tuple[np.ndarray, float, float]:

    if scale == "loglog":
        X = np.log(xvalues)
        Y = np.log(yvalues)
    elif scale == "logy":
        X = np.array(xvalues)
        Y = np.log(yvalues)
    elif scale == "logx":
        X = np.log(xvalues)
        Y = np.array(yvalues)
    elif scale == "linear":
        X = np.array(xvalues)
        Y = np.array(yvalues)
    else:
        raise ValueError("ERROR: scale", scale, "not supported")

    coeffs, cov = np.polyfit(X, Y, 1, cov=True)
    errors = np.sqrt(np.diag(cov))

    intercept = coeffs[1]
    slope = coeffs[0]
    std = t * errors[0]
    Y_pred = intercept + X * slope
    if scale in ["loglog", "logy"]:
        Y_pred = np.exp(Y_pred)
    y_error = t * std

    return Y_pred, slope, y_error
