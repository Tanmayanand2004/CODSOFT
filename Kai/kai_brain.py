"""
Kai - Advanced AI Chatbot Brain
Intelligent NLP processing with multiple APIs and advanced features
"""

import spacy
import re
import requests
import unicodedata
from datetime import datetime
import random
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Load spaCy model with fallback
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("✅ spaCy model loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ spaCy model not available, using fallback: {e}")
    # Fallback NLP class
    class SimpleNLP:
        def __call__(self, text):
            return SimpleDoc(text)
    
    class SimpleDoc:
        def __init__(self, text):
            self.text = text
            self.ents = []
    
    nlp = SimpleNLP()

# API Configuration
OPENWEATHER_API_KEY = "bdf9d40c08e95771e35e688eb15e3bc6"  # Same as VeltriX
DEFAULT_CITY = "Delhi"

# Kai's personality and responses
KAI_IDENTITY = {
    "name": "Kai",
    "creator": "Your Creator - a brilliant AI enthusiast",
    "personality": "minimalist, helpful, slightly witty",
    "greeting_responses": [
        "Hello! I'm Kai, your intelligent assistant. How can I help you today?",
        "Hey there! Kai here, ready to assist. What can I do for you?",
        "Hi! I'm Kai - your AI companion. What would you like to know?",
        "Greetings! Kai at your service. How may I assist you?",
        "Hello! This is Kai. What brings you here today?"
    ],
    "farewell_responses": [
        "Goodbye! It was great chatting with you. Take care!",
        "See you later! Feel free to come back anytime.",
        "Farewell! Wishing you a wonderful day ahead.",
        "Bye for now! I'll be here whenever you need me.",
        "Take care! Thanks for the great conversation."
    ],
    "identity_responses": [
        "I'm Kai - an intelligent AI assistant designed to be helpful, minimalist, and occasionally witty.",
        "Nice to meet you! I'm Kai, your friendly AI companion built to assist with various tasks.",
        "I'm Kai - think of me as your digital assistant with a personality.",
        "The name's Kai! I'm an AI assistant that tries to be both smart and personable."
    ],
    "creator_responses": [
        "I was created by a brilliant AI enthusiast who wanted to build something special.",
        "My creator is a talented developer passionate about AI and human-computer interaction.",
        "I'm the brainchild of an innovative developer who loves pushing the boundaries of AI.",
        "My creator? A visionary who believes in making AI both powerful and approachable."
    ]
}

# Enhanced response templates
INTENT_RESPONSES = {
    "greeting": lambda: random.choice(KAI_IDENTITY["greeting_responses"]),
    "farewell": lambda: random.choice(KAI_IDENTITY["farewell_responses"]),
    "identity": lambda: random.choice(KAI_IDENTITY["identity_responses"]),
    "creator": lambda: random.choice(KAI_IDENTITY["creator_responses"]),
    "help": "I'm Kai, and I can help you with weather updates, current time & date, jokes, motivational quotes, mathematical calculations, multiplication tables, and much more! Just ask me naturally.",
    "thanks": lambda: random.choice([
        "You're very welcome! Happy to help.",
        "My pleasure! That's what I'm here for.",
        "Anytime! Glad I could be useful.",
        "You're welcome! Feel free to ask anything else.",
        "Happy to assist! Is there anything else you need?"
    ]),
    "skills": "I have quite a few skills! I can check weather, tell time & date, share jokes and quotes, solve math problems, create multiplication tables, and engage in friendly conversation. What would you like to try?",
    "clear": "CLEAR_CHAT_HISTORY",
    "default": lambda: random.choice([
        "I'm not quite sure what you mean. Could you rephrase that?",
        "Hmm, I didn't understand that. Can you try asking differently?",
        "I'm still learning! Could you explain that in another way?",
        "That's outside my current understanding. Try asking something else!"
    ])
}

