import os
import pandas as pd
import uuid
import re
from collections import Counter


class Portfolio:
    def __init__(self, file_path=None):
        if file_path is None:
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resource", "my_portfolio.csv")
        self.file_path = file_path
        self.data = pd.read_csv(file_path)
        self.portfolio_store = {}

    def load_portfolio(self):
        if not self.portfolio_store:
            for _, row in self.data.iterrows():
                techstack = row["Techstack"]
                link = row["Links"]
                self.portfolio_store[techstack] = link

    def _calculate_similarity(self, skills, techstack):
        """Calculate similarity between job skills and techstack using keyword matching"""
        if not skills:
            return 0
        skills_normalized = [s.lower().strip() for s in skills]
        techstack_normalized = techstack.lower()
        
        matches = 0
        for skill in skills_normalized:
            # Check for word boundaries to avoid partial matches
            if re.search(r'\b' + re.escape(skill) + r'\b', techstack_normalized):
                matches += 1
        
        return matches / len(skills) if skills else 0

    def query_links(self, skills):
        """Query portfolio links based on skills similarity"""
        if not skills:
            return []
        
        similarities = []
        for techstack, link in self.portfolio_store.items():
            sim = self._calculate_similarity(skills, techstack)
            if sim > 0:
                similarities.append((sim, link))
        
        # Sort by similarity and get top results
        similarities.sort(key=lambda x: x[0], reverse=True)
        top_results = similarities[:2]
        
        return [{"links": link} for _, link in top_results]
