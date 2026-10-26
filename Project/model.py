"""
Train, calibrate, save and load the models (sector PCA plus XGBoost)
"""
import os
from dataclasses import dataclass

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler

import config
import features

# Use relatively conservative settings because the data is small and noisy
XGB_PARAMS = dict(
    n_estimators=300, max_depth=3, learning_rate=0.03, subsample=0.8, colsample_bytree=0.7,
    min_child_weight=20, reg_alpha=1.0, reg_lambda=5.0, eval_metric="logloss",
)


def fit_pca(sector_returns: pd.DataFrame, n_components: int = config.N_PCA) -> Pipeline:
    """
    Fit PCA on standardized sector returns, flipping signs so each factor points the same way on every refit
    """
    pipe = make_pipeline(StandardScaler(), PCA(n_components=n_components))
    pipe.fit(sector_returns.dropna())
    pca = pipe[-1]
    signs = np.where(pca.components_.sum(axis=1) < 0, -1.0, 1.0)
    pca.components_ *= signs[:, None]
    return pipe


def pca_features(pipe: Pipeline, sector_returns: pd.DataFrame) -> pd.DataFrame:
    """
    Daily factor returns from a fitted PCA, summed over 5 and 20 days.
    """
    clean = sector_returns.dropna()
    names = [f"pc{i + 1}" for i in range(pipe[-1].n_components_)]
    scores = pd.DataFrame(pipe.transform(clean), index=clean.index, columns=names)
    out = pd.concat([scores.rolling(5).sum().add_suffix("_5d"),
                     scores.rolling(20).sum().add_suffix("_20d")], axis=1)
    return out.add_prefix("pca_")


def fit_factor_pca(stock_returns: pd.DataFrame, n_components: int = config.N_FACTORS) -> Pipeline:
    """
    Fit PCA on standardized energy-stock returns.
    Signs are set so F1 is the whole sector and F2 reads as clean energy minus traditional/oil.
    """
    pipe = make_pipeline(StandardScaler(), PCA(n_components=n_components))
    pipe.fit(stock_returns.dropna())
    names = list(pipe.feature_names_in_)
    clean = [names.index(t) for t in config.FACTOR_UNIVERSE["clean"] if t in names]
    traditional = [names.index(t) for t in config.FACTOR_UNIVERSE["traditional"] if t in names]
    components = pipe[-1].components_
    for i in range(len(components)):
        tilt = components[i].sum() if i == 0 else components[i, clean].mean() - components[i, traditional].mean()
        if tilt < 0:
            components[i] *= -1
    return pipe


def factor_scores(pipe: Pipeline, stock_returns: pd.DataFrame) -> pd.DataFrame:
    clean = stock_returns.dropna()
    names = [f"f{i + 1}" for i in range(pipe[-1].n_components_)]
    return pd.DataFrame(pipe.transform(clean), index=clean.index, columns=names)


def factor_variance_shares(pipe: Pipeline, stock_returns: pd.DataFrame, window: int = 60) -> pd.DataFrame:
    """
    Share of recent stock movement explained by each factor (a rising F2 share means clean and oil are splitting apart)
    """
    clean = stock_returns.dropna()
    standardized = pd.DataFrame(pipe[0].transform(clean), index=clean.index)
    total = standardized.rolling(window).var().sum(axis=1)
    return factor_scores(pipe, stock_returns).rolling(window).var().div(total, axis=0)


def factor_features(pipe: Pipeline, stock_returns: pd.DataFrame) -> pd.DataFrame:
    """
    Recent factor returns and variance shares from a fitted energy-stock PCA.
    """
    scores = factor_scores(pipe, stock_returns)
    out = pd.concat([scores.rolling(5).sum().add_suffix("_5d"),
                     scores.rolling(20).sum().add_suffix("_20d"),
                     factor_variance_shares(pipe, stock_returns).add_suffix("_share60")], axis=1)
    return out.add_prefix("factor_")


