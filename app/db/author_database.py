import json
import os
from app.schemas.factcheck import AuthorProfile

class AuthorDatabase:
    """
    JSON-based mock database for author history and reliability profiles.
    """
    def __init__(self, db_path: str = "data/authors.json"):
        """
        Initialize the database from a JSON file.
        
        Args:
            db_path: Path to the JSON file containing author data.
        """
        self.db_path = db_path
        self.authors = {}
        self._load_data()
        
    def _load_data(self):
        """Load data from JSON or use defaults."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    data = json.load(f)
                    for name, profile_data in data.items():
                        self.authors[name] = AuthorProfile(**profile_data)
            except (json.JSONDecodeError, Exception) as e:
                print(f"Error loading author database: {e}")
                self.authors = {}
        else:
            self.authors = {}

    def get_author(self, name: str) -> AuthorProfile:
        """
        Retrieve an author's profile by name.
        
        Args:
            name: The full name of the author.
            
        Returns:
            An AuthorProfile object. If the author is not found, returns a default 'Unknown' profile.
        """
        if name in self.authors:
            return self.authors[name]
        
        # Default for unknown authors
        return AuthorProfile(
            author_name=name,
            historical_score=50,
            total_articles=0,
            reliability_assessment="Author not found in database.",
            trust_level="Neutral"
        )
