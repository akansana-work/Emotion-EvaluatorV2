# RDS Integration Steps

This guide outlines the steps taken to integrate Amazon RDS (MySQL) into the Emotion Evaluator V2 project to persist customer feedback and analysis results.

## 1. Updated Dependencies
Added the required dependencies for connecting to a MySQL database and managing environment variables.
* **File Modified:** `requirements.txt`
* **Additions:** `pymysql` and `python-dotenv`.
* **Purpose:** `pymysql` is the python driver to connect with MySQL databases, and `python-dotenv` loads the RDS credentials from a `.env` file securely.

## 2. Created the Database Manager
Implemented a dedicated database module to handle all database operations.
* **New File:** `database.py`
* **Description:** 
  - Retrieves database credentials (host, user, password, database name) from the `.env` file.
  - Establishes a connection to the RDS instance via `pymysql`.
  - Includes a `_create_table_if_not_exists` method to automatically create the `feedback_analysis` table if it doesn't already exist. The table schema stores the feedback text, sentiment, compound score, liked/disliked summaries, and the timestamp.
  - Includes a `save_analysis` method to safely insert new feedback records. Lists (liked, disliked) are converted to comma-separated strings before storing.

## 3. Updated the Main Application
Modified the Streamlit application to utilize the database manager and persist data upon every analysis.
* **File Modified:** `app.py`
* **Changes Made:**
  - Imported `DatabaseManager` from `database`.
  - Created a globally cached function `get_db()` using `@st.cache_resource` to ensure the database connection is initialized only once and shared across multiple Streamlit reruns.
  - Updated the "Analyze Feedback" button's execution block to call `db.save_analysis(feedback, sentiment, score, liked, disliked)` successfully inserting the analyzed data into the RDS table.

## 4. Setup Instructions for Deployment
Before deploying or running this application, you must now configure your environment with the RDS details.

1. **Create an RDS Instance (MySQL):** Provision a MySQL RDS instance in AWS. Make sure its security group allows inbound traffic on port 3306 from your EC2 instance or local machine.
2. **Set up Environment Variables:** Create a `.env` file in the root of your project directory (`EmotionEvaluatorV2/`) with the following keys:
   ```env
   DB_HOST=your-rds-endpoint.us-east-1.rds.amazonaws.com
   DB_USER=your_db_username
   DB_PASSWORD=your_db_password
   DB_NAME=emotion_evaluator_db
   ```
3. **Database Creation:** Ensure that the database specified in `DB_NAME` is already created on your RDS instance (e.g., `CREATE DATABASE emotion_evaluator_db;`). The application will handle the creation of the `feedback_analysis` table automatically.
