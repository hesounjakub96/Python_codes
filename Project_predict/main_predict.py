import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error as MSE


def add_new_cols(data):
    """
    add new useful cols in data for a prediction:
    - previous price
    - simple moving avg (1h and 3h)
    - hour
    - sin(2*pi*hour/24)  "sine on day" 
    """
    data["price_t_minus_1"] = data["price_eur"].shift(1)
    data["ma_1h"] = data["price_eur"].rolling("1h").mean()
    data["ma_3h"] = data["price_eur"].rolling("3h").mean()
    data["hour"] = data.index.hour
    data["hour_sin"] = np.sin(2 * np.pi * data.index.hour / 24)

    return data


data = pd.read_csv("energy_clean_data.csv", parse_dates=["timestamp"])
data = data.set_index("timestamp")

fig, ax = plt.subplots(2, 1, figsize=(12, 6))
ax[0].plot(data.index, data["price_eur"])
ax[0].set_title("Train data")

data = add_new_cols(data)

X = data.dropna().drop("price_eur", axis=1)
y = data.loc[X.index, "price_eur"]

model = RandomForestRegressor(
    n_estimators=10,
    max_depth=10,
    random_state=42
)

# model = LinearRegression()
model.fit(X, y)

data_test = pd.read_csv("energy_clean_data_test.csv",
                        parse_dates=["timestamp"])
data_test = data_test.set_index("timestamp")

data_test = add_new_cols(data_test)

X_test = data_test.dropna().drop("price_eur", axis=1)
y_test = data_test["price_eur"]
y_pred = model.predict(X_test)


ax[1].plot(data_test.index, data_test["price_eur"],
           label="True price", color="blue")
ax[1].plot(X_test.index, y_pred,
           label="Predicted price", color="red", linestyle="--")

ax[1].legend()
ax[1].set_title("Test data: true vs. predicted price")

mse = MSE(y_test[1:], y_pred)
rmse = np.sqrt(mse).round(2)

print(f"RMSE of predicted true and predicted price: {rmse}")

# testing strategy
cash = 0
amount = 0
trades = 0

theta1 = 0.05  # threshlods for buying/selling
theta2 = 0.02
for i in range(len(y_pred) - 1):

    current_price = y_test.iloc[i]
    future_price = y_test.iloc[i+1]
    predicted_future = y_pred[i]

    expected_return = (predicted_future - current_price) / current_price

    if expected_return > theta1:  # buy
        cash -= 2*current_price
        amount += 2
        trades += 2
    elif expected_return > theta2:
        cash -= current_price
        amount += 1
        trades += 1
    elif expected_return < -0.15 and amount > 0:  # sell (if you can)
        cash += amount*current_price
        trades += amount
        amount = 0
    elif expected_return < -theta1 and amount > 1:  # sell (if you can)
        cash += 2*current_price
        amount -= 2
        trades += 2
    elif expected_return < -theta2 and amount > 0:  # sell (if you can)
        cash += current_price
        amount -= 1
        trades += 1

# konečná hodnota portfolia
final_value = cash + amount * y_test.iloc[-1]

print("Trades:", trades)
print("Final value:", final_value)
print("Cash:", cash)
print("amount:", amount)

plt.tight_layout()
plt.show()
