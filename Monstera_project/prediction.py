import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import GroupShuffleSplit
from sklearn.base import BaseEstimator
from preprocess import lag_features_for_plant, invert_prediction

PLANT_CATEGORICAL = [
    "cultivar",
    "growing_medium",
    "light_type"
]


def make_prediction(plant_id: int,
                    df: pd.DataFrame,
                    encoders: dict[str, LabelEncoder],
                    model: BaseEstimator,
                    X_features: pd.DataFrame,
                    strategy: dict) -> pd.DataFrame:

    plant_history = df[df["plant_id"] == plant_id]

    X_new = _build_prediction_row(
        plant_history=plant_history,
        encoders=encoders,
        n_lags=3,
        days_since_acq_target=30
    )

    # Sort_features
    X_new_ready = X_new[X_features.columns]
    # predict new leaf
    y_pred_diff = model.predict(X_new_ready)

    last_known_leaf = plant_history.sort_values("leaf_order").iloc[-1]

    pred_df = invert_prediction(
        predicted_diff=y_pred_diff[0],
        last_known_values=last_known_leaf,
        method=strategy
    )

    # clean number of fenestrations
    for col in ["outer_fenestration_count", "inner_fenestration_count"]:
        pred_df[col] = pred_df[col].clip(lower=0).round().astype(int)

    encoded_cultivar = X_new["cultivar"].iloc[0]
    encoded_medium = X_new["growing_medium"].iloc[0]
    encoded_light = X_new["light_type"].iloc[0]
    p_id = X_new["plant_id"].iloc[0]

    cultivar_text = encoders["cultivar"].inverse_transform(
        [encoded_cultivar])[0] if encoded_cultivar != -1 else "Unknown"
    medium_text = encoders["growing_medium"].inverse_transform(
        [encoded_medium])[0] if encoded_medium != -1 else "Unknown"
    light_text = encoders["light_type"].inverse_transform(
        [encoded_light])[0] if encoded_light != -1 else "Unknown"

    print("Predicting:")
    print(f"Plant ID: {p_id}")
    print(f"Cultivar:    {cultivar_text}")
    print(f"Soil:      {medium_text}")
    print(f"Light:   {light_text}")
    print("-------------------")
    print(pred_df)
    print("-------------------")

    return pred_df


def _build_prediction_row(
    plant_history: pd.DataFrame,
    encoders: dict[str, LabelEncoder],
    n_lags: int = 3,
    days_since_acq_target: float = None
) -> pd.DataFrame:

    if len(plant_history) < n_lags:
        raise ValueError(
            f"Need at least {n_lags} historical leaves; got {len(plant_history)}"
        )

    first_row = plant_history.iloc[0]

    actual_meta = {}
    for col in PLANT_CATEGORICAL:
        actual_meta[col] = first_row[col]

    plant_id = first_row["plant_id"]

    dummy = plant_history.iloc[[-1]].copy()
    dummy["leaf_order"] += 1
    # the dummy row is a new leaf which will be predicted
    extended = pd.concat([plant_history, dummy], ignore_index=True)

    lag_df = lag_features_for_plant(extended, n_lags=n_lags)
    row = lag_df.iloc[[-1]].copy()

    for col in PLANT_CATEGORICAL:
        val = str(actual_meta.get(col, "unknown"))
        if col in encoders:
            try:
                row[col] = encoders[col].transform([val])[0]
            except ValueError:
                row[col] = -1  # unseen label
        else:
            row[col] = val

    row["plant_id"] = plant_id
    row["days_since_acq_target"] = days_since_acq_target or np.nan

    return row