# Contextual follow-up responses
CONTEXT_RESPONSES = {
    "joke": [
        "Glad I could make you smile! 😄",
        "Humor is one of my favorite features!",
        "I've got plenty more jokes where that came from!",
        "Nothing beats a good laugh, right?",
        "Comedy is definitely my strong suit!"
    ],
    "motivation": [
        "Hope that inspires you to keep pushing forward!",
        "Sometimes we all need a little motivation boost.",
        "Wisdom comes from many places - glad I could share some!",
        "Keep that positive energy flowing!",
        "You've got this! Stay motivated!"
    ],
    "weather": [
        "Weather info is always handy for planning your day!",
        "Hope that helps with your plans!",
        "Stay prepared for whatever weather comes your way!",
        "I'm here for all your weather updates!"
    ],
    "time_date": [
        "Time management is key to productivity!",
        "Always good to keep track of time!",
        "Hope that helps you stay on schedule!"
    ],
    "calculation": [
        "Math is one of my favorite subjects!",
        "Numbers never lie - unlike my jokes! 😉",
        "Need any other calculations? I'm here!",
        "I love crunching numbers for you!"
    ]
}

# Weather context responses
WEATHER_CONTEXT_RESPONSES = {
    "hot": [
        "Yeah, it's really hot! 🔥 Stay hydrated and try to stay cool!",
        "Absolutely! That's quite hot. Perfect weather for some AC and cold drinks! ❄️",
        "Oh wow, definitely on the hot side! Time to find some shade! ☀️",
        "You're right, that's pretty warm! Make sure to drink plenty of water! 💧",
        "Yep, it's scorching! Great pool weather though! 🏊‍♂️"
    ],
    "cold": [
        "Brr! 🥶 That's definitely cold! Time to bundle up!",
        "Yeah, pretty chilly! Perfect sweater weather! 🧥",
        "Oh that's cold alright! Hot chocolate weather for sure! ☕",
        "Absolutely freezing! Stay warm out there! ❄️",
        "You're right, that's cold! Time for some cozy blankets! 🛋️"
    ],
    "nice": [
        "Right? Perfect weather! 🌤️ Great day to be outside!",
        "Absolutely! Couldn't ask for better weather! ✨",
        "I agree! Ideal conditions for any outdoor activities! 🌿",
        "Yeah, just perfect! Nature's at its best! 🌸",
        "Totally! Weather like this makes everything better! 😊"
    ],
    "rain": [
        "Yeah, it's quite wet out there! ☔ Perfect for staying cozy indoors!",
        "Right? Rain can be so peaceful though! 🌧️",
        "I agree! Great reading weather! 📚",
        "Yep, pretty soggy! Time for some hot tea! ☕",
        "Absolutely! Perfect excuse to stay in and relax! 🏠"
    ]
}

# Advanced intent patterns
INTENT_PATTERNS = {
    "greeting": [
        r"\b(hi|hello|hey|good morning|good afternoon|good evening|greetings|howdy)\b"
    ],
    "farewell": [
        r"\b(bye|goodbye|exit|see you|see ya|quit|later|farewell|adios|ciao)\b"
    ],
    "time": [
        r"\b(what.?s the time|current time|tell me the time|time now|what time is it|time right now)\b"
    ],
    "date": [
        r"\b(today.?s date|what.?s the date|current date|which day|what day is it|date today)\b"
    ],
    "identity": [
        r"\b(who are you|what.?s your name|identify yourself|your name|what is your name|tell me about yourself)\b"
    ],
    "creator": [
        r"\b(who created you|who made you|your creator|your developer|who built you|who designed you)\b"
    ],
    "help": [
        r"\b(help|assist|what can you do|how can you help|commands|capabilities|features)\b"
    ],
    "thanks": [
        r"\b(thank you|thanks|thx|appreciate|cheers|nice|great|cool|good job|awesome|well done|brilliant|excellent|perfect|amazing|wonderful|fantastic|love it|hilarious|inspiring|very funny|so funny|lol|haha|good|good one|funny|that\'s funny|made me laugh|loved it|loved that|nice joke|good joke|great joke|motivating|motivational|inspiring words|wise|wisdom|great quote|nice quote|love that quote|helpful|useful|informative|interesting|lmao|rofl|ha|hehe)\b"
    ],
    "joke": [
        r"\b(joke|make me laugh|tell me something funny|say something funny|humor|humour|funny)\b"
    ],
    "motivation": [
        r"\b(motivate me|motivation|inspire me|feeling low|quote|quotes|tell me a quote|need inspiration|wisdom|wise words)\b"
    ],
    "skills": [
        r"\b(skill|skills|abilities|what you can do|features|functions|capabilities|what do you offer)\b"
    ],
    "weather": [
        r"\b(weather|temperature|forecast|climate|hot|cold|raining|weather in|temperature in|how.?s the weather)\b"
    ],
    "calculation": [
        r"(\d+[\+\-\*\/x\(\)]*[\+\-\*\/x\d\(\)]*)|calculate|calculator|compute|math|arithmetic|solve|equation|what\s+is\s+[\d\+\-\*\/x\(\)]+|what.?s\s+[\d\+\-\*\/x\(\)]+|can\s+you\s+solve"
    ],
    "multiplication_table": [
        r"\b(table of \d+|multiplication table|times table|show me.*table|\d+.*table)\b"
    ],
    "clear": [
        r"\b(clear|clear chat|reset|start over|clean|refresh)\b"
    ]
}

