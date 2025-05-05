import spacy
import random
import re
from textblob import TextBlob

# Load spaCy's language model
nlp = spacy.load("en_core_web_sm")

# Simple responses based on keywords or patterns
def generate_response(message_content: str) -> str:
    # Process the message content using spaCy
    doc = nlp(message_content.lower())

    sentiment = TextBlob(message_content).sentiment.polarity

    # Always respond to specific queries first
    if re.search(r'\b(hello|hi|hey|greetings)\b', message_content.lower()):
        return "Greetings! I'm DeepSeek-R1, your artificial intelligence assistant. How can I help you today?"

    elif re.search(r'\b(who are you|what is your name)\b', message_content.lower()):
        return "Greetings! I'm DeepSeek-R1, an artificial intelligence assistant created by DeepSeek. I'm at your service and would be delighted to assist you with any inquiries or tasks you may have."
    
    elif re.search(r'\b(help|assist|support)\b', message_content.lower()):
        return "Sure! How can I assist you today? You can ask me anything, whether it's related to tech, programming, or just a casual chat."

    elif re.search(r'\b(weather)\b', message_content.lower()):
        return "I currently don't have weather data, but you can easily check the weather online or using apps like AccuWeather or Weather.com."

    elif re.search(r'\b(joke)\b', message_content.lower()):
        # Send a random joke
        jokes = [
            "Why don't skeletons fight each other? They don't have the guts!",
            "I told my computer I needed a break, and now it won't stop sending me Kit-Kats!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "What do you call fake spaghetti? An impasta!",
            "How does a penguin build its house? Igloos it together!"
        ]
        return random.choice(jokes)

    # Now, handle sentiment-based responses for mood
    if sentiment > 0.1:  # Positive sentiment
        positive_responses = [
            "I'm glad to see you're in a good mood! How can I assist you?",
            "It seems like you're feeling positive! Let me know if you'd like to chat about something exciting!",
            "You're in great spirits today! Is there anything I can help you with?",
            "I can sense your enthusiasm! How can I make your day even better?",
            "You're radiating positivity! What's on your mind?"
        ]
        return random.choice(positive_responses)
    
    elif sentiment < -0.1:  # Negative sentiment
        negative_responses = [
            "I'm sorry to hear that. Is there something I can do to help? Feel free to share what's on your mind.",
            "I sense you're not feeling great. If you need someone to talk to, I'm here for you.",
            "It seems like something might be bothering you. I'm happy to listen and offer assistance if needed.",
            "I understand you're having a rough time. Would you like to talk about it or need advice?",
            "I'm here for you if you'd like to chat. Whatever you're going through, you're not alone."
        ]
        return random.choice(negative_responses)

    elif sentiment == 0:  # Neutral sentiment
        neutral_responses = [
            "I'm here to assist with whatever you need. What can I help you with today?",
            "I see you're in a neutral mood. Anything on your mind?",
            "Feel free to ask me anything you'd like. I'm here to help!",
            "I'm always ready to help you out. What do you need assistance with?",
            "I'm just a message away if you need anything!"
        ]
        return random.choice(neutral_responses)
    
    # Handling more complex topics with spaCy (organization names, places, etc.)
    elif any(ent.label_ == "ORG" for ent in doc.ents):  # Checks for organization names
        return f"It looks like you're talking about a company or organization. How can I assist you with {', '.join([ent.text for ent in doc.ents if ent.label_ == 'ORG'])}? Are you looking for information or help with something specific?"

    elif any(ent.label_ == "GPE" for ent in doc.ents):  # Recognizes geographical places
        places = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
        return f"It looks like you're referring to a location. Are you talking about {', '.join(places)}? Let me know if you'd like more information about that area."

    # More advanced pattern recognition (handling questions, programming, etc.)
    elif re.search(r'\b(code|programming|python|java|javascript|software|development)\b', message_content.lower()):
        return "Ah, it looks like you're talking about programming! I can assist you with coding in Python, Java, or JavaScript. What are you working on?"

    elif re.search(r'\b(game|gaming|video games|esports|gamer|games)\b', message_content.lower()):
        return "Ah, a fellow gamer! What games are you into? I can discuss the latest in gaming, esports, or even help you with tips and tricks for your favorite games."

    # Detecting complex or deep topics (philosophy, science, etc.)
    elif re.search(r'\b(philosophy|science|technology|AI|robotics|future|innovation)\b', message_content.lower()):
        return "You're venturing into deep waters! Let's talk about philosophy, science, or the future of technology. What's on your mind?"

    # Exploring topics related to health, fitness, and wellness
    elif re.search(r'\b(health|fitness|exercise|wellness|workout)\b', message_content.lower()):
        return "Taking care of your health is important! Whether you're looking for workout tips or advice on staying healthy, I'm happy to assist you."

    # Social media or entertainment-related questions
    elif re.search(r'\b(movie|tv|show|entertainment|celebrity)\b', message_content.lower()):
        return "I see you're interested in entertainment! Whether you're looking for movie recommendations or celebrity news, let's chat about the latest shows or films."

    # Handling questions about general knowledge
    elif re.search(r'\b(history|geography|culture|facts|general knowledge)\b', message_content.lower()):
        return "You're inquiring about something interesting! History, geography, and culture are fascinating topics. Feel free to ask anything specific, and I'll provide the best information I can!"

    # Default response if nothing matches
    return "I didn't quite get that. Could you please clarify or ask something else? I'm here to help!"
