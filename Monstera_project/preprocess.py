import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import GroupShuffleSplit


def new_features(df: pd.DataFrame) -> pd.DataFrame:
    df["area_cm2"] = df["length_cm"] * df["width_cm"]
    df["total_fenestration"] = df["outer_fenestration_count"] + \
        df["inner_fenestration_count"]
    df = df.sort_values(["plant_id", "leaf_order"]).reset_index(drop=True)
    # might be usefull - plant shop conditions are unknown, but for this amount of day, it is in known place
    df["days_since_acq"] = (df["matured_at"] - df["acquired_at"]).dt.days

    return df


LEAF_NUMERIC = [
    "width_cm",
    "length_cm",
    "area_cm2",
    "outer_fenestration_count",
    "inner_fenestration_count",
    "total_fenestration",
    "days_since_acq"
]

TARGETS = [
    "length_cm",
    "width_cm",
    "outer_fenestration_count",
    "inner_fenestration_count",
]

PLANT_CATEGORICAL = [
    "cultivar",
    "growing_medium",
    "light_type"
]


def lag_features_for_plant(group: pd.DataFrame, n_lags: int = 3) -> pd.DataFrame:
    rows = []
    arr = group[LEAF_NUMERIC].values  # shape (n_leaves, n_features)
    orders = group["leaf_order"].values

    for i in range(n_lags, len(group)):
        row: dict = {}

        row["leaf_order"] = int(orders[i])

        for lag in range(1, n_lags + 1):
            idx = i - lag
            for j, col in enumerate(LEAF_NUMERIC):
                row[f"{col}_lag{lag}"] = arr[idx, j]

        window = arr[:i]
        for j, col in enumerate(LEAF_NUMERIC):
            row[f"{col}_rollmean"] = np.nanmean(window[:, j])
            row[f"{col}_rollstd"] = np.nanstd(window[:, j])
            row[f"{col}_rollmax"] = np.nanmax(window[:, j])

        for col in ["length_cm", "width_cm", "total_fenestration"]:
            j = LEAF_NUMERIC.index(col)
            prev = arr[i - 1, j]
            prev2 = arr[i - 2, j]
            row[f"{col}_growth_rate"] = (
                (prev - prev2) / prev2 if prev2 != 0 else 0.0)

        rows.append(row)

    return pd.DataFrame(rows)


def build_feature_matrix(
    df: pd.DataFrame,
    n_lags: int = 3,
    encode_categoricals: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, LabelEncoder]]:
    df = df.sort_values(["plant_id", "leaf_order"]).reset_index(drop=True)

    feature_parts = []
    target_parts = []

    for plant_id, group in df.groupby("plant_id"):
        group = group.reset_index(drop=True)

        if len(group) <= n_lags:
            # we need atleas n_lags leaves
            continue

        # for each leaf with atleast n_lags previous leaves create row with roll features
        lag_df = lag_features_for_plant(group, n_lags=n_lags)

        plant_row = group.iloc[0]
        for col in PLANT_CATEGORICAL:
            lag_df[col] = plant_row[col]
        lag_df["plant_id"] = plant_id
        lag_df["days_since_acq_target"] = group["days_since_acq"].values[n_lags:]

        # Targets y
        tgt_df = group[TARGETS].iloc[n_lags:].reset_index(drop=True)

        feature_parts.append(lag_df.reset_index(drop=True))
        target_parts.append(tgt_df)

    X = pd.concat(feature_parts, ignore_index=True)
    y = pd.concat(target_parts,  ignore_index=True)

    # Label-encode categoricals
    encoders: dict[str, LabelEncoder] = {}
    if encode_categoricals:
        for col in PLANT_CATEGORICAL:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            encoders[col] = le

    # Drop any rows where ALL lag-1 values are NaN (edge case)
    lag1_cols = [c for c in X.columns if c.endswith("_lag1")]
    mask = X[lag1_cols].notna().any(axis=1)
    X = X[mask].reset_index(drop=True)
    y = y[mask].reset_index(drop=True)

    return X, y, encoders

# this is an old function which prepared split - now i use logo


def prepare_split(df: pd.DataFrame):
    X, y, encoders = build_feature_matrix(df)

    splitter = GroupShuffleSplit(
        n_splits=1, test_size=0.1, random_state=13
    )
    train_idx, test_idx = next(splitter.split(X, y, groups=X["plant_id"]))

    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    print(
        f"   Train plants: {X_train['plant_id'].nunique()}  "
        f"({len(X_train)} samples)  |  "
        f"Test plants: {X_test['plant_id'].nunique()}  "
        f"({len(X_test)} samples)"
    )

    return X_train, X_test, y_train, y_test, encoders


def transform_target(
    df_x: pd.DataFrame,
    df_y: pd.DataFrame,
    method: dict
) -> pd.DataFrame:
    y_transformed = pd.DataFrame(index=df_y.index)

    for col, mode in method.items():
        if mode == "ratio":
            y_transformed[col] = df_y[col] / df_x[f"{col}_lag1"]
        elif mode == "diff":
            y_transformed[col] = df_y[col] - df_x[f"{col}_lag1"]

    return y_transformed


def invert_prediction(predicted_diff: np.ndarray, last_known_values: pd.Series, method: dict) -> pd.DataFrame:
    # 1. Zajištění plochého pole (oprava dimenze 1,1,4 -> 4)
    predicted_diff = np.array(predicted_diff).flatten()

    final_preds = {}
    for i, (col, mode) in enumerate(method.items()):
        lag_col = f"{col}_lag1" if f"{col}_lag1" in last_known_values else col
        last_val = last_known_values[lag_col]
        pred_val = predicted_diff[i]

        if mode == "ratio":
            val = float(last_val * pred_val)
        elif mode == "diff":
            val = float(last_val + pred_val)

        # Zaokrouhlení pro fenestrace (pokud jsou to inty)
        if "fenestration" in col:
            val = round(val)

        final_preds[col] = val

    # Tady vracíme DataFrame vytvořený z jednoho řádku
    return pd.DataFrame([final_preds])
