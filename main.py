import os
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import pytz
from pymongo import MongoClient, server_api
import certifi

# Set up bot token and webhook URL
TOKEN = os.environ.get('TOKEN')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

# Initialize bot and Flask app
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# MongoDB setup
MONGO_URI = os.environ.get('MONGO_URI')

# Initialize MongoDB client with SSL configuration
client = MongoClient(MONGO_URI, server_api=server_api.ServerApi('1'), tlsCAFile=certifi.where())
db = client['OmegaofTS']
users_collection = db['Users']

# Ensure MongoDB connection
try:
    client.admin.command('ping')
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")

# Ensure 'user_id' is unique in the collection
try:
    users_collection.create_index("user_id", unique=True)
    print("Unique index on 'user_id' created successfully!")
except Exception as e:
    print(f"Failed to create unique index: {e}")

# Set up the webhook
try:
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
    print(f"Webhook set to: {WEBHOOK_URL}")
except Exception as e:
    print(f"Failed to set webhook: {e}")

@app.route('/')
def home():
    """Health check route."""
    return "Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming updates from Telegram."""
    json_data = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "OK", 200

# Handle /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Send a welcome message and save user data to MongoDB."""
    # Fetch user info
    user_name = message.from_user.first_name or "User"
    user_id = message.from_user.id

    # Get current date and time in IST
    ist_timezone = pytz.timezone("Asia/Kolkata")
    current_time_ist = datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S")

    # Welcome message
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

    # Inline buttons
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📚 Learning Resources", callback_data="learning_resources"),
        InlineKeyboardButton("💰 Earn Crypto for FREE", callback_data="earn_crypto"),
        InlineKeyboardButton("🎓 Free Certifications", callback_data="free_certifications"),
        InlineKeyboardButton("📌 Roadmaps", callback_data="roadmaps"),
        InlineKeyboardButton("💀 Modded APKs", callback_data="modded_apks"),
        InlineKeyboardButton("✨ Tricks", callback_data="tricks"),
        InlineKeyboardButton("🏆 Internships", callback_data="internships"),
        InlineKeyboardButton("🎯 Donate Us", callback_data="donate"),
        InlineKeyboardButton("🛠 Free Courses", callback_data="free_courses"),
        InlineKeyboardButton("🔑 Money-Making Ideas", callback_data="money_ideas"),
        InlineKeyboardButton("🎮 Join Wild Guns 2.0", callback_data="wild_guns")
    )

    # Save user data to MongoDB
    user_data = {"user_id": user_id, "first_seen": current_time_ist}
    try:
        # Insert only if the user is not already in the database
        if not users_collection.find_one({"user_id": user_id}):
            users_collection.insert_one(user_data)
            print(f"New user added: {user_id}")
        else:
            print(f"User {user_id} already exists in the database.")
    except Exception as e:
        print(f"Failed to save user data: {e}")

    # Send the welcome message
    bot.send_message(chat_id=message.chat.id, text=welcome_text, reply_markup=markup)

# Handle button presses
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    """Handle button presses."""
    bot.answer_callback_query(
        callback_query_id=call.id,
        text="⚠️ Bot is now under maintenance due to load issues. \n\nPlease try again later!",
        show_alert=True
    )

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