# Keep track of conversation context
conversation_context = {
    "last_intent": None,
    "conversation_count": 0
}

def initialize_kai():
    """Initialize Kai's components"""
    logger.info("🧠 Initializing Kai's neural networks...")
    conversation_context["conversation_count"] = 0
    logger.info("🎯 Kai is ready for intelligent conversations!")

def normalize_text(text):
    """Normalize text for better processing"""
    text = unicodedata.normalize("NFKD", text)
    text = text.replace("'", "'").replace("'", "'").replace(""", '"').replace(""", '"')
    return text

def preprocess_input(text):
    """Advanced text preprocessing"""
    text = normalize_text(text)
    text = text.replace("that's", "thats").replace("it's", "its").replace("what's", "whats")
    return text.lower().strip()

def detect_intent(text):
    """Advanced intent detection with priority handling"""
    
    # Handle contextual responses first (like "very funny" after a joke)
    feedback_patterns = [
        r"\b(very funny|so funny|lol|haha|good|good one|funny|that\'s funny|made me laugh|loved it|loved that|nice joke|good joke|great joke)\b",
        r"\b(motivating|motivational|inspiring words|wise|wisdom|great quote|nice quote|love that quote)\b",
        r"\b(helpful|useful|informative|interesting|good to know|nice info|thanks for info)\b"
    ]
    
    for pattern in feedback_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return "thanks"
    
    # Special patterns for calculations
    if re.search(r'\d+\s*[\+\-\*\/x]\s*\d+', text):
        return "calculation"
    
    # Check for multiplication table requests
    if re.search(r'table', text) and re.search(r'\d+', text):
        return "multiplication_table"
    
    # Pattern matching with priority
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return intent
    
    # Single word city detection for weather
    words = text.split()
    if len(words) == 1 and len(words[0]) >= 3 and words[0].isalpha():
        common_words = ["hello", "hi", "hey", "bye", "help", "thanks", "joke", "quote"]
        if words[0].lower() not in common_words:
            return "weather"
    
    return "default"

