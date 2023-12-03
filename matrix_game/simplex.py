import math
import numpy as np

class SimplexDomain:
    def __init__(self, dimension):
        self._dimension = dimension
        self._prox      = SimplexEntropyProx(dimension)

    def dimension(self):
        return self._dimension

    def combine(self, y, alpha, x):
        return (1.0 - alpha)*y + alpha*x

    def prox(self):
        return self._prox

    def center(self):
        return np.ones(self._dimension)/self._dimension

    def diameter(self):
        return np.log(self._dimension)

    """
    support function: argmax_{x\in\Delta} g'x
    """
    def support(self, g):
        idx           = np.argmax(g)
        value         = g[idx]
        response      = np.zeros(self._dimension)
        response[idx] = 1.0
        return value, response

    def __repr__(self):
        return 'SimplexDomain(%d)' % self._dimension

class SimplexEntropyProx:
    def __init__(self, dimension):
        self._dimension = dimension

    def center(self):
        """ Returns a numpy array representing the center of the simplex as measured
        by the prox function. In the case of a simplex, this is the same as the uniform
        distribution.

        """
        _, arg = self(0.0, np.zeros(self._dimension), 1.0)
        return arg

    def __call__(self, alpha, g, beta, y=None):
        """ Computes the argmin and value of the expression:
        argmin_{x\in\Delta} alpha*g'x + beta*D(x, y)

        if y is not set, then the prox center is used

        The following derivation shows that the final return value corresponds to
        the prox function value:
        f(x)   = x'log(x) - x'e + 1 + log(n) + I_\Delta(x)
        f'(x)  = log(x) + \partial I_\Delta(x)
        f(e/n) = 0
        f^*(g) = log(Z) - log(n), Z = e'exp(g)
        min_{x\in\Delta} alpha*g'x + beta*D(x, y)
        = min alpha*g'x + beta*f(x) - beta*f(y) - beta*<\partial f(y), x - y>
        = -max -alpha*g'x - beta*f(x) + beta*f(y) + beta*<log(y), x - y>
        = -(beta*f)^*(-alpha*g + beta*log(y)) - beta*f(y) + beta*y'log(y)
        = -beta*f^*(-alpha/beta*g + log(y)) - beta*[y'log(y) + log(n)] +
        beta*y'log(y)
        = -beta*f^*(-alpha/beta*g + log(y)) - beta*log(n)
        = -beta*[log y'exp(-alpha/beta*g) - log(n)] - beta*log(n)
        = -beta*[log exp(-alpha/beta*offset)*y'exp(-alpha/beta*(g - offset)) ]
        = alpha*offset - beta*log y'exp(-alpha/beta*(g - offset))
        = alpha*offset - beta*log(Z)
        """

        if alpha < 0.0:
            offset = np.max(g)
        else:
            offset = np.min(g)

        z = np.exp(-alpha/beta*(g - offset))
        if y is not None:
            z *= y
        else:
            z /= len(g)

        Z = np.sum(z)
        z /= Z

        return alpha*offset - beta*math.log(Z), z
