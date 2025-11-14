from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running."

# ---------------- BOT LOGIC ---------------- #

CONFESSION_PREFIX = "👻 *Ghost Confession*\n\n"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👻 Send me a message and I'll anonymously post it into the group."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Ignore commands
    if text.startswith("/"):
        return

    # Anonymous message format
    confession = CONFESSION_PREFIX + text

    # Send the confession into the same group
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=confession,
        parse_mode="Markdown"
    )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Unknown command.")

# ---------------- START BOT ---------------- #

def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    application.run_polling()

if __name__ == "__main__":
    run_bot()