def extract_city_from_input(user_input):
    """Enhanced city extraction using NLP"""
    doc = nlp(user_input)
    city = None
    
    logger.info(f"Extracting city from input: '{user_input}'")
    
    # First check for general weather queries without specific cities
    general_weather_patterns = [
        r"^what'?s?\s+the\s+weather\s+(today|now)?",
        r"^weather\s+(today|now)?$",
        r"^(current\s+)?weather$",
        r"^how'?s?\s+the\s+weather",
        r"^tell\s+me\s+the\s+weather"
    ]
    
    for pattern in general_weather_patterns:
        if re.search(pattern, user_input.strip(), re.IGNORECASE):
            city = DEFAULT_CITY
            logger.info(f"General weather query detected, using default city: {city}")
            return city
    
    # Try NLP entity recognition for specific cities
    try:
        for ent in doc.ents:
            if hasattr(ent, 'label_') and ent.label_ == "GPE":
                city = ent.text
                logger.info(f"NLP extracted city: {city}")
                break
    except Exception as e:
        logger.warning(f"NLP entity extraction failed: {e}")
    
    # Enhanced regex patterns for specific city detection
    if not city:
        patterns = [
            r"weather\s+in\s+([a-zA-Z][a-zA-Z\s]{2,})",
            r"temperature\s+in\s+([a-zA-Z][a-zA-Z\s]{2,})", 
            r"weather\s+(?:for|of|at)\s+([a-zA-Z][a-zA-Z\s]{2,})",
            r"([a-zA-Z][a-zA-Z\s]{2,})\s+weather",
            r"([a-zA-Z][a-zA-Z\s]{2,})\s+temperature"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                potential_city = match.group(1).strip()
                stop_words = ["the", "weather", "temperature", "current", "what", "is", "like", "today", "now", "this", "that"]
                if potential_city.lower() not in stop_words and len(potential_city) > 2:
                    city = potential_city
                    logger.info(f"Regex extracted city: {city}")
                    break
    
    # If no city found, use default
    if not city:
        city = DEFAULT_CITY
        logger.info(f"No city detected, using default: {city}")
    
    return city

def get_weather_data(user_input):
    """Get weather information with enhanced error handling"""
    city = extract_city_from_input(user_input)
    logger.info(f"Weather request for city: {city}")
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        logger.info(f"Weather API response status: {response.status_code}")
        logger.info(f"Weather API response: {data}")
        
        if response.status_code == 200 and data.get("main"):
            temp = round(data["main"]["temp"])
            feels_like = round(data["main"]["feels_like"])
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"].title()
            
            weather_emoji = "☀️" if "clear" in description.lower() else "🌤️" if "cloud" in description.lower() else "🌧️" if "rain" in description.lower() else "🌨️" if "snow" in description.lower() else "🌫️"
            
            return f"{weather_emoji} Weather in {city.title()}: {temp}°C (feels like {feels_like}°C)\n{description} | Humidity: {humidity}%"
        else:
            error_msg = data.get("message", "Unknown error")
            logger.error(f"Weather API error: {error_msg}")
            return f"Sorry, I couldn't find weather information for '{city}'. Please check the city name and try again."
    
    except requests.exceptions.Timeout:
        logger.error("Weather API timeout")
        return "Weather service is taking too long to respond. Please try again."
    except requests.exceptions.RequestException as e:
        logger.error(f"Weather API request error: {e}")
        return "Weather service is currently unavailable. Please try again later."
    except Exception as e:
        logger.error(f"Weather processing error: {e}")
        return f"I encountered an error while getting weather for {city}. Please try again."

def get_random_joke():
    """Get a random joke with fallbacks"""
    try:
        response = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=5)
        if response.status_code == 200:
            joke_data = response.json()
            return f"😄 {joke_data['setup']}\n\n{joke_data['punchline']}"
    except:
        pass
    
    # Fallback jokes
    fallback_jokes = [
        "😄 Why don't scientists trust atoms?\n\nBecause they make up everything!",
        "😄 What do you call a fake noodle?\n\nAn impasta!",
        "😄 Why did the scarecrow win an award?\n\nHe was outstanding in his field!",
        "😄 What's the best thing about Switzerland?\n\nI don't know, but the flag is a big plus!",
        "😄 Why don't eggs tell jokes?\n\nThey'd crack each other up!"
    ]
    return random.choice(fallback_jokes)

def get_motivational_quote():
    """Get an inspirational quote with fallbacks"""
    try:
        response = requests.get("https://zenquotes.io/api/random", timeout=5)
        if response.status_code == 200:
            quote_data = response.json()
            return f"💭 \"{quote_data[0]['q']}\"\n\n— {quote_data[0]['a']}"
    except:
        pass
    
    # Fallback quotes
    fallback_quotes = [
        "💭 \"The only way to do great work is to love what you do.\"\n\n— Steve Jobs",
        "💭 \"Innovation distinguishes between a leader and a follower.\"\n\n— Steve Jobs",
        "💭 \"Stay hungry, stay foolish.\"\n\n— Steve Jobs",
        "💭 \"The future belongs to those who believe in the beauty of their dreams.\"\n\n— Eleanor Roosevelt",
        "💭 \"It is during our darkest moments that we must focus to see the light.\"\n\n— Aristotle"
    ]
    return random.choice(fallback_quotes)

