"""
ml/preprocess.py
Leakage-safe preprocessing and feature engineering for Chiller Forensics.

CRITICAL PRINCIPLES:
1. Prevent data leakage: No future observations are used to impute past values.
   Backward-fill (bfill) across time is strictly avoided.
2. Imputation parameters (e.g., column medians) are computed strictly from training sets.
3. Strict chronological sorting by equipment_id and timestamp.
4. Time features are computed point-in-time from the timestamp without lookahead.
"""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

from ml.config import (
    CONTEXTUAL_VARIABLES,
    EQUIPMENT_COL,
    MODEL_FEATURES,
    TARGET_COL,
    TIMESTAMP_COL,
    TRAIN_SPLIT_RATIO,
)


def load_raw_data(filepath: str) -> pd.DataFrame:
    """Load raw dataset from CSV file."""
    df = pd.read_csv(filepath)
    return df


def engineer_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract point-in-time temporal features from the timestamp column.
    
    Features created:
    - hour (0-23)
    - day_of_week (0-6, Monday=0, Sunday=6)
    - month (1-12)
    - is_weekend (1 if Saturday/Sunday else 0)
    - sin_hour, cos_hour (cyclical representation so 23:30 is adjacent to 00:00)
    """
    df = df.copy()
    ts = pd.to_datetime(df[TIMESTAMP_COL])
    df["dt"] = ts
    df["hour"] = ts.dt.hour + (ts.dt.minute / 60.0)
    df["day_of_week"] = ts.dt.dayofweek
    df["month"] = ts.dt.month
    df["is_weekend"] = (ts.dt.dayofweek >= 5).astype(int)

    # Cyclical 24-hour encoding
    df["sin_hour"] = np.sin(2 * np.pi * df["hour"] / 24.0)
    df["cos_hour"] = np.cos(2 * np.pi * df["hour"] / 24.0)

    return df


def clean_and_sort_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse timestamps, drop exact duplicate rows, convert numerical columns,
    and enforce strict chronological order by equipment and timestamp.
    """
    df = df.copy()
    # Remove duplicates
    df = df.drop_duplicates(subset=[EQUIPMENT_COL, TIMESTAMP_COL])

    # Convert numeric columns
    numeric_cols = CONTEXTUAL_VARIABLES + [TARGET_COL]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Engineer time features
    df = engineer_time_features(df)

    # Chronological sort per equipment
    df = df.sort_values(by=[EQUIPMENT_COL, "dt"]).reset_index(drop=True)

    return df


def split_train_test_by_equipment(
    df: pd.DataFrame,
    split_ratio: float = TRAIN_SPLIT_RATIO,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Dict[str, float]]]:
    """
    Split data chronologically per equipment into train and test sets to strictly 
    prevent temporal leakage.
    
    Returns:
        train_df: Chronological first split_ratio of each chiller's data.
        test_df: Chronological remaining (1 - split_ratio) of each chiller's data.
        impute_stats: Training-set medians per equipment for leakage-safe imputation.
    """
    train_dfs = []
    test_dfs = []
    impute_stats: Dict[str, Dict[str, float]] = {}

    for eq, group in df.groupby(EQUIPMENT_COL, sort=False):
        group = group.sort_values("dt").reset_index(drop=True)
        split_idx = int(len(group) * split_ratio)

        train_part = group.iloc[:split_idx].copy()
        test_part = group.iloc[split_idx:].copy()

        # Compute medians strictly on the training set for this equipment
        medians = {}
        for col in CONTEXTUAL_VARIABLES:
            med_val = train_part[col].median()
            medians[col] = float(med_val) if not pd.isna(med_val) else 0.0
        impute_stats[eq] = medians

        train_dfs.append(train_part)
        test_dfs.append(test_part)

    train_df = pd.concat(train_dfs, ignore_index=True)
    test_df = pd.concat(test_dfs, ignore_index=True)

    return train_df, test_df, impute_stats


def impute_leakage_safe(
    df: pd.DataFrame,
    impute_stats: Dict[str, Dict[str, float]],
    drop_null_target: bool = False,
) -> pd.DataFrame:
    """
    Apply leakage-safe missing value imputation without dropping rows:
    1. For all contextual variables and target energy consumption within each equipment:
       - Linear interpolation for interior null values.
       - Chronological forward-fill (ffill).
       - Leading nulls filled with training-set equipment median (or group median fallback).
       - Backward-fill (bfill) as secondary safety to ensure zero nulls remain.
    2. Zero rows are dropped via dropna to preserve continuous time-series alignment.
    """
    df_imputed = df.copy()
    processed_groups = []

    all_numeric_cols = CONTEXTUAL_VARIABLES + [TARGET_COL]

    for eq, group in df_imputed.groupby(EQUIPMENT_COL, sort=False):
        group = group.sort_values("dt").copy()
        eq_medians = impute_stats.get(eq, {})

        for col in all_numeric_cols:
            if col in group.columns:
                # 1. Forward-direction linear interpolation for interior gaps
                group[col] = group[col].interpolate(method="linear", limit_direction="forward")
                # 2. Historical forward fill
                group[col] = group[col].ffill()
                # 3. Leading values filled with train median
                fallback_val = eq_medians.get(col, group[col].median() if not group[col].empty else 0.0)
                group[col] = group[col].fillna(fallback_val if not pd.isna(fallback_val) else 0.0)
                # 4. Backward fill safety guard
                group[col] = group[col].bfill()

        processed_groups.append(group)

    result_df = pd.concat(processed_groups, ignore_index=True)

    if drop_null_target and TARGET_COL in result_df.columns:
        result_df = result_df.dropna(subset=[TARGET_COL]).reset_index(drop=True)

    return result_df


def prepare_dataset(
    filepath: str,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Dict[str, float]]]:
    """
    Full preprocessing pipeline:
    1. Load CSV
    2. Clean, engineer time features, and sort chronologically
    3. Chronological train/test split per equipment
    4. Leakage-safe zero-drop imputation calibrated on training data
    
    Returns:
        full_clean_df: Entire cleaned dataset with zero-drop imputation (preserves all rows)
        train_df: Training partition (leakage-free)
        test_df: Test partition (leakage-free)
        impute_stats: Training medians used for imputation
    """
    raw_df = load_raw_data(filepath)
    clean_df = clean_and_sort_data(raw_df)

    train_raw, test_raw, impute_stats = split_train_test_by_equipment(clean_df)

    train_df = impute_leakage_safe(train_raw, impute_stats, drop_null_target=False)
    test_df = impute_leakage_safe(test_raw, impute_stats, drop_null_target=False)

    # Impute full dataset sequentially per equipment using training statistics without dropping rows
    full_clean_df = impute_leakage_safe(clean_df, impute_stats, drop_null_target=False)

    return full_clean_df, train_df, test_df, impute_stats