def time_decay_weights(index: pd.DatetimeIndex, half_life_years: float | None = config.HALF_LIFE_YEARS) -> np.ndarray:
    """
    Weight 1 for the newest row, halving every half_life_years.
    None gives equal weights.
    """
    if half_life_years is None:
        return np.ones(len(index))
    age_years = np.asarray((index.max() - index).days) / 365.25
    return 0.5 ** (age_years / half_life_years)


def make_classifier(kind: str = "xgb"):
    if kind == "xgb":
        return xgb.XGBClassifier(**XGB_PARAMS)
    # Logistic regression, mostly for comparison/testing
    if kind == "logit":
        return make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                             LogisticRegression(C=0.1, max_iter=1000))
    raise ValueError(f"unknown classifier kind: {kind}")


def fit_classifier(classifier, X: pd.DataFrame, y: pd.Series, weights: np.ndarray):
    if isinstance(classifier, Pipeline):
        classifier.fit(X, y, logisticregression__sample_weight=weights)
    else:
        classifier.fit(X, y, sample_weight=weights)
    return classifier


def _logit(probs: np.ndarray) -> np.ndarray:
    probs = np.clip(probs, 1e-6, 1 - 1e-6)
    return np.log(probs / (1 - probs)).reshape(-1, 1)


def fit_calibrator(raw_probs: np.ndarray, y: pd.Series) -> LogisticRegression:
    """
    Uses Platt scaling, essentially a logistic regression that maps raw model probabilities to calibrated ones. It aims to rescale the model but should never flip its direction entirely.
    If the fit would flip it, it predicts using the base rate instead.
    """
    calibrator = LogisticRegression().fit(_logit(raw_probs), y)
    if calibrator.coef_[0, 0] <= 0:
        base_rate = float(np.clip(np.mean(y), 1e-3, 1 - 1e-3))
        calibrator.coef_[:] = 0.0
        calibrator.intercept_[:] = np.log(base_rate / (1 - base_rate))
    return calibrator


def apply_calibrator(calibrator: LogisticRegression | None, raw_probs: np.ndarray) -> np.ndarray:
    return raw_probs if calibrator is None else calibrator.predict_proba(_logit(raw_probs))[:, 1]


# Include Nones largely for checking against raw and seeing if these fancy additions actually help
@dataclass
class AssetModel:
    ticker: str
    feature_columns: list[str]
    pca: Pipeline | None
    classifier: object
    calibrator: LogisticRegression | None
    factor_pca: Pipeline | None = None

    def design_matrix(self, base: pd.DataFrame, sector_returns: pd.DataFrame,
                      stock_returns: pd.DataFrame | None = None) -> pd.DataFrame:
        X = base
        if self.pca is not None:
            X = X.join(pca_features(self.pca, sector_returns))
        if self.factor_pca is not None:
            X = X.join(factor_features(self.factor_pca, stock_returns))
        return X[self.feature_columns]

    def predict_proba(self, base: pd.DataFrame, sector_returns: pd.DataFrame,
                      stock_returns: pd.DataFrame | None = None) -> pd.Series:
        X = self.design_matrix(base, sector_returns, stock_returns)
        raw = self.classifier.predict_proba(X)[:, 1]
        return pd.Series(apply_calibrator(self.calibrator, raw), index=X.index, name=self.ticker)


def prune_correlated(X: pd.DataFrame, threshold: float = config.CORR_THRESHOLD) -> list[str]:
    """
    Drop mostly-empty columns and near-duplicates of columns already kept
    """
    X = X.loc[:, X.notna().mean() > 0.5]
    correlation = X.corr(method="spearman").abs()
    kept = []
    for column in X.columns:
        if all(correlation.at[column, other] <= threshold for other in kept):
            kept.append(column)
    return kept