def solve_calculation(text):
    """Enhanced mathematical calculation solver with order of operations"""
    # Handle percentage calculations
    percentage_pattern = r'(\d+\.?\d*)%\s*of\s*(\d+\.?\d*)'
    percentage_match = re.search(percentage_pattern, text)
    if percentage_match:
        try:
            percent = float(percentage_match.group(1))
            base = float(percentage_match.group(2))
            result = base * percent / 100
            return f"🔢 {percent}% of {base} = {result:g}"
        except:
            pass
    
    # Extract mathematical expression
    # Handle complex expressions like 5+5*2, 10-3*2, etc.
    math_pattern = r'[\d+\-*/.\s()]+'
    expression = re.search(math_pattern, text.replace('x', '*').replace('÷', '/'))
    
    if expression:
        try:
            # Clean the expression
            expr = expression.group().strip()
            # Remove spaces and validate
            expr = re.sub(r'\s+', '', expr)
            
            # Security check - only allow numbers, operators, and parentheses
            if re.match(r'^[\d+\-*/.()]+$', expr):
                # Evaluate with proper order of operations
                result = eval(expr)
                
                # Format the result nicely
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                
                return f"🔢 {expr.replace('*', '×').replace('/', '÷')} = {result}"
            else:
                return "🚫 Invalid mathematical expression. Please use only numbers and basic operators (+, -, *, /)."
                
        except ZeroDivisionError:
            return "🚫 Division by zero is not allowed!"
        except Exception as e:
            # Fallback to simple two-number operations
            math_pattern = r'(\d+\.?\d*)\s*([+\-*/x])\s*(\d+\.?\d*)'
            match = re.search(math_pattern, text.replace('x', '*'))
            
            if match:
                try:
                    num1 = float(match.group(1))
                    operator = match.group(2)
                    num2 = float(match.group(3))
                    
                    if operator == '+':
                        result = num1 + num2
                    elif operator == '-':
                        result = num1 - num2
                    elif operator == '*':
                        result = num1 * num2
                    elif operator == '/':
                        if num2 == 0:
                            return "🚫 Division by zero is not allowed!"
                        result = num1 / num2
                    
                    return f"🔢 {num1:g} {operator} {num2:g} = {result:g}"
                except:
                    pass
    
    return "🤔 I couldn't solve that equation. Try something like '5 + 3', '10 * 2', or '5+5*2'."

def generate_times_table(text):
    """Generate multiplication table in vertical format"""
    number_match = re.search(r'\d+', text)
    if not number_match:
        return "🔢 Please specify a number for the multiplication table (e.g., 'table of 7')."
    
    number = int(number_match.group())
    if number > 20:
        return "🔢 Let's keep it reasonable! Please choose a number between 1 and 20."
    
    table = [f"📊 Multiplication Table for {number}:\n"]
    
    for i in range(1, 11):
        result = number * i
        table.append(f"{number} × {i} = {result}")
    
    return "\n".join(table)

def detect_weather_context(user_input):
    """Detect weather-related context comments"""
    user_input_lower = user_input.lower()
    
    # Hot/warm context
    hot_patterns = [
        r"\b(hot|warm|burning|scorching|sweltering|boiling|blazing)\b",
        r"it'?s hot",
        r"so hot",
        r"really hot",
        r"very hot",
        r"quite hot"
    ]
    
    # Cold context  
    cold_patterns = [
        r"\b(cold|freezing|chilly|frigid|icy|frozen)\b",
        r"it'?s cold",
        r"so cold", 
        r"really cold",
        r"very cold",
        r"quite cold"
    ]
    
    # Nice weather context
    nice_patterns = [
        r"\b(nice|good|great|perfect|beautiful|lovely|pleasant|amazing)\b.*\b(weather|day)\b",
        r"\b(weather|day)\b.*\b(nice|good|great|perfect|beautiful|lovely|pleasant|amazing)\b"
    ]
    
    # Rainy context
    rain_patterns = [
        r"\b(rainy|wet|raining|pouring|drizzling)\b",
        r"it'?s raining",
        r"so wet",
        r"getting wet"
    ]
    
    for pattern in hot_patterns:
        if re.search(pattern, user_input_lower):
            return "hot"
    
    for pattern in cold_patterns:
        if re.search(pattern, user_input_lower):
            return "cold"
            
    for pattern in nice_patterns:
        if re.search(pattern, user_input_lower):
            return "nice"
            
    for pattern in rain_patterns:
        if re.search(pattern, user_input_lower):
            return "rain"
    
    return None

