import numpy as np
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt


def split(data, max_iter=100):
    i = np.argmax(np.sum(cdist(data, data), axis=1))  # farthest point
    j = np.argmax(cdist(data, [data[i]]).ravel())  # farthest point of i

    c1, c2 = data[i].copy(), data[j].copy()  # i j are set as centers

    for _ in range(max_iter):
        D = cdist(data, [c1, c2])  # distances from points i and j
        # set labels to other points based on the closes center
        labels = np.argmin(D, axis=1)

        cluster1, cluster2 = data[labels ==
                                  0], data[labels == 1]  # new clusters

        # new first center (if nonempty)
        nc1 = cluster1.mean(axis=0) if len(cluster1) else c1
        # new second centrer (if nonempty)
        nc2 = cluster2.mean(axis=0) if len(cluster2) else c2

        # check if centers did not change ("==" did not work well with float)
        if np.allclose([nc1, nc2], [c1, c2]):
            break

        c1, c2 = nc1, nc2

    return cluster1, cluster2


def levelwise_split(data, minimal_number_of_clusters):
    clusters = [data]
    depth = int(np.ceil(np.log2(minimal_number_of_clusters)))

    for _ in range(depth):
        new_clusters = []
        for cluster in clusters:
            cluster1, cluster2 = split(cluster)
            new_clusters.extend([cluster1, cluster2])
        clusters = new_clusters

    visualize_clusters(clusters, "Hierarchical binary clustering")
    return clusters


def greedy_split(data, number_of_clusters):
    clusters = [data]

    while len(clusters) < number_of_clusters:
        # which cluster should be split
        scores = [np.sum((c - c.mean(axis=0))**2) if len(c)
                  else 0 for c in clusters]
        i = np.argmax(scores)

        cluster = clusters.pop(i)  # take cluster from clusters list
        cluster1, cluster2 = split(cluster)  # make new clusters

        clusters.extend([cluster1, cluster2])  # put them back to list

    visualize_clusters(clusters, "Greedy clustering")
    return clusters


def visualize_clusters(clusters, title):
    X = np.vstack(clusters)
    labels = np.concatenate([np.full(len(c), i)
                            for i, c in enumerate(clusters)])

    plt.scatter(X[:, 0], X[:, 1], c=labels, cmap="tab20", s=30, alpha=0.8)
    plt.title(title)
    plt.show()
