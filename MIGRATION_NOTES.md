# Code Migration Notes

This file outlines the changes made to the "Echoes of Emotion" project to prepare it for a Cloud-Native AWS Deployment for a student demo.

## 1. Removed Google Gemini Integration
*   **File:** `nlp.py`
*   **Change:** Deleted `import google.generativeai` and `from dotenv import load_dotenv`.
*   **Why:** Moving away from third-party API keys managed in a local `.env` file to utilizing AWS's managed AI service.

## 2. Integrated Amazon Bedrock (Meta Llama 3)
*   **File:** `nlp.py`
*   **Change:** Added `import boto3` and initialized `self.bedrock_client = boto3.client('bedrock-runtime')`.
*   **Why:** Uses the AWS SDK. When this runs on an EC2 instance with the correct IAM Role, it authenticates automatically without any hardcoded credentials. 
*   **Change:** Updated `generate_summary` to use the Meta Llama 3 8B Instruct model (`meta.llama3-8b-instruct-v1:0`). Modified the prompt to match Llama 3's required prompt formatting (`<|begin_of_text|>...`).

## 3. Added a Web Interface (Streamlit)
*   **File:** `app.py`
*   **Change:** Created a brand new file using the `streamlit` library.
*   **Why:** A command-line interface is not ideal for a student demo. Streamlit provides a professional, interactive web UI in ~50 lines of code. It imports the logic directly from `nlp.py`.

## 4. Updated Dependencies
*   **File:** `requirements.txt`
*   **Change:** Added `boto3` and `streamlit`.
*   **Why:** Ensures the AWS server can easily install the required packages using `pip install -r requirements.txt`.
