import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import multivariate_normal


def bayes_n(clusters):
    clusters = [np.array(c) for c in clusters]

    all_points = np.vstack(clusters)

    priors = [len(cluster) / len(all_points) for cluster in clusters]

    mus = [cluster.mean(axis=0) for cluster in clusters]
    covs = [
        np.cov(c.T) + 1e-6 * np.eye(c.shape[1])  # regularizace
        for c in clusters
    ]

    xmin, xmax = all_points[:, 0].min(), all_points[:, 0].max()
    ymin, ymax = all_points[:, 1].min(), all_points[:, 1].max()
    x = np.arange(xmin, xmax, 0.05)
    y = np.arange(ymin, ymax, 0.05)
    X, Y = np.meshgrid(x, y)
    grid = np.c_[X.ravel(), Y.ravel()]

    probs = np.zeros((len(grid), len(clusters)))

    for i, (mu, cov, p) in enumerate(zip(mus, covs, priors)):
        rv = multivariate_normal(mean=mu, cov=cov)
        probs[:, i] = rv.pdf(grid) * p

    labels = np.argmax(probs, axis=1)

    plt.scatter(grid[:, 0], grid[:, 1], c=labels, cmap="tab20", s=5, alpha=0.3)

    for c in clusters:
        plt.scatter(c[:, 0], c[:, 1], s=10, c="black")

    plt.title("Bayesův klasifikátor (N tříd)")
    plt.show()


def knn_n(clusters, K=1):
    clusters = [np.array(cluster) for cluster in clusters]

    X_train = np.vstack(clusters)
    y_train = np.hstack([
        np.full(len(c), i) for i, c in enumerate(clusters)
    ])

    x1 = np.arange(X_train[:, 0].min(), X_train[:, 0].max(), 0.05)
    x2 = np.arange(X_train[:, 1].min(), X_train[:, 1].max(), 0.05)

    X1, X2 = np.meshgrid(x1, x2)
    grid = np.c_[X1.ravel(), X2.ravel()]

    labels = np.zeros(len(grid))

    for j, point in enumerate(grid):

        dists = np.sum((X_train - point)**2, axis=1)

        knn_idx = np.argsort(dists)[:K]
        knn_labels = y_train[knn_idx]

        labels[j] = np.bincount(knn_labels).argmax()

    plt.scatter(grid[:, 0], grid[:, 1], c=labels, s=5, alpha=0.3)
    plt.scatter(X_train[:, 0], X_train[:, 1], c="black", s=10)
    plt.title(f"{K}-NN klasifikátor")
    plt.show()


def train_linear_classifier(clusters, method="rosenblatt", max_iter=500, beta=1.0, delta=0.1):

    num_clusters = len(clusters)
    X_list = []
    y_list = []

    for i, cluster in enumerate(clusters):
        X_list.append(np.array(cluster))
        y_list.append(np.full(len(cluster), i))

    X = np.vstack(X_list)
    y = np.concatenate(y_list)  # labels

    # points [x,y] as vector [1,x,y] -> dot product and
    X_aug = np.hstack([np.ones((X.shape[0], 1)), X])

    all_weights = []
    iterations_log = []

    # ONE-vs-ALL
    for k in range(num_clusters):
        # for cluster k set 1 for other clusters -1
        y_binary = np.where(y == k, 1, -1)

        w = np.array([0.0, 1.0, 1.0])  # normal of starting line 0+1*x+1*y=0

        converged = False
        for epoch in range(max_iter):
            errors = 0
            # randomize order of X_aug - otherwise might "jump" between two points
            indices = np.random.permutation(len(X_aug))

            for idx in indices:
                xi = X_aug[idx]
                yi = y_binary[idx]

                # dot product >0 (<) and yi =1(-1); if different signs we need update
                projection = np.dot(w, xi) * yi

                update_needed = False
                if method == "rosenblatt":
                    if projection <= 0:
                        update_needed = True
                        update_step = beta * yi * xi

                elif method == "mkp" or method == "umkp":
                    if projection < delta:
                        update_needed = True
                        norm_sq = np.sum(xi**2)
                        update_step = (
                            beta * (delta - projection) / norm_sq) * (yi * xi)

                        if method == "umkp":
                            while np.dot(w + update_step, xi) * yi < delta:  # update until < delta
                                w += update_step
                                if np.linalg.norm(update_step) < 1e-6:
                                    break

                if update_needed:
                    w += update_step
                    errors += 1

            if errors == 0:
                iterations_log.append(epoch + 1)
                converged = True
                break

        if not converged:
            iterations_log.append(max_iter)

        all_weights.append(w)

    print(
        f"Metoda {method.upper()} doběhla. Iterace pro clustery: {iterations_log}")

    plot_results(clusters, all_weights, f"{method.upper()}")
    return all_weights


def plot_results(clusters, weights, title):
    plt.figure(figsize=(10, 7))
    colors = ["red", "blue", "green", "purple", "orange", "cyan"]

    for i, cluster in enumerate(clusters):
        plt.scatter(cluster[:, 0], cluster[:, 1], c=colors[i %
                    len(colors)], marker="x", label=f"Cluster {i}")

    ax = plt.gca()
    x_vals = np.array(ax.get_xlim())

    for w in weights:
        # w0 + w1*x + w2*y = 0  =>  y = -(w1*x + w0) / w2
        if w[2] != 0:
            y_vals = -(w[1] * x_vals + w[0]) / w[2]
            plt.plot(x_vals, y_vals, "--k", alpha=0.7)

    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()
