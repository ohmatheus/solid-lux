import pandas as pd

import re

__all__ = ["public_function", "PUBLIC_VAR"]

#---------------------------------------------------------------------------
def _clean_numeric(value):
    """Convert min_premium from string to float, handling cases like '$100'."""
    if isinstance(value, str):  
        value = re.sub(r"[^\d.]", "", value)
        try:
            return float(value) if value else None  # Convert to float
        except ValueError:
            return None
    return value

#---------------------------------------------------------------------------
def _get_associated_comment(group, num_col, comment_col):
    """Get the comment corresponding to the lowest numerical value in the group."""
    min_idx = group[num_col].idxmin(skipna=True) 
    return group.loc[min_idx, comment_col] if pd.notna(min_idx) else None

#---------------------------------------------------------------------------
def _most_frequent_value(series):
    return series.mode().iloc[0] if not series.mode().empty else None

#---------------------------------------------------------------------------
def _process_group(group) -> pd.Series:
    """Process each company group to apply merging logic."""
    result = {
        "company_name": group["company_name"].iloc[0],  # Keep company name
        "min_premium": group["min_premium"].min(skipna=True),
        "min_premium_comments": _get_associated_comment(group, "min_premium", "min_premium_comments"),
        "policy_period": group["policy_period"].min(skipna=True),
        "policy_period_comments": _get_associated_comment(group, "policy_period", "policy_period_comments"),
        "supp_fee_policy": group["supp_fee_policy"].min(skipna=True),
        "coverage_BI": _most_frequent_value(group["coverage_BI"]),
        "coverage_PD": _most_frequent_value(group["coverage_PD"]),
        "coverage_MED": _most_frequent_value(group["coverage_MED"]),
        "coverage_UM_UIMBI": _most_frequent_value(group["coverage_UM_UIMBI"]),
        "coverage_UMPD": _most_frequent_value(group["coverage_UMPD"]),
        "coverage_COMP": _most_frequent_value(group["coverage_COMP"]),
        "coverage_COLL": _most_frequent_value(group["coverage_COLL"]),
        "coverage_GAP": _most_frequent_value(group["coverage_GAP"]),
    }
    return pd.Series(result)


#---------------------------------------------------------------------------
def clean_and_format(df:pd.DataFrame) -> pd.DataFrame:
    # Apply to the column
    df["min_premium"] = df["min_premium"].apply(_clean_numeric)
    df["policy_period"] = df["policy_period"].apply(_clean_numeric)
    df["supp_fee_policy"] = df["supp_fee_policy"].apply(_clean_numeric)
    
    df_cleaned = df.groupby("company_name").apply(_process_group).reset_index(drop=True)
    return df_cleaned
