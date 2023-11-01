import telebot
from apscheduler.schedulers.background import BackgroundScheduler
import random
import os
import numpy as np
import sqlite3
import io
import matplotlib.pyplot as plt
from telebot import types, TeleBot
from keep_alive import keep_alive

TOKEN = 'YOUR TG TOKEN'
bot = telebot.TeleBot(TOKEN)

# SQLite3 connection
conn = sqlite3.connect('subscribers.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS subscribers (user_id INTEGER PRIMARY KEY)')
conn.commit()

keep_alive()

# Function to get all subscribers from the database
def get_subscribers():
    cursor.execute('SELECT user_id FROM subscribers')
    return {row[0] for row in cursor.fetchall()}

# List of subscribers (store user ids)
subscribers = get_subscribers()

quotes = [
    "Your limitation—it's only your imagination.",
    "Push yourself, because no one else is going to do it for you.",
    "Sometimes later becomes never. Do it now.",
    "Great things never come from comfort zones.",
    "Dream it. Wish it. Do it.",
    "Success doesn’t just find you. You have to go out and get it.",
    "The harder you work for something, the greater you’ll feel when you achieve it.",
    "Dream bigger. Do bigger.",
    "Don’t stop when you’re tired. Stop when you’re done.",
    "Wake up with determination. Go to bed with satisfaction.",
    "Do something today that your future self will thank you for.",
    "Little things make big days.",
    "It’s going to be hard, but hard does not mean impossible.",
    "Don’t wait for opportunity. Create it.",
    "Sometimes we’re tested not to show our weaknesses, but to discover our strengths.",
    "The key to success is to focus on goals, not obstacles.",
    "Dream it. Believe it. Build it.",
    "Don't tell everyone your plans, instead show them your results.",
    "I am not a product of my circumstances. I am a product of my decisions.",
    "Don’t be afraid to give up the good to go for the great.",
    "I find that the harder I work, the more luck I seem to have.",
    "The road to success and the road to failure are almost exactly the same.",
    "Success is what happens after you have survived all of your disappointments.",
    "You don’t find will power, you create it.",
    "Your passion is waiting for your courage to catch up.",
    "Magic is believing in yourself. If you can make that happen, you can make anything happen.",
    "If you want to fly give up everything that weighs you down.",
    "You are not your resume, you are your work.",
    "The way to get started is to quit talking and begin doing.",
    "If you're offered a seat on a rocket ship, don't ask what seat! Just get on.",
    # Add more quotes as needed
]

# Function to send a random quote to a specific user
def send_random_quote(chat_id):
    quote = random.choice(quotes)

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 2))  # width, height in inches
    plt.axis('off')
    ax.text(0.5, 0.5, quote, fontsize=24, va='center', ha='center', wrap=True)

    # Save the figure to a BytesIO object
    img_byte_array = io.BytesIO()
    plt.savefig(img_byte_array, format='png', bbox_inches='tight', pad_inches=0.5)
    img_byte_array = img_byte_array.getvalue()
    plt.close(fig)

    # Send image
    bot.send_photo(chat_id, ('quote.png', img_byte_array))


@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id

    # Check if user is already subscribed
    if chat_id not in subscribers:
        subscribers.add(chat_id)

        # Send the user their first motivational quote immediately
        quote = random.choice(quotes)
        bot.send_message(chat_id, quote)

    # Creating a keyboard with buttons for the remaining commands
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        types.KeyboardButton("/start"),
        types.KeyboardButton("/stop"),
        types.KeyboardButton("/help"),
        types.KeyboardButton("/support")
    ]

    # Adding buttons to the keyboard in two columns
    markup.row(buttons[0], buttons[1])
    markup.row(buttons[2], buttons[3])

    # List of all available commands and their descriptions
    commands = [
        "/start - Start the bot and receive daily quotes",
        "/stop - Unsubscribe from daily motivational quotes",
        "/help - Show all available commands",
        "/support - Contact support"
    ]

    # Join the commands list into a single string, separated by new lines
    commands_text = "\n\n".join(commands)

    # Send the welcome message, commands list, and keyboard
    bot.send_message(chat_id, "Welcome to the Motivational Quotes Bot! 🎉\n\n"
                              "Here are all the available commands:\n" + commands_text,
                     reply_markup=markup)


@bot.message_handler(commands=['help'])
def send_help(message):
    # Create a new reply keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)

    # Define the buttons for all available commands
    buttons = [
        types.KeyboardButton('/start'),
        types.KeyboardButton('/stop'),
        types.KeyboardButton('/help'),
        types.KeyboardButton('/support')
    ]

    # Add the buttons to the keyboard in rows of two
    markup.add(*buttons)

    # Send a message with the keyboard
    bot.send_message(message.chat.id, "Here are the available commands:", reply_markup=markup)


@bot.message_handler(commands=['stop', 'unsubscribe'])
def send_goodbye(message):
    chat_id = message.chat.id
    if chat_id in subscribers:
        subscribers.remove(chat_id)
        bot.send_message(chat_id, "You have unsubscribed from daily motivational quotes. Feel free to subscribe again anytime! 👋")
    else:
        bot.send_message(chat_id, "You are not currently subscribed.")


@bot.message_handler(commands=['support'])
def send_support(message):
    # Create a new inline keyboard
    markup = types.InlineKeyboardMarkup()

    # Define the inline button
    # Replace 'https://yourlink.com' with the actual link to your support account or page
    support_button = types.InlineKeyboardButton(text="Text Support", url="https://t.me/AmaAlex009")

    # Add the button to the keyboard
    markup.add(support_button)

    # Send a message with the inline keyboard
    bot.send_message(message.chat.id, "Need support? Click the button below:", reply_markup=markup)



# Function to send daily quote
def send_daily_quote():
    for chat_id in subscribers:
        send_random_quote(chat_id)

# Schedule daily quote sending
scheduler = BackgroundScheduler(timezone='UTC')  # Set your timezone
scheduler.add_job(send_daily_quote, 'cron', hour=8, minute=0, second=0)
scheduler.start()


# Polling loop
bot.polling(none_stop=True)

