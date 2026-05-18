import numpy as np


def perceptron(X, y, max_iter=1000):
    X = np.c_[np.ones(len(X)), X]  # bias
    w = np.zeros(X.shape[1])

    for _ in range(max_iter):
        errors = 0

        for xi, yi in zip(X, y):
            if yi * np.dot(w, xi) <= 0:
                w += yi * xi
                errors += 1

        if errors == 0:
            break

    return w


def train_multiclass(clusters, max_iter=100):
    X = np.vstack(clusters)

    y = np.hstack([
        np.full(len(c), i) for i, c in enumerate(clusters)
    ])

    classifiers = []

    for k in range(len(clusters)):
        y_bin = np.where(y == k, 1, -1)
        w = perceptron(X, y_bin, max_iter)
        classifiers.append(w)

    return classifiers


def mkp(X, y, beta=1.0, delta=1.0, max_iter=500):

    X = np.c_[np.ones(len(X)), X]  # bias
    classes = np.unique(y)

    classifiers = []

    for k in classes:

        w = np.zeros(X.shape[1])

        y_bin = np.where(y == k, 1, -1)

        for _ in range(max_iter):

            errors = 0

            idx = np.random.permutation(len(X))
            Xs, ys = X[idx], y_bin[idx]

            for xi, yi in zip(Xs, ys):

                norm = np.dot(xi, xi)

                Q = np.dot(w, xi) * yi

                if Q < delta:
                    w += (beta / norm) * xi * yi
                    errors += 1

            if errors == 0:
                break

        classifiers.append(w)

    return classifiers


def umkp(X, y, beta=1.0, delta=1.0, max_iter=1000):

    X = np.c_[np.ones(len(X)), X]
    classes = np.unique(y)

    classifiers = []

    for k in classes:

        w = np.zeros(X.shape[1])
        y_bin = np.where(y == k, 1, -1)

        for _ in range(max_iter):

            errors = 0
            idx = np.random.permutation(len(X))

            for xi, yi in zip(X[idx], y_bin[idx]):

                Q = np.dot(w, xi) * yi

                if Q < delta:
                    w += beta * xi * yi
                    errors += 1

            if errors == 0:
                break

        classifiers.append(w)

    return classifiers
