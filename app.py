import streamlit as st
from nlp import CustomerFeedbackAnalyzer
import json
from database import DatabaseManager

@st.cache_resource
def get_db():
    return DatabaseManager()

# Setup page config
st.set_page_config(page_title="Echoes of Emotion", page_icon="🎭", layout="centered")

st.title("Echoes of Emotion 🎭")
st.subheader("AI-Powered Sentiment Analyzer")

st.markdown("Enter customer feedback below to analyze sentiment and extract key points using NLTK VADER and AWS Bedrock (Meta Llama 3).")

# Input field (Restricted to 1000 characters to save Bedrock input token costs)
feedback = st.text_area("Customer Feedback:", height=150, max_chars=1000, placeholder="Type the review here... (max 1000 characters)")

# Action button
if st.button("Analyze Feedback", type="primary"):
    if not feedback.strip():
        st.warning("Please enter some feedback first.")
    else:
        with st.spinner("Analyzing sentiment and generating summary..."):
            # Initialize our updated analyzer (no API keys needed thanks to AWS IAM)
            analyzer = CustomerFeedbackAnalyzer()
            result = analyzer.analyze_feedback(feedback)
            
            # Display Sentiment Section
            st.markdown("### 📊 Sentiment Score")
            sentiment = result['sentiment_analysis']['sentiment']
            score = result['sentiment_analysis']['score']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Sentiment", sentiment.upper())
            with col2:
                st.metric("Compound Score", f"{score:.2f}")
                
            # Progress bar mapped from -1.0..1.0 to 0.0..1.0
            st.progress((score + 1) / 2) 
            
            st.divider()
            
            # Display AI Summary Section
            st.markdown("### 💡 Llama 3 Summary")
            summary_raw = result['summary']
            
            try:
                # Llama 3 is instructed to return JSON
                summary_data = json.loads(summary_raw)
                
                liked = summary_data.get("liked", [])
                disliked = summary_data.get("disliked", [])
                
                if liked:
                    st.success("**What they liked:**\n- " + "\n- ".join(liked))
                if disliked:
                    st.error("**What they disliked:**\n- " + "\n- ".join(disliked))
                    
                if "error" in summary_data:
                    st.error(summary_data["error"])
                    
                # Save to database
                db = get_db()
                db.save_analysis(feedback, sentiment, score, liked, disliked)
                    
            except json.JSONDecodeError:
                # Fallback if Llama 3 outputs raw text instead of strict JSON
                st.write(summary_raw)
