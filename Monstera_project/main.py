import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import mean_squared_error as MSE
from prediction import make_prediction
from preprocess import new_features, build_feature_matrix, transform_target, invert_prediction

df = pd.read_csv("data2.csv",  parse_dates=["matured_at", "acquired_at"])
df = new_features(df)

X, y, encoders = build_feature_matrix(df)
X_features = X.drop(columns=["plant_id"])

# predict growth factor for size and difference of nu,ber of fenestration
# this should overcome my problems with decision trees - it cannot predict higher values then it already seen
strategy = {
    "length_cm": "ratio",
    "width_cm": "ratio",
    "outer_fenestration_count": "diff",
    "inner_fenestration_count": "diff"
}

y_transformed = transform_target(X, y, strategy)

base_xgb = XGBRegressor(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.05,
    n_jobs=-1
)
model = MultiOutputRegressor(base_xgb)


# Train and validate model using logo - leave one group out
logo = LeaveOneGroupOut()

rmse_scores = []
groups = X["plant_id"].values

for train_idx, test_idx in logo.split(X, y_transformed, groups=groups):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y_transformed.iloc[train_idx], y_transformed.iloc[test_idx]

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_pred[:, 2:] = np.round(y_pred[:, 2:])

    y_pred_list = []
    y_test_list = []
    for i in range(len(y_test)):
        y_pred_list.append(invert_prediction(
            y_pred[i], X_test.iloc[i], strategy))
        y_test_list.append(invert_prediction(
            y_test.iloc[i].values, X_test.iloc[i], strategy))

    y_pred_df = pd.concat(y_pred_list, ignore_index=True)
    y_test_df = pd.concat(y_test_list, ignore_index=True)

    mse = MSE(y_test_df, y_pred_df, multioutput='raw_values')
    rmse = np.sqrt(mse)
    rmse_scores.append(rmse)

rmse_scores = np.array(rmse_scores)

rmse_scores[:, 2:] = np.round(rmse_scores[:, 2:])
rmse_mean_by_feature = np.mean(rmse_scores, axis=0)
print(f"RMSE pro jednotlivé rostliny:\n{np.round(rmse_scores, 2)}")
print(
    f"Průměrná chyba délky: {np.mean(rmse_mean_by_feature[0]):.2f} cm")
print(
    f"Průměrná chyba šířky: {np.mean(rmse_mean_by_feature[1]):.2f} cm")

# I know the model works "well" on train&test set - but i have only few data. so lets train the model on all of them and hope for not overfitting
model.fit(X_features, y_transformed)

pred = make_prediction(3, df, encoders, model, X_features, strategy)
# for i in df['plant_id'].unique().tolist():
#     pred = make_prediction(i, df, encoders, model, X_features, strategy)
