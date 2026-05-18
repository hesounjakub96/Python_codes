import pandas as pd
import numpy as np

dates = pd.date_range(start="2023-01-01", periods=100, freq="h")
np.random.seed(42)

load = 500 + 100 * np.sin(np.linspace(0, 10, 100)) + \
    np.random.normal(0, 10, 100)
price = 500-load * 0.5 + np.random.normal(0, 5, 100)

df = pd.DataFrame({"timestamp": dates, "load_mw": load, "price_eur": price})

df.loc[5:7, "price_eur"] = np.nan  # missing values
df.loc[[20, 35, 80], "load_mw"] = 1000       # Outlier

df.to_csv("energy_data.csv", index=False)
print("Data uložena do energy_data.csv")
