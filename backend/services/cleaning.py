"""Data cleaning utilities and functions."""

import hashlib
import re
from datetime import datetime
from typing import List, Optional, Tuple

import pandas as pd

from backend.core.logging import logger


def clean_id(s: str) -> str:
    """
    Clean ID column values by keeping only alphanumeric characters,
    collapsing spaces/underscores, and converting to uppercase.
    
    Args:
        s: Input string to clean
        
    Returns:
        Cleaned string
    """
    if pd.isna(s) or s is None:
        return ""
    
    # Convert to string and strip
    s = str(s).strip()
    
    # Keep only alphanumeric characters, spaces, hyphens, underscores
    s = re.sub(r'[^A-Za-z0-9\s\-_]', '', s)
    
    # Collapse multiple spaces/underscores into single space
    s = re.sub(r'[\s_]+', ' ', s)
    
    # Convert to uppercase and strip again
    s = s.upper().strip()
    
    return s


def parse_date_column(series: pd.Series, col_name: str) -> pd.DataFrame:
    """
    Parse a date column and create derived date features.
    
    Args:
        series: Pandas series with date values
        col_name: Name of the column
        
    Returns:
        DataFrame with original and derived date columns
    """
    result_df = pd.DataFrame()
    
    # Original column
    result_df[col_name] = series
    
    try:
        # Parse dates
        parsed_dates = pd.to_datetime(series, errors='coerce', infer_datetime_format=True)
        
        # Base date column
        date_col = f"{col_name}_date"
        result_df[date_col] = parsed_dates.dt.date
        
        # Derived columns
        result_df[f"{col_name}_year"] = parsed_dates.dt.year
        result_df[f"{col_name}_month"] = parsed_dates.dt.month
        result_df[f"{col_name}_day"] = parsed_dates.dt.day
        result_df[f"{col_name}_qtr"] = parsed_dates.dt.quarter
        result_df[f"{col_name}_week"] = parsed_dates.dt.isocalendar().week
        
        logger.info(f"Parsed date column '{col_name}'",
                   valid_dates=int(parsed_dates.notna().sum()),
                   total_values=len(series))
        
    except Exception as e:
        logger.error(f"Failed to parse date column '{col_name}': {e}")
        # Fill with None if parsing fails
        for suffix in ['_date', '_year', '_month', '_day', '_qtr', '_week']:
            result_df[f"{col_name}{suffix}"] = None
    
    return result_df


def create_dim_dates(date_columns: List[pd.Series], 
                    column_names: List[str]) -> pd.DataFrame:
    """
    Create a date dimension table from multiple date columns.
    
    Args:
        date_columns: List of date series
        column_names: Names of the date columns
        
    Returns:
        Date dimension DataFrame
    """
    all_dates = []
    
    for series, col_name in zip(date_columns, column_names):
        try:
            parsed_dates = pd.to_datetime(series, errors='coerce')
            valid_dates = parsed_dates.dropna()
            
            for date_val in valid_dates:
                all_dates.append({
                    'date': date_val.date(),
                    'role': col_name,
                    'year': date_val.year,
                    'month': date_val.month,
                    'day': date_val.day,
                    'quarter': date_val.quarter,
                    'week': date_val.isocalendar().week,
                    'weekday': date_val.weekday(),
                    'month_name': date_val.strftime('%B'),
                    'day_name': date_val.strftime('%A')
                })
        except Exception as e:
            logger.warning(f"Failed to process date column '{col_name}': {e}")
    
    if not all_dates:
        logger.warning("No valid dates found for dimension table")
        return pd.DataFrame()
    
    dim_dates = pd.DataFrame(all_dates)
    
    # Remove duplicates but keep role information
    dim_dates = dim_dates.drop_duplicates(subset=['date', 'role'])
    
    logger.info(f"Created date dimension", 
               total_dates=len(dim_dates),
               date_range=f"{dim_dates['date'].min()} to {dim_dates['date'].max()}")
    
    return dim_dates


