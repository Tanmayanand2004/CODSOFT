"""
Kai - Advanced AI Chatbot with NLP Intelligence
Flask backend with modern UI and rich functionality
"""

from flask import Flask, render_template, request, jsonify
from kai_brain import get_response, initialize_kai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize Kai's NLP components
try:
    initialize_kai()
    logger.info("✅ Kai's brain initialized successfully")
except Exception as e:
    logger.error(f"❌ Error initializing Kai: {e}")

@app.route("/")
def index():
    """Main chat interface"""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Chat endpoint - handles user messages and returns Kai's responses"""
    try:
        user_input = request.json.get("message", "").strip()
        
        if not user_input:
            return jsonify({
                "response": "I didn't receive any input. Could you please say something?",
                "status": "error"
            })
        
        # Get response from Kai's brain
        response = get_response(user_input)
        
        logger.info(f"User: {user_input[:50]}... | Kai: {response[:50]}...")
        
        return jsonify({
            "response": response,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({
            "response": "I'm experiencing some technical difficulties. Please try again.",
            "status": "error"
        }), 500

@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "bot": "Kai",
        "version": "1.0.0"
    })

if __name__ == "__main__":
    logger.info("🤖 Starting Kai - Advanced AI Chatbot")
    logger.info("🚀 Access Kai at http://localhost:5000")
    logger.info("💡 Features: Weather, Jokes, Quotes, Math, Time & More!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
