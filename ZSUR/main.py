import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from clusters_counts import hladiny_simple, retez_mapy, maximim
from clustering import levelwise_split, greedy_split
from classificators import bayes_n, knn_n, train_linear_classifier

data = pd.read_csv("data.txt", names=["x", "y"], sep=" ")
data = np.asarray(data)

plt.scatter(data[:, 0], data[:, 1])
plt.title("Data")
plt.show()

n1 = hladiny_simple(data)
print("Počet skupin dle prosté hladiny:", n1)
n2 = retez_mapy(data)
print("Počet skupin dle řetězové mapy:", n2)
n3 = maximim(data)
print("Počet skupin dle MaxiMin:", n3)

n = round((n1 + n2 + n3)/3)
print("Finální počet skupin:", n)

levelwise_split(data, n)
clusters = greedy_split(data, n)

bayes_n(clusters)
knn_n(clusters)  # slow..

train_linear_classifier(clusters)
train_linear_classifier(clusters, method="mkp")
train_linear_classifier(clusters, method="umkp")
