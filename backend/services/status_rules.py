"""Business rules and transformations for Status sheet processing."""

import re
from typing import Dict, List

import pandas as pd

from backend.core.logging import ETLLogger
from backend.services.cleaning import standardize_text


class StatusProcessor:
    """Processor for Status sheet with business rules."""
    
    def __init__(self, df: pd.DataFrame, logger: ETLLogger):
        """Initialize with DataFrame and logger."""
        self.df = df.copy()
        self.logger = logger
        
    def process(self) -> pd.DataFrame:
        """
        Process Status sheet according to business rules.

        Returns:
            Cleaned Status DataFrame
        """
        self.logger.info("Starting Status sheet processing",
                        input_rows=len(self.df), input_cols=len(self.df.columns))

        try:
            # Step 1: Clean headers
            self.logger.info("Step 1: Cleaning headers")
            self._clean_headers()

            # Step 2: Standardize text columns
            self.logger.info("Step 2: Standardizing text columns")
            self._standardize_text_columns()

            # Step 3: Convert percentage columns
            self.logger.info("Step 3: Converting percentage columns")
            self._convert_percentage_columns()

            # Step 4: Clean project names
            self.logger.info("Step 4: Cleaning project names")
            self._clean_project_names()

            # Step 5: Remove empty rows
            self.logger.info("Step 5: Removing empty rows")
            self._remove_empty_rows()

            self.logger.info("Status sheet processing complete",
                            output_rows=len(self.df), output_cols=len(self.df.columns))

            return self.df

        except Exception as e:
            self.logger.error(f"Error in status processing: {str(e)}",
                            step="status_processing",
                            error_type=type(e).__name__)
            raise
    
    def _clean_headers(self):
        """Clean and standardize column headers."""
        original_cols = self.df.columns.tolist()
        
        cleaned_cols = []
        for col in original_cols:
            # Convert to string and strip
            clean_col = str(col).strip()
            
            # Collapse multiple spaces
            clean_col = re.sub(r'\s+', ' ', clean_col)
            
            # Standardize common header patterns
            clean_col = self._standardize_header_name(clean_col)
            
            cleaned_cols.append(clean_col)
        
        self.df.columns = cleaned_cols
        
        self.logger.info("Cleaned column headers", 
                        original_count=len(original_cols),
                        cleaned_count=len(cleaned_cols))
    
    def _standardize_header_name(self, header: str) -> str:
        """Standardize individual header names."""
        header_lower = header.lower()
        
        # Common standardizations
        standardizations = {
            'oem': 'OEM',
            'project': 'Project',
            'ppap': 'PPAP',
            'psw': 'PSW',
            'total part numbers': 'Total_Part_Numbers',
            'psw available': 'PSW_Available',
            'drawing available': 'Drawing_Available',
            '1st ppap milestone': 'First_PPAP_Milestone',
            'managed by': 'Managed_By'
        }
        
        for pattern, replacement in standardizations.items():
            if pattern in header_lower:
                return replacement
        
        # Default: title case with underscores
        return header.replace(' ', '_').title()
    
    def _standardize_text_columns(self):
        """Standardize text columns."""
        text_columns = ['OEM', 'Project', 'Managed_By']

        standardized = 0
        for col in text_columns:
            try:
                if col in self.df.columns.tolist():
                    self.logger.info(f"Standardizing column: {col}")
                    self.df[col] = standardize_text(self.df[col])
                    standardized += 1
                    self.logger.info(f"Successfully standardized column: {col}")
            except Exception as e:
                self.logger.error(f"Error standardizing column '{col}': {str(e)}",
                                column=col, error_type=type(e).__name__)
                raise

        self.logger.info("Standardized text columns", count=standardized)
    
    def _convert_percentage_columns(self):
        """Convert percentage columns to numeric values (0-1 range)."""
        try:
            percentage_patterns = [
                r'%',
                r'percent',
                r'available',
                r'complete'
            ]

            converted = 0
            for col in self.df.columns:
                try:
                    col_lower = str(col).lower()

                    # Check if column name suggests percentages
                    is_percentage = any(pattern in col_lower for pattern in percentage_patterns)

                    if is_percentage:
                        self.logger.info(f"Converting percentage column: {col}")
                        # Convert percentage strings to numeric
                        self.df[col] = self._parse_percentage_values(self.df[col])
                        converted += 1

                        self.logger.info(f"Converted percentage column: {col}")

                except Exception as e:
                    self.logger.warning(f"Failed to convert percentage column '{col}': {e}")

            self.logger.info("Converted percentage columns", count=converted)

        except Exception as e:
            self.logger.error(f"Error in percentage conversion: {str(e)}",
                            error_type=type(e).__name__)
            raise
    
    def _parse_percentage_values(self, series: pd.Series) -> pd.Series:
        """Parse percentage values from various formats."""
        def parse_value(val):
            if pd.isna(val):
                return None
            
            val_str = str(val).strip()
            
            # Handle empty strings
            if not val_str:
                return None
            
            # Remove percentage sign
            val_str = val_str.replace('%', '')
            
            try:
                # Convert to float
                num_val = float(val_str)
                
                # If value is > 1, assume it's in percentage format (e.g., 85 = 85%)
                if num_val > 1:
                    return num_val / 100.0
                else:
                    return num_val
                    
            except ValueError:
                # Handle text values like "Complete", "N/A", etc.
                val_lower = val_str.lower()
                if val_lower in ['complete', 'done', 'finished', '100']:
                    return 1.0
                elif val_lower in ['none', 'n/a', 'na', 'not available', '0']:
                    return 0.0
                else:
                    return None
        
        return series.apply(parse_value)
    
    def _clean_project_names(self):
        """Clean and standardize project names."""
        try:
            # Check if Project column exists
            if 'Project' in self.df.columns.tolist():
                # Remove common prefixes/suffixes
                def clean_project(name):
                    try:
                        if pd.isna(name):
                            return name

                        name = str(name).strip()

                        # Remove common patterns
                        patterns_to_remove = [
                            r'^Project\s*:?\s*',
                            r'\s*-\s*Project$',
                            r'\s*\(.*\)$'  # Remove parenthetical notes
                        ]

                        for pattern in patterns_to_remove:
                            name = re.sub(pattern, '', name, flags=re.IGNORECASE)

                        return name.strip()
                    except Exception as e:
                        # If there's an error processing this name, return it as-is
                        return name

                self.df['Project'] = self.df['Project'].apply(clean_project)

                self.logger.info("Cleaned project names")
        except Exception as e:
            self.logger.warning(f"Failed to clean project names: {e}")
    
    def _remove_empty_rows(self):
        """Remove rows that are completely empty or contain only whitespace."""
        try:
            original_count = len(self.df)

            # Check for rows where all values are null or empty strings
            def is_row_not_empty(row):
                """Check if a row has any non-empty values."""
                # First check if any values are not null
                if not row.notna().any():
                    return False

                # Then check if any non-null values are not empty strings
                non_null_values = [val for val in row if pd.notna(val)]
                return any(str(val).strip() != '' for val in non_null_values)

            mask = self.df.apply(is_row_not_empty, axis=1)

            # Filter DataFrame using the boolean mask
            self.df = self.df.loc[mask]

            removed_count = original_count - len(self.df)

            if removed_count > 0:
                self.logger.info("Removed empty rows", count=removed_count)

        except Exception as e:
            self.logger.error(f"Error removing empty rows: {str(e)}",
                            error_type=type(e).__name__)
            raise
    
    def get_project_summary(self) -> Dict[str, any]:
        """Get summary statistics for the status sheet."""
        summary = {
            'total_projects': 0,
            'total_parts': 0,
            'avg_psw_available': 0,
            'avg_drawing_available': 0,
            'projects_by_oem': {}
        }
        
        try:
            columns_list = self.df.columns.tolist()

            if 'Project' in columns_list:
                summary['total_projects'] = self.df['Project'].nunique()

            if 'Total_Part_Numbers' in columns_list:
                total_parts = pd.to_numeric(self.df['Total_Part_Numbers'], errors='coerce')
                summary['total_parts'] = int(total_parts.sum()) if total_parts.notna().any() else 0

            if 'PSW_Available' in columns_list:
                psw_avg = pd.to_numeric(self.df['PSW_Available'], errors='coerce').mean()
                summary['avg_psw_available'] = round(psw_avg, 3) if pd.notna(psw_avg) else 0

            if 'Drawing_Available' in columns_list:
                drawing_avg = pd.to_numeric(self.df['Drawing_Available'], errors='coerce').mean()
                summary['avg_drawing_available'] = round(drawing_avg, 3) if pd.notna(drawing_avg) else 0

            if 'OEM' in columns_list and 'Project' in columns_list:
                oem_projects = self.df.groupby('OEM')['Project'].nunique().to_dict()
                summary['projects_by_oem'] = oem_projects
            
        except Exception as e:
            self.logger.warning(f"Failed to generate project summary: {e}")
        
        return summary
