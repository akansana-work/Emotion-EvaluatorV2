import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import boto3
import json

# Download necessary NLTK data
nltk.download('vader_lexicon', quiet=True)

class CustomerFeedbackAnalyzer:
    def __init__(self):
        """Initialize sentiment analyzer and AWS Bedrock model"""
        # Set up sentiment analyzer
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Initialize AWS Bedrock client
        # Requires IAM Role with Bedrock Access attached to EC2
        self.bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Meta Llama 3 8B Instruct model via Bedrock
        self.model_id = 'meta.llama3-8b-instruct-v1:0'
    
    def analyze_sentiment(self, text):
        """Analyze sentiment using NLTK's VADER"""
        scores = self.sentiment_analyzer.polarity_scores(text)
        compound = scores['compound']
        
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
            
        return {
            'sentiment': sentiment,
            'score': compound,
            'details': scores
        }
    
    def generate_summary(self, text):
        """Generate a summary of likes and dislikes using Amazon Bedrock"""
        
        # Llama 3 requires a specific prompt formatting
        prompt = f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>
Please analyze the following customer feedback and generate a concise summary that highlights:
1. What the customer liked (positive points)
2. What the customer disliked or had concerns about (negative points)

Feedback: {text}

Respond ONLY with a valid JSON object in this exact format:
{{
    "liked": ["point 1", "point 2"],
    "disliked": ["point 1", "point 2"]
}}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        
        # Llama 3 payload format for Bedrock
        body = json.dumps({
            "prompt": prompt,
            "max_gen_len": 200, # Hard limit on response length to save money
            "temperature": 0.5,
        })
        
        try:
            response = self.bedrock_client.invoke_model(
                body=body,
                modelId=self.model_id,
                accept='application/json',
                contentType='application/json'
            )
            
            response_body = json.loads(response.get('body').read())
            return response_body['generation']
            
        except Exception as e:
            # Fallback error structure
            return f'{{"liked": [], "disliked": [], "error": "Bedrock connection failed: {str(e)}"}}'
    
    def analyze_feedback(self, text):
        """Complete feedback analysis with sentiment and summary generation"""
        sentiment_result = self.analyze_sentiment(text)
        summary = self.generate_summary(text)
        
        return {
            'sentiment_analysis': sentiment_result,
            'summary': summary
        }

# Example usage (CLI Fallback)
def main():
    analyzer = CustomerFeedbackAnalyzer()
    feedback = input("Please enter the customer feedback: ")
    result = analyzer.analyze_feedback(feedback)
    
    print(f"\nSentiment: {result['sentiment_analysis']['sentiment']} (Score: {result['sentiment_analysis']['score']:.2f})")
    print("\nSummary of Customer Feedback:")
    print(result['summary'])

if __name__ == "__main__":
    main()