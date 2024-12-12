import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
import logging
import torch
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ProjectStats:
    total_count: int
    total_budget: float
    completed: int
    in_progress: int
    not_started: int
    avg_completion: float

class ResponseGenerator:
    def __init__(self):
        self.data_cache = {}

    def _clean_numeric(self, value: Any, default: float = 0.0) -> float:
        """Clean numeric values"""
        try:
            if pd.isna(value) or value == '' or value is None:
                return default
            return float(value)
        except (ValueError, TypeError):
            return default

    def _format_currency(self, amount: float) -> str:
        """Format currency values"""
        try:
            if pd.isna(amount) or amount <= 0:
                return "MK 0.00"
            return f"MK {amount:,.2f}"
        except Exception as e:
            logger.error(f"Error formatting currency: {e}")
            return "MK 0.00"

    def _format_status(self, completion: float) -> str:
        """Format status based on completion percentage"""
        if completion == 100:
            return "Completed"
        elif completion == 0:
            return "Not Started"
        else:
            return "In Progress"

    def _sort_and_filter_projects(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Enhanced filtering and sorting logic"""
        try:
            # Clean and prepare numeric values
            df['BUDGET'] = pd.to_numeric(df['BUDGET'], errors='coerce').fillna(0)
            df['COMPLETIONPERCENTAGE'] = pd.to_numeric(df['COMPLETIONPERCENTAGE'], errors='coerce').fillna(0)
            
            # Make a copy for filtering
            filtered_df = df.copy()
            query = str(filters.get('query', '')).lower()
            
            # Status/Completion filtering
            if any(word in query for word in ['complete', 'completed', 'finished']):
                return filtered_df[filtered_df['COMPLETIONPERCENTAGE'] >= 100].copy()
            elif any(word in query for word in ['not started', 'pending', 'approved']):
                return filtered_df[filtered_df['COMPLETIONPERCENTAGE'] == 0].copy()
            elif 'in progress' in query:
                return filtered_df[
                    (filtered_df['COMPLETIONPERCENTAGE'] > 0) & 
                    (filtered_df['COMPLETIONPERCENTAGE'] < 100)
                ].copy()

            # Budget sorting
            if 'highest budget' in query:
                # Sort by budget, excluding zero budgets
                non_zero_budget = filtered_df[filtered_df['BUDGET'] > 0].sort_values('BUDGET', ascending=False)
                return non_zero_budget.copy()
            elif 'lowest budget' in query:
                non_zero_budget = filtered_df[filtered_df['BUDGET'] > 0].sort_values('BUDGET', ascending=True)
                return non_zero_budget.copy()

            # Sector filtering
            if filters.get('sector'):
                filtered_df = filtered_df[
                    filtered_df['PROJECTSECTOR'].str.lower() == filters['sector'].lower()
                ]

            # Region filtering
            if filters.get('region'):
                filtered_df = filtered_df[
                    filtered_df['REGION'].str.lower() == filters['region'].lower()
                ]

            # Remove duplicates and return
            return filtered_df.drop_duplicates(subset=['PROJECTNAME', 'DISTRICT', 'REGION']).copy()

        except Exception as e:
            logger.error(f"Error in filtering projects: {e}")
            return df

    def _calculate_stats(self, df: pd.DataFrame) -> ProjectStats:
        """Calculate accurate project statistics"""
        try:
            completed = len(df[df['COMPLETIONPERCENTAGE'] >= 100])
            not_started = len(df[df['COMPLETIONPERCENTAGE'] == 0])
            in_progress = len(df[(df['COMPLETIONPERCENTAGE'] > 0) & (df['COMPLETIONPERCENTAGE'] < 100)])
            total_budget = df[df['BUDGET'] > 0]['BUDGET'].sum()
            avg_completion = df['COMPLETIONPERCENTAGE'].mean() if not df.empty else 0.0
            
            return ProjectStats(
                total_count=len(df),
                total_budget=total_budget,
                completed=completed,
                in_progress=in_progress,
                not_started=not_started,
                avg_completion=avg_completion
            )
        except Exception as e:
            logger.error(f"Error calculating stats: {e}")
            return ProjectStats(0, 0.0, 0, 0, 0, 0.0)

    def _format_project_info(self, row: pd.Series) -> List[str]:
        """Format project information"""
        try:
            completion = float(row['COMPLETIONPERCENTAGE'] or 0)
            budget = float(row['BUDGET'] or 0)
            
            project_info = [
                f"\n {row['PROJECTNAME']}",
                f"• Sector: {row.get('PROJECTSECTOR', 'Sector not specified')}",
                f"• Status: {self._format_status(completion)}",
                f"• Location: {row.get('DISTRICT', 'Location not specified')}, {row.get('REGION', '')}",
                f"• Budget: {self._format_currency(budget)}",
                f"• Completion: {completion:.1f}%"
            ]
            
            if pd.notna(row.get('PROJECTDESC')):
                project_info.append(f"• Description: {row['PROJECTDESC']}")
            
            return project_info
        except Exception as e:
            logger.error(f"Error formatting project info: {e}")
            return ["\nError formatting project information"]

    def generate_response(
        self,
        df: pd.DataFrame,
        filters: Dict[str, Any],
        language: str,
        model: Optional[Any] = None,
        tokenizer: Optional[Any] = None
    ) -> str:
        try:
            # Filter and sort data
            filtered_df = self._sort_and_filter_projects(df, filters)
            
            # Calculate statistics
            stats = self._calculate_stats(filtered_df)
            
            # Build response header
            sector = filters.get('sector', 'all sectors')
            region = filters.get('region', 'all regions')
            district = filters.get('district', '')
            location = f" in {district}, {region}" if district else f" for {region}"
            
            response = [f"Found {stats.total_count} projects in {sector}{location}:"]
            
            # Add project details
            for _, row in filtered_df.head(5).iterrows():
                project_info = self._format_project_info(row)
                response.append("\n".join(project_info))
            
            # Add summary
            summary = [
                "\nSummary:",
                f"• Total Budget: {self._format_currency(stats.total_budget)}",
                f"• Project Status Breakdown:",
                f"  - Completed (100%): {stats.completed} projects",
                f"  - In Progress (1-99%): {stats.in_progress} projects",
                f"  - Not Started (0%): {stats.not_started} projects",
                f"• Average Completion: {stats.avg_completion:.1f}%",
                f"• Projects Shown: {min(5, stats.total_count)} of {stats.total_count}"
            ]
            
            if stats.total_count > 5:
                summary.append("Type 'show more' to see additional projects.")
            
            response.extend(summary)
            return "\n\n".join(response)

        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            raise

    def generate_paginated_response(
        self,
        df: pd.DataFrame,
        pagination_info: Dict[str, Any],
        language: str
    ) -> str:
        try:
            filtered_df = self._sort_and_filter_projects(df, pagination_info.get('filters', {}))
            start = pagination_info.get('offset', 0)
            limit = pagination_info.get('page_size', 5)
            
            response = ["Here are more projects:"]
            
            for _, row in filtered_df.iloc[start:start+limit].iterrows():
                project_info = self._format_project_info(row)
                response.append("\n".join(project_info))
            
            remaining = len(filtered_df) - (start + limit)
            if remaining > 0:
                response.append(f"\n{remaining} more projects available. Type 'show more' to continue.")
            
            return "\n\n".join(response)

        except Exception as e:
            logger.error(f"Error generating paginated response: {e}")
            raise

    def is_show_more_request(self, query: str) -> bool:
        """Check if query is requesting more results"""
        show_more_phrases = ['show more', 'more results', 'next', 'continue']
        return any(phrase in query.lower() for phrase in show_more_phrases)