import pandas as pd
from typing import List, Dict, Any
import logging
import random

logger = logging.getLogger(__name__)

class SuggestionGenerator:
    def __init__(self):
        self.suggestions_cache = {}

    async def generate_suggestions(
        self,
        filters: Dict[str, Any],
        df: pd.DataFrame,
        language: str,
        max_suggestions: int = 3
    ) -> List[str]:
        """Generate contextual follow-up questions"""
        try:
            cache_key = f"{str(filters)}:{language}"
            if cache_key in self.suggestions_cache:
                return self.suggestions_cache[cache_key]

            suggestions = []
            
            # Add sector-based suggestions
            if not filters.get('sector') and not df.empty:
                sectors = df['PROJECTSECTOR'].unique()
                if len(sectors) > 0:
                    sector = random.choice(sectors)
                    suggestions.append(f"Show me projects in the {sector} sector")

            # Add location-based suggestions
            if not filters.get('district') and not df.empty:
                districts = df['DISTRICT'].unique()
                if len(districts) > 0:
                    district = random.choice(districts)
                    suggestions.append(f"What projects are in {district}?")

            # Add budget-based suggestions
            if not filters.get('has_budget') and not df.empty:
                suggestions.append("Show me projects with the highest budget")

            # Add status-based suggestions
            if not any([filters.get('completed'), filters.get('in_progress'), 
                       filters.get('not_started')]) and not df.empty:
                suggestions.append("What projects are currently in progress?")

            # Randomly select max_suggestions if we have more
            if len(suggestions) > max_suggestions:
                suggestions = random.sample(suggestions, max_suggestions)

            self.suggestions_cache[cache_key] = suggestions
            return suggestions

        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return []