def get_current_time():
    """Get current time with emoji"""
    current_time = datetime.now().strftime('%I:%M %p')
    return f"🕐 The current time is {current_time}"

def get_current_date():
    """Get current date with emoji"""
    current_date = datetime.now().strftime('%A, %B %d, %Y')
    return f"📅 Today is {current_date}"

def get_response(user_input):
    """Generate intelligent response based on user input"""
    global conversation_context
    
    # Update conversation count
    conversation_context["conversation_count"] += 1
    
    # Preprocess input
    cleaned_input = preprocess_input(user_input)
    intent = detect_intent(cleaned_input)
    
    logger.info(f"User input: '{user_input}' -> Intent: '{intent}' -> Last intent: '{conversation_context.get('last_intent')}'")
    
    # Generate response based on intent
    response = ""
    
    if intent == "greeting":
        response = INTENT_RESPONSES["greeting"]()
    elif intent == "farewell":
        response = INTENT_RESPONSES["farewell"]()
    elif intent == "identity":
        response = INTENT_RESPONSES["identity"]()
    elif intent == "creator":
        response = INTENT_RESPONSES["creator"]()
    elif intent == "help":
        response = INTENT_RESPONSES["help"]
    elif intent == "thanks":
        # Context-aware thanks response
        last_intent = conversation_context.get("last_intent")
        if last_intent in CONTEXT_RESPONSES:
            response = random.choice(CONTEXT_RESPONSES[last_intent])
            logger.info(f"Context-aware thanks response for last intent: {last_intent}")
        else:
            response = INTENT_RESPONSES["thanks"]()
            logger.info("Generic thanks response")
    elif intent == "skills":
        response = INTENT_RESPONSES["skills"]
    elif intent == "time":
        response = get_current_time()
        conversation_context["last_intent"] = "time_date"
    elif intent == "date":
        response = get_current_date()
        conversation_context["last_intent"] = "time_date"
    elif intent == "weather":
        response = get_weather_data(user_input)
        conversation_context["last_intent"] = "weather"
    elif intent == "joke":
        response = get_random_joke()
        conversation_context["last_intent"] = "joke"
    elif intent == "motivation":
        response = get_motivational_quote()
        conversation_context["last_intent"] = "motivation"
    elif intent == "calculation":
        response = solve_calculation(user_input)
        conversation_context["last_intent"] = "calculation"
    elif intent == "multiplication_table":
        response = generate_times_table(user_input)
        conversation_context["last_intent"] = "calculation"
    elif intent == "clear":
        response = "CLEAR_CHAT_HISTORY"
        conversation_context = {"last_intent": None, "conversation_count": 0}
    else:
        # Check for weather context responses
        weather_context = detect_weather_context(user_input)
        last_intent = conversation_context.get("last_intent")
        
        if weather_context and last_intent == "weather":
            response = random.choice(WEATHER_CONTEXT_RESPONSES[weather_context])
            logger.info(f"Weather context response: {weather_context}")
        else:
            response = INTENT_RESPONSES["default"]()
    
    # Update last intent (except for thanks to preserve context)
    if intent != "thanks":
        conversation_context["last_intent"] = intent
    
    logger.info(f"Generated response: '{response[:100]}...'")
    return response

# Testing function
if __name__ == "__main__":
    initialize_kai()
    print("🤖 Kai is ready for testing!")
    
    test_inputs = [
        "Hello Kai!",
        "What's the weather in London?",
        "Tell me a joke",
        "What is 15 + 27?",
        "Thanks!"
    ]
    
    for test_input in test_inputs:
        print(f"\nUser: {test_input}")
        print(f"Kai: {get_response(test_input)}")
