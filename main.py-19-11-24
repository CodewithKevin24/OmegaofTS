import os
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import pytz  # For timezone conversion
from pymongo import MongoClient, server_api  # Import server_api from pymongo
import certifi  # For SSL certificate verification

# Set up the bot token and webhook URL
TOKEN = os.environ.get('TOKEN')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

# Initialize bot and Flask app
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Get MongoDB URI from environment variables
MONGO_URI = os.environ.get('MONGO_URI')

# Set up the webhook
try:
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
    print(f"Webhook set to: {WEBHOOK_URL}")
except Exception as e:
    print(f"Failed to set webhook: {e}")

# Initialize MongoDB client with SSL configuration
try:
    client = MongoClient(MONGO_URI, server_api=server_api.ServerApi('1'), tlsCAFile=certifi.where())
    db = client['OmegaofTSBotUsers']  # The database will be created automatically if not exists
    users_collection = db['Users']    # The collection will be created automatically if not exists

    client.admin.command('ping')  # Test MongoDB connection
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    users_collection = None  # Handle case where MongoDB is not connected

@app.route('/')
def home():
    """Health check route for the bot server."""
    return "Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    """Process incoming Telegram updates."""
    json_data = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "OK", 200

# Handle /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Send a welcome message with user info and current date/time in IST."""

    # Fetch user info
    user_name = message.from_user.first_name or "User"
    user_id = message.from_user.id

    # Get current date and time in IST
    ist_timezone = pytz.timezone("Asia/Kolkata")
    current_time_ist = datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S")  # Format: YYYY-MM-DD HH:MM:SS

    # Welcome message with user details
    welcome_text = (
        f"Welcome {user_name}!\n\n"
        f"Your Telegram User ID: {user_id}\n"
        f"Current Date & Time (IST): {current_time_ist}\n\n"
        "✅ Learning Resources for almost every field\n"
        "✅ Premium Courses FREE Download\n"
        "✅ Modded APKs of Netflix, Prime, Hotstar, Truecaller, etc.\n"
        "✅ Roadmaps for different Careers\n"
        "✅ Internship Opportunities\n"
        "✅ Free Certification Courses\n"
        "✅ Money Making Methods\n\n"
        "And guess what? It's completely FREE 🔥\n"
        "Enjoy 🚩"
    )

    # Create inline buttons
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📚 Learning Resources", callback_data="button_click"),
        InlineKeyboardButton("💰 Earn Crypto for FREE", callback_data="button_click"),
        InlineKeyboardButton("🎓 Free Certifications", callback_data="button_click"),
        InlineKeyboardButton("📌 Roadmaps", callback_data="button_click"),
        InlineKeyboardButton("💀 Modded APKs", callback_data="button_click"),
        InlineKeyboardButton("✨ Tricks", callback_data="button_click"),
        InlineKeyboardButton("🏆 Internships", callback_data="button_click"),
        InlineKeyboardButton("🎯 Donate Us", callback_data="button_click"),
        InlineKeyboardButton("🛠 Free Courses", callback_data="button_click"),
        InlineKeyboardButton("🔑 Money-Making Ideas", callback_data="button_click"),
        InlineKeyboardButton("🎮 Join Wild Guns 2.0", callback_data="button_click")
    )

    # Send the welcome message with the inline keyboard
    bot.send_message(chat_id=message.chat.id, text=welcome_text, reply_markup=markup)

    # Save user data to MongoDB
    if users_collection:
        user_data = {
            "user_id": user_id,
            "user_name": user_name,
            "start_time": current_time_ist,
        }
        # Use update_one with upsert=True to create or update the user document
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": user_data},
            upsert=True
        )
        print(f"User {user_name} data saved to MongoDB.")

def save_user(chat_id):
    try:
        users_collection.update_one(
            {'chat_id': chat_id},
            {'$set': {'chat_id': chat_id}},
            upsert=True
        )
        print(f"User {chat_id} saved to the database.")
    except Exception as e:
        print(f"Failed to save user {chat_id}: {e}")


# Handle button presses
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    """Show a pop-up message when a button is pressed."""
    # Respond with a popup alert
    bot.answer_callback_query(
        callback_query_id=call.id,
        text="⚠️ Bot is now under maintenance due to load issues. \n\nPlease try again later!",
        show_alert=True  # True ensures it displays as a pop-up alert
    )

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
