import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        """Initialize connection to RDS MySQL."""
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")
        
        # We try to connect. If credentials are not set, it will fail gracefully.
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=pymysql.cursors.DictCursor
            )
            self._create_table_if_not_exists()
        except Exception as e:
            print(f"Database connection error: {e}")
            self.connection = None

    def _create_table_if_not_exists(self):
        """Create the table to store feedback if it does not exist."""
        if not self.connection:
            return

        create_table_query = """
        CREATE TABLE IF NOT EXISTS feedback_analysis (
            id INT AUTO_INCREMENT PRIMARY KEY,
            feedback_text TEXT NOT NULL,
            sentiment VARCHAR(50),
            score FLOAT,
            liked TEXT,
            disliked TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(create_table_query)
            self.connection.commit()
        except Exception as e:
            print(f"Error creating table: {e}")

    def save_analysis(self, feedback, sentiment, score, liked, disliked):
        """Save the feedback and analysis result to RDS."""
        if not self.connection:
            print("Database not connected. Skipping save.")
            return False
            
        insert_query = """
        INSERT INTO feedback_analysis (feedback_text, sentiment, score, liked, disliked)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        # Convert lists to strings for storage
        liked_str = ", ".join(liked) if isinstance(liked, list) else str(liked)
        disliked_str = ", ".join(disliked) if isinstance(disliked, list) else str(disliked)
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insert_query, (feedback, sentiment, score, liked_str, disliked_str))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error saving analysis: {e}")
            return False
