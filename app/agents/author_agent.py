from app.schemas.factcheck import AuthorProfile
from app.db.author_database import AuthorDatabase

class AuthorAgent:
    """
    Agent responsible for assessing the reliability of article authors.
    Utilizes an AuthorDatabase to retrieve historical performance data.
    """
    def __init__(self, db: AuthorDatabase):
        """
        Initialize the AuthorAgent with a database instance.
        
        Args:
            db: An instance of AuthorDatabase for retrieving profile information.
        """
        self.db = db

    async def get_profile(self, name: str) -> AuthorProfile:
        """
        Retrieve the historical profile of an author.
        
        Args:
            name: The name of the author to retrieve a profile for.
            
        Returns:
            An AuthorProfile object for the specified author name.
        """
        # In a more advanced implementation, this might perform additional lookups or analysis.
        return self.db.get_author(name)
