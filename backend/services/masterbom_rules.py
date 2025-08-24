"""Business rules and transformations for MasterBOM sheet processing."""

from typing import Dict, List, Tuple

import pandas as pd

from backend.core.logging import ETLLogger
from backend.services.cleaning import clean_id, standardize_text, parse_date_column, detect_date_columns


class MasterBOMProcessor:
    """Processor for MasterBOM sheet with business rules."""
    
    def __init__(self, df: pd.DataFrame, logger: ETLLogger):
        """Initialize with DataFrame and logger."""
        self.df = df.copy()
        self.logger = logger
        self.project_columns = []
        self.id_column = None
        
    def process(self, id_col: str = "YAZAKI PN", 
                date_cols: List[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Process MasterBOM sheet according to business rules.
        
        Args:
            id_col: Name of the ID column
            date_cols: List of date column names to process
            
        Returns:
            Dictionary with processed DataFrames
        """
        self.logger.info("Starting MasterBOM processing", 
                        input_rows=len(self.df), input_cols=len(self.df.columns))
        
        # Step 1: Clean column names
        self._clean_column_names()
        
        # Step 2: Identify ID column and project columns
        self._identify_columns(id_col)
        
        # Step 3: Clean ID column
        self._clean_id_column()
        
        # Step 4: Process date columns
        if date_cols is None:
            date_cols = detect_date_columns(self.df)
        self._process_date_columns(date_cols)
        
        # Step 5: Standardize text columns
        self._standardize_text_columns()
        
        # Step 6: Create normalized plant-item-status table
        plant_item_status = self._create_plant_item_status()
        
        # Step 7: Create fact parts table
        fact_parts = self._create_fact_parts()
        
        # Step 8: Clean main DataFrame
        masterbom_clean = self._finalize_masterbom()
        
        self.logger.info("MasterBOM processing complete",
                        output_tables=3,
                        masterbom_rows=len(masterbom_clean),
                        plant_status_rows=len(plant_item_status),
                        fact_parts_rows=len(fact_parts))
        
        return {
            'masterbom_clean': masterbom_clean,
            'plant_item_status': plant_item_status,
            'fact_parts': fact_parts
        }
    
    def _clean_column_names(self):
        """Clean and standardize column names."""
        original_cols = self.df.columns.tolist()
        
        # Strip whitespace and standardize
        self.df.columns = [str(col).strip() for col in self.df.columns]
        
        self.logger.info("Cleaned column names", 
                        original_count=len(original_cols))
    
    def _identify_columns(self, id_col: str):
        """Identify ID column and project columns."""
        columns = self.df.columns.tolist()
        
        # Find ID column
        self.id_column = None
        for col in columns:
            if str(col).strip().upper() == id_col.upper():
                self.id_column = col
                break
        
        if self.id_column is None:
            self.logger.warning(f"ID column '{id_col}' not found, using first column")
            self.id_column = columns[0]
        
        # Find project columns (between ID and Item Description)
        id_idx = columns.index(self.id_column)
        desc_idx = None
        
        for i, col in enumerate(columns[id_idx + 1:], start=id_idx + 1):
            col_lower = str(col).lower()
            if 'item' in col_lower and 'desc' in col_lower:
                desc_idx = i
                break
        
        if desc_idx is None:
            # Assume all remaining columns are projects if no description found
            desc_idx = len(columns)
        
        self.project_columns = columns[id_idx + 1:desc_idx]
        
        self.logger.info("Identified columns",
                        id_column=self.id_column,
                        project_columns_count=len(self.project_columns),
                        project_columns=self.project_columns[:5])  # Log first 5
    
    def _clean_id_column(self):
        """Clean the ID column values."""
        if self.id_column not in self.df.columns:
            return
        
        # Create standardized ID column
        self.df['part_id_raw'] = self.df[self.id_column].astype(str)
        self.df['part_id_std'] = self.df[self.id_column].apply(clean_id)
        
        # Count cleaning results
        non_empty = self.df['part_id_std'].str.len() > 0
        
        self.logger.info("Cleaned ID column",
                        total_parts=len(self.df),
                        valid_ids=int(non_empty.sum()),
                        empty_ids=int((~non_empty).sum()))
    
    def _process_date_columns(self, date_cols: List[str]):
        """Process date columns and create derived features."""
        processed_cols = []
        
        for col in date_cols:
            if col in self.df.columns:
                try:
                    date_df = parse_date_column(self.df[col], col)
                    
                    # Add new columns to main DataFrame
                    for new_col in date_df.columns:
                        if new_col != col:  # Don't overwrite original
                            self.df[new_col] = date_df[new_col]
                    
                    processed_cols.append(col)
                    
                except Exception as e:
                    self.logger.error(f"Failed to process date column '{col}': {e}")
        
        self.logger.info("Processed date columns", 
                        requested=len(date_cols),
                        processed=len(processed_cols),
                        columns=processed_cols)
    
    def _standardize_text_columns(self):
        """Standardize text columns like supplier names."""
        text_columns = [
            'Supplier Name', 'Original Supplier Name', 
            'Item Description', 'Part Specification'
        ]
        
        standardized = 0
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = standardize_text(self.df[col])
                standardized += 1
        
        self.logger.info("Standardized text columns", count=standardized)
    
    def _create_plant_item_status(self) -> pd.DataFrame:
        """Create normalized plant-item-status long table."""
        if not self.project_columns:
            self.logger.warning("No project columns found for normalization")
            return pd.DataFrame()
        
        # Prepare base data
        base_cols = ['part_id_std', 'part_id_raw']
        if self.id_column:
            base_cols.append(self.id_column)
        
        # Melt project columns into long format
        id_vars = [col for col in base_cols if col in self.df.columns]
        
        melted = pd.melt(
            self.df,
            id_vars=id_vars,
            value_vars=self.project_columns,
            var_name='project_plant',
            value_name='raw_status'
        )
        
        # Apply status classification rules
        melted['status_class'] = melted.apply(self._classify_status, axis=1)
        melted['is_duplicate'] = melted.apply(self._check_duplicate, axis=1)
        melted['is_new'] = melted['status_class'] == 'new'
        melted['notes'] = None
        
        # Calculate plant counts per part
        plant_counts = self._calculate_plant_counts(melted)
        melted = melted.merge(plant_counts, on='part_id_std', how='left')
        
        self.logger.info("Created plant-item-status table",
                        total_records=len(melted),
                        unique_parts=melted['part_id_std'].nunique(),
                        unique_plants=melted['project_plant'].nunique())
        
        return melted
    
    def _classify_status(self, row) -> str:
        """Classify status based on raw_status value."""
        raw_status = str(row['raw_status']).strip().upper()
        
        if raw_status == 'X':
            return 'active'
        elif raw_status == 'D':
            return 'inactive'
        elif raw_status == '0':
            # Check for duplicates - simplified logic
            return 'duplicate'  # Will be refined in _check_duplicate
        elif raw_status in ['', 'NAN', 'NONE']:
            return 'new'
        else:
            return 'new'  # Default for unknown values
    
    def _check_duplicate(self, row) -> bool:
        """Check if part is a duplicate."""
        if row['status_class'] == 'duplicate':
            # Count occurrences of this part_id_std in the original DataFrame
            part_count = (self.df['part_id_std'] == row['part_id_std']).sum()
            return part_count > 1
        return False
    
    def _calculate_plant_counts(self, melted_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate counts by status for each part."""
        counts = melted_df.groupby('part_id_std')['status_class'].value_counts().unstack(fill_value=0)
        
        # Ensure all status columns exist
        for status in ['active', 'inactive', 'new', 'duplicate']:
            if status not in counts.columns:
                counts[status] = 0
        
        # Rename columns
        counts = counts.rename(columns={
            'active': 'n_active',
            'inactive': 'n_inactive', 
            'new': 'n_new',
            'duplicate': 'n_duplicate'
        })
        
        return counts.reset_index()
    
    def _create_fact_parts(self) -> pd.DataFrame:
        """Create fact table with one row per part."""
        if 'part_id_std' not in self.df.columns:
            return pd.DataFrame()
        
        # Group by part_id_std and aggregate
        fact_cols = ['part_id_std', 'part_id_raw']
        
        # Add key business columns if they exist
        business_cols = [
            'Item Description', 'Supplier Name', 'Supplier PN',
            'PSW', 'PSW Type', 'PSW Sub Type', 'YPN Status',
            'Handling Manual', 'IMDS STATUS (Yes, No, N/A)',
            'FAR Status', 'PPAP Details'
        ]
        
        available_cols = [col for col in business_cols if col in self.df.columns]
        fact_cols.extend(available_cols)
        
        # Create fact table (one row per part)
        fact_parts = self.df[fact_cols].drop_duplicates(subset=['part_id_std'])
        
        # Add derived flags
        if 'PSW' in fact_parts.columns:
            fact_parts['psw_ok'] = fact_parts['PSW'].notna() & (fact_parts['PSW'] != '')
        
        if 'Handling Manual' in fact_parts.columns:
            fact_parts['has_handling_manual'] = fact_parts['Handling Manual'].notna()
        
        if 'FAR Status' in fact_parts.columns:
            fact_parts['far_ok'] = fact_parts['FAR Status'].str.contains('OK', case=False, na=False)
        
        if 'IMDS STATUS (Yes, No, N/A)' in fact_parts.columns:
            fact_parts['imds_ok'] = fact_parts['IMDS STATUS (Yes, No, N/A)'].str.contains('Yes', case=False, na=False)
        
        self.logger.info("Created fact parts table",
                        total_parts=len(fact_parts),
                        columns=len(fact_parts.columns))
        
        return fact_parts
    
    def _finalize_masterbom(self) -> pd.DataFrame:
        """Finalize the cleaned MasterBOM DataFrame."""
        # Remove duplicate rows
        original_count = len(self.df)
        cleaned_df = self.df.drop_duplicates()
        duplicates_removed = original_count - len(cleaned_df)
        
        if duplicates_removed > 0:
            self.logger.info("Removed duplicate rows", count=duplicates_removed)
        
        return cleaned_df
