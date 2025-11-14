import logging
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# -----------------------------
# SETTINGS
# -----------------------------
TOKEN = "8451526641:AAEu4ZsIaeJoaKDs6vcGfhBsjo02ON_KJCE"

GROUP_FILE = "groups.json"

# Load group list
def load_groups():
    if not os.path.exists(GROUP_FILE):
        return []
    with open(GROUP_FILE, "r") as f:
        return json.load(f)

# Save group list
def save_groups(groups):
    with open(GROUP_FILE, "w") as f:
        json.dump(groups, f)

# Logging
logging.basicConfig(level=logging.INFO)
current_group = {}   # Stores user → group mapping temporarily

# -----------------------------
# When bot is added to a group
# -----------------------------
async def added_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type in ["group", "supergroup"]:
        groups = load_groups()

        if chat.id not in groups:
            groups.append(chat.id)
            save_groups(groups)

        await update.message.reply_text("👻 *GhostBot Activated!*\nI will now accept anonymous confessions here.",
                                        parse_mode="Markdown")

# -----------------------------
# /confess command (in DM only)
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return await update.message.reply_text("👻 DM me to confess anonymously.")

    groups = load_groups()
    if not groups:
        return await update.message.reply_text("⚠️ No groups available yet.")

    # Show group list as buttons
    keyboard = [
        [InlineKeyboardButton(f"👻 {gid}", callback_data=f"group_{gid}")]
        for gid in groups
    ]

    await update.message.reply_text("👻 *Choose a group to confess in:*",
                                    reply_markup=InlineKeyboardMarkup(keyboard),
                                    parse_mode="Markdown")


# -----------------------------
# User selects group
# -----------------------------
async def choose_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    group_id = query.data.replace("group_", "")
    user_id = query.from_user.id
    current_group[user_id] = int(group_id)

    await query.edit_message_text(
        "💀 *Ghost is listening...*\nNow send me your confession.",
        parse_mode="Markdown"
    )


# -----------------------------
# Handle confession text
# -----------------------------
async def confession(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in current_group:
        return await update.message.reply_text("Use /start to begin.")

    confession_text = update.message.text
    group_id = current_group[user_id]

    # Send anonymously to the group
    await context.bot.send_message(
        chat_id=group_id,
        text=f"👻 *Anonymous Confession:*\n\n{confession_text}",
        parse_mode="Markdown"
    )

    await update.message.reply_text("🕯️ Your ghost message has been delivered.")

    del current_group[user_id]


# -----------------------------
# MAIN BOT
# -----------------------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, added_to_group))
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(choose_group))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, confession))

app.run_polling()