def select_features(data: pd.DataFrame, columns: list[str], max_features: int = config.MAX_FEATURES,
                    half_life_years: float | None = config.HALF_LIFE_YEARS, validation_share: float = 0.3) -> list[str]:
    """
    Keep the features that most help AUC on the last 30% of the training data, after dropping near-duplicates.
    Runs inside each training window, so it never sees test data.
    """
    columns = prune_correlated(data[columns])
    validation_start = data.index[int(len(data) * (1 - validation_share))]

    # Drop the last HORIZON_DAYS rows before validation so fit labels can't see validation prices
    fit_rows = data.loc[:validation_start].iloc[:-config.HORIZON_DAYS].dropna(subset=["y_fit"])
    validation = data.loc[validation_start:]

    # Fit on y_fit (training labels), score on y_all (every day labelled)
    classifier = fit_classifier(make_classifier("xgb"), fit_rows[columns], fit_rows["y_fit"],
                                time_decay_weights(fit_rows.index, half_life_years))
    
    # Shuffle each feature on the validation rows and measure how much AUC drops
    importance = permutation_importance(classifier, validation[columns], validation["y_all"],
                                        scoring="roc_auc", n_repeats=5, random_state=0)
    ranked = pd.Series(importance.importances_mean, index=columns).sort_values(ascending=False)

    # Keep features that helped; if none did, keep the top max_features anyway
    keep = ranked[ranked > 0].index[:max_features].tolist()
    return keep or ranked.index[:max_features].tolist()


def train_asset_model(base: pd.DataFrame, sector_returns: pd.DataFrame, close: pd.DataFrame,
                      ticker: str, train_end, groups=None, kind: str = config.CLASSIFIER,
                      dead_zone: float = config.DEAD_ZONE,
                      max_features: int | None = config.MAX_FEATURES,
                      half_life_years: float | None = config.HALF_LIFE_YEARS,
                      calibrate: bool = True, stock_returns: pd.DataFrame | None = None) -> AssetModel:
    """
    Fit PCA, feature selection, classifier and calibrator for one ticker, using only data up to train_end.
    """
    groups = list(groups or config.DEFAULT_GROUPS)
    train_end = pd.Timestamp(train_end)

    pca, X = None, base
    if "pca" in groups:
        pca = fit_pca(sector_returns.loc[:train_end])
        X = base.join(pca_features(pca, sector_returns))
    factor_pca = None
    if "factors" in groups:
        if stock_returns is None:
            raise ValueError("the 'factors' group needs stock_returns (data_loader.fetch_factor_universe)")
        factor_pca = fit_factor_pca(stock_returns.loc[:train_end])
        X = X.join(factor_features(factor_pca, stock_returns))
    columns = features.select_columns(X.columns, groups)

    # y_fit skips near-zero moves for training; y_all labels every day for validation and calibration
    data = X[columns].assign(y_all=features.make_target(close, ticker),
                          y_fit=features.make_target(close, ticker, dead_zone=dead_zone))
    
    # Drop the last HORIZON_DAYS rows: their labels look past train_end
    data = data.loc[:train_end].iloc[:-config.HORIZON_DAYS].dropna(subset=["y_all"])

    # Hold out the last CALIBRATION_YEARS for calibration, with a HORIZON_DAYS gap
    calibration_start = data.index.max() - pd.DateOffset(years=config.CALIBRATION_YEARS)
    fit_part = data.loc[:calibration_start].iloc[:-config.HORIZON_DAYS]
    calibration_part = data.loc[calibration_start:]

    if max_features:
        columns = select_features(fit_part, columns, max_features, half_life_years)

    fit_rows = fit_part.dropna(subset=["y_fit"])
    classifier = fit_classifier(make_classifier(kind), fit_rows[columns], fit_rows["y_fit"],
                                time_decay_weights(fit_rows.index, half_life_years))
    calibrator = None
    if calibrate:
        calibrator = fit_calibrator(classifier.predict_proba(calibration_part[columns])[:, 1], calibration_part["y_all"])
    return AssetModel(ticker, columns, pca, classifier, calibrator, factor_pca)


# TODO: Not sure if this is the best, check against gitignore as well
def save_models(models: dict, directory: str = config.MODEL_DIR) -> str:
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, "models.joblib")
    joblib.dump(models, path)
    return path


def load_models(directory: str = config.MODEL_DIR) -> dict:
    return joblib.load(os.path.join(directory, "models.joblib"))
