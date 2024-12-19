import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Bot Token from BotFather
BOT_TOKEN = "7381647603:AAHFgD6hH3L9vr23fr1Ezn62Y_9SYpb8gX0"

# Replace with your channel username and valid invite link
CHANNEL = {
    "username": "@xstream_links2",  # Replace with your channel username
    "invite_link": "@xstream_links2"  # Replace with your valid invite link
}

# The link to send after verifying the channel join
ACCESS_LINK = "https://t.me/opcontentsbot/Trbxdwnldr"

# Path to user database file
USER_DB_FILE = "user_db.json"

# Load user database
def load_user_db():
    try:
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save user database
def save_user_db(user_db):
    with open(USER_DB_FILE, "w") as f:
        json.dump(user_db, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /start command. Sends the user a message with the channel join link and a button to verify.
    """
    user_id = update.message.chat.id
    username = update.message.chat.username

    # Add the user to the database
    user_db = load_user_db()
    if str(user_id) not in user_db:
        user_db[str(user_id)] = {"username": username}
        save_user_db(user_db)

    # Prepare the message with the channel join link
        # Prepare the message with the channel join link
    message = (
        f"""Hi! To use this bot, you must first join the following channels:

        🔹 [Join Channel 1](https://t.me/+L-mSWNllYqs5NGJl)
        🔹 [Join Channel 2](https://t.me/+jnL6tk-ICTViZjBl)
        🔹 [Join {CHANNEL['username']}]({CHANNEL['invite_link']})

        Once you've joined all the channels, click the button below to verify your membership."""
    )

    # Create a button for verifying the join
    keyboard = [[InlineKeyboardButton("✅ I Joined", callback_data="check_membership")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message
    await update.message.reply_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Verifies if the user has joined the channel and sends the access link if verified.
    """
    query = update.callback_query
    user_id = query.message.chat.id

    try:
        # Check the membership status of the user in the channel
        member_status = await context.bot.get_chat_member(chat_id=CHANNEL["username"], user_id=user_id)

        # Allowed statuses: member, administrator, creator
        if member_status.status not in ["member", "administrator", "creator"]:
            await query.answer("You haven't joined the channel yet. Please join and try again!", show_alert=True)
            return
    except Exception as e:
        # Handle cases where the bot cannot check membership
        await query.answer("An error occurred while checking your membership. Please ensure the bot is an admin in the channel.", show_alert=True)
        return

    # Send the access link button if the user is verified
    keyboard = [[InlineKeyboardButton("Click Here for TeraBox Downloader", url=ACCESS_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="🎉 You’ve successfully joined the channel! Click the button below to USE OUR DOWNLOADER:",
        reply_markup=reply_markup
    )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Allows the admin to broadcast a message to all users in the database.
    """
    user_id = update.message.chat.id
    username = update.message.chat.username
    user_db = load_user_db()

    # Check if the sender is an admin (replace with your admin username)
    if username != "@pipipix6":  # Replace with your Telegram username
        await update.message.reply_text("You are not authorized to use this command.")
        return

    # Get the broadcast message
    broadcast_message = " ".join(context.args)
    if not broadcast_message:
        await update.message.reply_text("Please provide a message to broadcast. Example: /broadcast Hello everyone!")
        return

    # Broadcast the message to all users
    failed = 0
    for user in user_db:
        try:
            await context.bot.send_message(chat_id=int(user), text=broadcast_message)
        except Exception:
            failed += 1

    await update.message.reply_text(f"Broadcast completed. Failed to send to {failed} users.")

def main():
    """
    Main function to start the bot.
    """
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_membership, pattern="check_membership"))
    application.add_handler(CommandHandler("broadcast", broadcast))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