def standardize_text(series: pd.Series) -> pd.Series:
    """
    Standardize text values by stripping whitespace and converting to title case.

    Args:
        series: Pandas series with text values

    Returns:
        Cleaned series
    """
    try:
        # Ensure we're working with a proper Series
        if not isinstance(series, pd.Series):
            series = pd.Series(series)

        # Create a copy to avoid modifying the original
        result_series = series.copy()

        # Process each value individually to avoid Series ambiguity
        for idx in result_series.index:
            try:
                val = result_series.iloc[idx]

                # Handle null/None values
                if pd.isna(val) or val is None:
                    continue

                # Convert to string and strip
                text = str(val).strip()

                # Skip empty strings
                if not text:
                    continue

                # Unescape newlines and normalize whitespace
                text = re.sub(r'\\n', '\n', text)
                text = re.sub(r'\s+', ' ', text)

                # Convert to title case for names
                if len(text) > 0:
                    text = text.title()

                result_series.iloc[idx] = text

            except Exception as e:
                # If there's an error processing this specific value, leave it as-is
                continue

        return result_series

    except Exception as e:
        # If there's a fundamental error, return the original series
        print(f"Error in standardize_text: {e}")
        return series


def create_row_hash(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.Series:
    """
    Create a hash for each row based on significant columns.
    
    Args:
        df: DataFrame to hash
        columns: Specific columns to include in hash (default: all)
        
    Returns:
        Series with row hashes
    """
    if columns is None:
        columns = df.columns.tolist()
    
    def hash_row(row):
        # Convert row values to string and concatenate
        row_str = '|'.join(str(row[col]) for col in columns if col in row.index)
        
        # Create MD5 hash
        return hashlib.md5(row_str.encode()).hexdigest()
    
    return df.apply(hash_row, axis=1)


def remove_duplicate_rows(df: pd.DataFrame, 
                         subset: Optional[List[str]] = None) -> Tuple[pd.DataFrame, int]:
    """
    Remove duplicate rows and return cleaned DataFrame with count.
    
    Args:
        df: DataFrame to deduplicate
        subset: Columns to consider for duplicates (default: all)
        
    Returns:
        Tuple of (cleaned_df, duplicate_count)
    """
    original_count = len(df)
    
    # Remove duplicates, keeping first occurrence
    cleaned_df = df.drop_duplicates(subset=subset, keep='first')
    
    duplicate_count = original_count - len(cleaned_df)
    
    if duplicate_count > 0:
        logger.info(f"Removed {duplicate_count} duplicate rows",
                   original_rows=original_count,
                   final_rows=len(cleaned_df))
    
    return cleaned_df, duplicate_count


def detect_date_columns(df: pd.DataFrame) -> List[str]:
    """
    Auto-detect date columns based on column names and content.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        List of column names that appear to contain dates
    """
    date_columns = []
    
    # Common date column name patterns
    date_patterns = [
        r'date',
        r'time',
        r'approved',
        r'promised',
        r'created',
        r'updated',
        r'modified',
        r'sop',
        r'milestone'
    ]
    
    for col in df.columns:
        col_lower = str(col).lower()
        
        # Check column name patterns
        is_date_name = any(re.search(pattern, col_lower) for pattern in date_patterns)
        
        if is_date_name:
            # Verify content looks like dates
            sample = df[col].dropna().head(10)
            if len(sample) > 0:
                try:
                    parsed = pd.to_datetime(sample, errors='coerce')
                    valid_ratio = parsed.notna().sum() / len(sample)
                    
                    if valid_ratio > 0.5:  # At least 50% valid dates
                        date_columns.append(col)
                        logger.info(f"Auto-detected date column: '{col}'",
                                   valid_ratio=valid_ratio)
                except Exception:
                    pass
    
    return date_columns
