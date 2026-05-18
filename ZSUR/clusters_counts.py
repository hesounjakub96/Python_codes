import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from scipy.spatial.distance import cdist


def hladiny_simple(data, threshold=3):
    Z = linkage(data, method="single")

    plt.figure()
    dendrogram(Z)
    plt.ylabel("Distance")
    plt.title("Dendrogram")
    plt.show()

    labels = fcluster(Z, t=threshold, criterion="distance")

    pocet_skupin = len(np.unique(labels))

    return pocet_skupin


def retez_mapy(data, threshold=0.33, show_path=True, show_distances=True):
    n = len(data)

    D = cdist(data, data, metric="sqeuclidean")
    np.fill_diagonal(D, np.inf)

    start = np.random.randint(n)
    used = np.zeros(n, dtype=bool)

    chain = [start]
    used[start] = True
    current = start
    distances = []

    for _ in range(n - 1):

        # nearest unused
        candidates = np.where(~used)[0]
        next_index = candidates[np.argmin(D[current, candidates])]

        distances.append(D[current, next_index])
        chain.append(next_index)
        used[next_index] = True
        current = next_index

    pocet_skupin = 1 + np.sum(distances >= 1 + max(distances) * threshold)

    if show_path:
        path = data[chain]

        plt.plot(path[:, 0], path[:, 1], marker="x")
        plt.title("Chain map")
        plt.show()

    if show_distances:
        plt.plot(np.arange(len(distances)), distances)
        plt.show()

    return pocet_skupin


def maximim(data, start_index=None, plot=True):
    n = len(data)

    D = cdist(data, data)  # dist_matrix
    # random start; not rly centers..
    centers = [np.random.randint(n) if start_index is None else start_index]
    # furthest point as the second center
    centers.append(np.argmax(D[centers[0]]))

    while True:

        d_min = np.min(D[:, centers], axis=1)  # distance to the nearest center

        candidate = np.argmax(d_min)
        m = d_min[candidate]

        # mean distance between centers
        if len(centers) > 1:
            avg = D[np.ix_(centers, centers)].mean()
        else:
            avg = 0

        if m > avg:
            centers.append(candidate)
        else:
            break

    if plot:
        plt.scatter(data[:, 0], data[:, 1], label="data")

        # plt.scatter(
        #     data[centers, 0],
        #     data[centers, 1],
        #     marker="D",
        #     s=50,
        #     label="centers"
        # )

        plt.legend()
        plt.title("MaxiMin centers")
        plt.show()

    return len(centers)
