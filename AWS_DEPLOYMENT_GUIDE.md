# AWS Deployment Guide: Emotion Evaluator

This guide provides step-by-step instructions to deploy the "Echoes of Emotion" web application on Amazon Web Services (AWS). It utilizes EC2 for hosting, IAM for security, Amazon Bedrock for generative AI (Meta Llama 3), and Amazon RDS (MySQL) for persistent data storage.

## Phase 1: AWS Console Configuration

### Step 1: Amazon Bedrock Model Access
*Note: AWS recently updated Bedrock! Serverless foundation models (like Meta Llama 3) are now automatically enabled by default. You do not need to manually request access anymore.*

### Step 2: Create an IAM Role for EC2
We need to give the server permission to use Bedrock without storing passwords or API keys on the server itself.
1. In the AWS Console, search for **IAM** and open it.
2. On the left menu, click **Roles**, then click **Create role**.
3. Under "Trusted entity type", select **AWS service**, and for "Use case", select **EC2**. Click Next.
4. In the permissions search box, type `AmazonBedrockFullAccess`.
5. Check the box next to the policy `AmazonBedrockFullAccess`. Click Next.
6. Name the role `EC2-Bedrock-Role`.
7. Click **Create role**.

### Step 3: Launch the EC2 Instance
1. Go to the **EC2 Dashboard** and click **Launch instance**.
2. **Name:** `EmotionEvaluator-Demo`
3. **OS:** Ubuntu Server 24.04 LTS (Free Tier eligible).
4. **Instance Type:** `t2.micro`.
5. **Key Pair:** Select your existing key pair (e.g., from the House Price project).
6. **Network Settings (Security Group):**
   * Check **Allow SSH traffic** (Port 22).
   * Check **Allow HTTP traffic** (Port 80).
   * Check **Allow HTTPS traffic** (Port 443).
   * *Important:* Click "Edit" on the Network Settings, add a Custom TCP rule for Port **8501** (Anywhere). This is the port Streamlit uses.
7. **Advanced Details:**
   * Scroll down to **IAM instance profile**.
   * Select the `EC2-Bedrock-Role` you created in Step 2.
8. Click **Launch instance**.

### Step 4: Provision an Amazon RDS (MySQL) Instance
1. Go to the **RDS Dashboard** and click **Create database**.
2. Select **Standard create** and choose **MySQL**.
3. Under Templates, choose **Free tier** (if available) or **Dev/Test**.
4. Set the **DB instance identifier** (e.g., `emotion-db`), **Master username** (e.g., `admin`), and a secure **Master password**.
5. Under Connectivity, ensure **Public access** is set appropriately (Yes if accessing from local for testing, No if only EC2 needs access) and create/select a VPC security group that allows inbound traffic on port 3306 from your EC2 instance's security group.
6. Expand **Additional configuration** and provide an **Initial database name** (e.g., `emotion_evaluator_db`). This is required so the DB exists.
7. Click **Create database** (this will take a few minutes).

---

## Phase 2: Server Setup & Application Deployment

Wait for your instance to start, then SSH into it using your terminal:
```bash
ssh -i /path/to/your-key.pem ubuntu@<your-ec2-public-ip>
```

### Step 1: Prepare the Environment
Run the following commands on the server to install Python and necessary tools:
```bash
# Update packages
sudo apt update -y

# Install pip and venv
sudo apt install python3-pip python3-venv -y

# Clone your repository (replace with your actual github link)
git clone <your-github-repo-url>
cd <your-repo-folder>
```

### Step 2: Install Dependencies
Create an isolated virtual environment and install the required Python packages.
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Download the NLTK Sentiment Lexicon
python -m nltk.downloader vader_lexicon
```

### Step 3: Configure Database Credentials
You need to provide the application with your RDS credentials using a `.env` file.
```bash
# Create the .env file
nano .env
```
Paste the following inside the file, replacing the values with your actual RDS details:
```env
DB_HOST=<your-rds-endpoint>
DB_USER=<your-master-username>
DB_PASSWORD=<your-master-password>
DB_NAME=<your-initial-database-name>
```
Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

### Step 4: Start the Web Application
Streamlit runs an active web server. If you run it normally, it will shut down when you close your SSH terminal. We will use `nohup` to run it in the background forever.

```bash
# Run the Streamlit app in the background
nohup streamlit run app.py &
```

*Press `Enter` to return to the prompt after running the command.*

---

## Phase 3: Accessing the Demo
1. Go to your EC2 Console and find your instance's **Public IPv4 address**.
2. Open a web browser and go to:
   `http://<your-ec2-public-ip>:8501`
3. The UI will appear. You can now share this exact URL with your students!

## Troubleshooting
* **Cannot reach the site:** Double-check that Port 8501 is open in the EC2 Security Group.
* **Bedrock connection failed:** Verify that the IAM Role (`EC2-Bedrock-Role`) is properly attached to the EC2 instance (Right-click instance -> Security -> Modify IAM Role).
* **Llama 3 throws an error:** Ensure you requested model access in the `us-east-1` region (or whichever region your `boto3` client is set to).
