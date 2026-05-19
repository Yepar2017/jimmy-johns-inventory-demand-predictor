import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error
from sklearn.ensemble import GradientBoostingRegressor
import joblib

IN_PATH = Path("data/processed/bread_daily_est_2025.csv")
MODEL_PATH = Path("models/daily_bread_model.joblib")

def make_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("date").copy()
    df["dow"] = df["date"].dt.dayofweek
    df["lag_1"] = df["bread_used_est"].shift(1)
    df["roll7"] = df["bread_used_est"].rolling(7).mean()
    df["sales_roll7"] = df["total_sales"].rolling(7).mean()
    df = df.dropna().copy()
    return df

def main():
    df = pd.read_csv(IN_PATH)
    df["date"] = pd.to_datetime(df["date"])

    df = make_features(df)

    features = ["total_sales", "dow", "lag_1", "roll7", "sales_roll7"]
    X = df[features]
    y = df["bread_used_est"]

    tscv = TimeSeriesSplit(n_splits=5)
    maes = []

    model = GradientBoostingRegressor(random_state=42)

    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        maes.append(mean_absolute_error(y_test, preds))

    print("MAE (folds):", [round(m, 2) for m in maes])
    print("MAE avg:", round(float(np.mean(maes)), 2))

    # fit final model on all data
    model.fit(X, y)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": features}, MODEL_PATH)
    print("Saved model:", MODEL_PATH)

if __name__ == "__main__":
    main()
