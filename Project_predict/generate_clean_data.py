import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

len = 96
dates = pd.date_range(start="2023-01-01", periods=len, freq="15min")
# np.random.seed(42)

# ------------ train data --------------

load = 500 + 100 * np.sin(np.linspace(0, 10, len)) + 25 * np.sin(np.linspace(0, 50, len)) + \
    np.random.normal(0, 10, len)
price = 500-load * 0.5 + \
    np.random.normal(0, 5, len) + 4*np.linspace(0, 10, len)

df = pd.DataFrame({"timestamp": dates, "load_mw": load, "price_eur": price})

df.to_csv("energy_clean_data.csv", index=False)

plt.plot(dates, price)
plt.show()

# ----------- test data ---------------------

dates = pd.date_range(start="2023-01-02", periods=len, freq="15min")

load = 500 + 100 * np.sin(np.linspace(0, 10, len)) + 25 * np.sin(np.linspace(0, 50, len)) + \
    np.random.normal(0, 10, len)
price = 500-load * 0.5 + \
    np.random.normal(0, 5, len) + 4*np.linspace(0, 10, len)

df = pd.DataFrame({"timestamp": dates, "load_mw": load, "price_eur": price})

df.to_csv("energy_clean_data_test.csv", index=False)

plt.plot(dates, price)
plt.show()
