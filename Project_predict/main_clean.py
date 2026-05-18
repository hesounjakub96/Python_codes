import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = pd.read_csv("energy_data.csv", parse_dates=["timestamp"])
data = data.set_index("timestamp")

fig, ax = plt.subplots(2, 2, figsize=(12, 6))

ax[0, 0].plot(data.index, data["price_eur"])
ax[0, 0].set_title("price_eur")
ax[0, 1].plot(data.index, data["load_mw"])
ax[0, 1].set_title("load_mw")


print(data["price_eur"].describe())
print(data["price_eur"].isna().sum())

data["price_eur"] = data["price_eur"].interpolate(method="linear")
print(data.head())
Q1 = np.quantile(data["load_mw"], .25)
Q3 = np.quantile(data["load_mw"], .75)
IQR = Q3 - Q1
lower = Q1 - 1.5*IQR
upper = Q3 + 1.5*IQR

print(data["load_mw"].describe())

mask = (data["load_mw"] < lower) | (data["load_mw"] > upper)

data.loc[mask, "load_mw"] = (
    data["load_mw"].shift(1) + data["load_mw"].shift(-1)
) / 2


data["hour"] = data.index.hour
data["price_sma_12"] = data["price_eur"].rolling(window=12).mean()


data["price_t_minus_1"] = data["price_eur"].shift(1)

ax[1, 0].plot(data.index, data["price_eur"])
ax[1, 0].set_title("price_eur")
ax[1, 1].plot(data.index, data["load_mw"])
ax[1, 1].set_title("load_mw")

print(data)
fig.text(0.5, 0.92, "Original data", ha='center', fontsize=12)
fig.text(0.5, 0.42, "Clean data", ha='center', fontsize=12)
plt.tight_layout(rect=[0, 0, 1, 0.9])
plt.show()
