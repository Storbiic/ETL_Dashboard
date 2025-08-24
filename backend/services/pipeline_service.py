"""Automated pipeline service for ETL processing and PowerBI integration."""

from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from backend.core.config import settings
from backend.core.logging import ETLLogger
from backend.models.schemas import ArtifactInfo
from backend.services.powerbi_integration import PowerBIIntegration


class PipelineService:
    """Service for automated ETL pipeline with PowerBI integration."""
    
    def __init__(self, logger: Optional[ETLLogger] = None):
        """Initialize pipeline service."""
        self.logger = logger or ETLLogger()
        self.powerbi_integration = PowerBIIntegration(logger)
        
    def execute_post_etl_pipeline(
        self, 
        artifacts: List[ArtifactInfo], 
        dataframes: Dict[str, pd.DataFrame],
        file_id: str
    ) -> Dict:
        """
        Execute the automated pipeline after ETL transformation.
        
        Args:
            artifacts: List of generated artifacts from ETL
            dataframes: Dictionary of processed dataframes
            file_id: ID of the processed file
            
        Returns:
            Pipeline execution results
        """
        pipeline_results = {
            "file_id": file_id,
            "pipeline_executed": True,
            "copied_files": [],
            "powerbi_template": None,
            "data_source_info": {},
            "errors": []
        }
        
        try:
            self.logger.info("Starting post-ETL pipeline", 
                           file_id=file_id,
                           artifacts_count=len(artifacts))
            
            # Step 1: Copy files to pipeline output folder
            if settings.auto_copy_to_pipeline:
                copied_files = self._copy_files_to_pipeline(artifacts)
                pipeline_results["copied_files"] = copied_files
                
                if copied_files:
                    self.logger.info("Files copied to pipeline folder", 
                                   files_count=len(copied_files))
                else:
                    pipeline_results["errors"].append("Failed to copy files to pipeline folder")
            
            # Step 2: Create PowerBI template
            template_path = self._create_powerbi_template(dataframes, file_id)
            if template_path:
                pipeline_results["powerbi_template"] = template_path
                self.logger.info("PowerBI template created", 
                               template_path=template_path)
            else:
                pipeline_results["errors"].append("Failed to create PowerBI template")
            
            # Step 3: Create data source information
            data_source_info = self._create_data_source_info(pipeline_results["copied_files"])
            pipeline_results["data_source_info"] = data_source_info
            
            # Step 4: Generate pipeline summary
            pipeline_results["summary"] = self._create_pipeline_summary(
                pipeline_results, dataframes
            )
            
            self.logger.info("Post-ETL pipeline completed successfully", 
                           file_id=file_id,
                           errors_count=len(pipeline_results["errors"]))
            
            return pipeline_results
            
        except Exception as e:
            error_msg = f"Pipeline execution failed: {e}"
            self.logger.error(error_msg, file_id=file_id)
            pipeline_results["errors"].append(error_msg)
            pipeline_results["pipeline_executed"] = False
            return pipeline_results
    
    def _copy_files_to_pipeline(self, artifacts: List[ArtifactInfo]) -> List[str]:
        """Copy artifacts to pipeline output folder."""
        try:
            # Convert ArtifactInfo objects to dictionaries
            artifact_dicts = []
            for artifact in artifacts:
                if hasattr(artifact, 'dict'):
                    artifact_dicts.append(artifact.dict())
                else:
                    # Handle case where artifact is already a dict
                    artifact_dicts.append({
                        'path': getattr(artifact, 'path', str(artifact)),
                        'name': getattr(artifact, 'name', Path(str(artifact)).name),
                        'size_bytes': getattr(artifact, 'size_bytes', 0)
                    })
            
            return self.powerbi_integration.copy_files_to_pipeline(artifact_dicts)
            
        except Exception as e:
            self.logger.error(f"Failed to copy files to pipeline: {e}")
            return []
    
    def _create_powerbi_template(self, dataframes: Dict[str, pd.DataFrame], file_id: str) -> Optional[str]:
        """Create PowerBI template with current data structure."""
        try:
            # Check if template already exists
            template_name = f"ETL_Dashboard_Template_{file_id[:8]}.pbit"
            template_path = settings.powerbi_templates_folder_path / template_name
            
            # Always create/update template with current data structure
            return self.powerbi_integration.create_powerbi_template(dataframes)
            
        except Exception as e:
            self.logger.error(f"Failed to create PowerBI template: {e}")
            return None
    
    def _create_data_source_info(self, copied_files: List[str]) -> Dict:
        """Create comprehensive data source information."""
        return self.powerbi_integration.create_data_source_info(copied_files)
    
    def _create_pipeline_summary(self, pipeline_results: Dict, dataframes: Dict[str, pd.DataFrame]) -> Dict:
        """Create pipeline execution summary."""
        return {
            "pipeline_folder": str(settings.pipeline_output_folder_path.absolute()),
            "templates_folder": str(settings.powerbi_templates_folder_path.absolute()),
            "files_copied": len(pipeline_results["copied_files"]),
            "template_created": pipeline_results["powerbi_template"] is not None,
            "tables_processed": len(dataframes),
            "total_rows": sum(len(df) for df in dataframes.values()),
            "parquet_files": len([f for f in pipeline_results["copied_files"] if f.endswith('.parquet')]),
            "csv_files": len([f for f in pipeline_results["copied_files"] if f.endswith('.csv')]),
            "sqlite_files": len([f for f in pipeline_results["copied_files"] if f.endswith('.sqlite')]),
            "errors": pipeline_results["errors"]
        }
    
    def get_pipeline_status(self, file_id: str) -> Dict:
        """Get current pipeline status for a file."""
        try:
            pipeline_folder = settings.pipeline_output_folder_path
            templates_folder = settings.powerbi_templates_folder_path
            
            # Check for files in pipeline folder
            pipeline_files = []
            if pipeline_folder.exists():
                pipeline_files = [f.name for f in pipeline_folder.iterdir() if f.is_file()]
            
            # Check for templates
            template_files = []
            if templates_folder.exists():
                template_files = [f.name for f in templates_folder.iterdir() if f.suffix in ['.pbit', '.json']]
            
            return {
                "file_id": file_id,
                "pipeline_folder_exists": pipeline_folder.exists(),
                "templates_folder_exists": templates_folder.exists(),
                "pipeline_files": pipeline_files,
                "template_files": template_files,
                "pipeline_folder_path": str(pipeline_folder.absolute()),
                "templates_folder_path": str(templates_folder.absolute())
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get pipeline status: {e}")
            return {
                "file_id": file_id,
                "error": str(e)
            }
    
    def open_powerbi_dashboard(self, template_name: str = None) -> Dict:
        """Open PowerBI dashboard/template."""
        try:
            templates_folder = settings.powerbi_templates_folder_path
            
            if template_name:
                template_path = templates_folder / template_name
            else:
                # Find the most recent template
                template_files = list(templates_folder.glob("*.pbit"))
                if not template_files:
                    return {
                        "success": False,
                        "error": "No PowerBI templates found",
                        "templates_folder": str(templates_folder.absolute())
                    }
                
                template_path = max(template_files, key=lambda f: f.stat().st_mtime)
            
            if not template_path.exists():
                return {
                    "success": False,
                    "error": f"Template not found: {template_path}",
                    "templates_folder": str(templates_folder.absolute())
                }
            
            # Try to open in PowerBI Desktop
            success = self.powerbi_integration.open_powerbi_template(str(template_path))
            
            return {
                "success": success,
                "template_path": str(template_path),
                "powerbi_desktop_found": self.powerbi_integration.get_powerbi_desktop_path() is not None,
                "message": "PowerBI template opened successfully" if success else "Failed to open PowerBI template"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to open PowerBI dashboard: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_available_templates(self) -> List[Dict]:
        """Get list of available PowerBI templates."""
        try:
            templates_folder = settings.powerbi_templates_folder_path
            templates = []
            
            if templates_folder.exists():
                for template_file in templates_folder.iterdir():
                    if template_file.suffix in ['.pbit', '.json']:
                        stat = template_file.stat()
                        templates.append({
                            "name": template_file.name,
                            "path": str(template_file.absolute()),
                            "size_bytes": stat.st_size,
                            "modified": stat.st_mtime,
                            "type": "PowerBI Template" if template_file.suffix == '.pbit' else "Template Config"
                        })
            
            # Sort by modification time (newest first)
            templates.sort(key=lambda t: t["modified"], reverse=True)
            
            return templates
            
        except Exception as e:
            self.logger.error(f"Failed to get available templates: {e}")
            return []
