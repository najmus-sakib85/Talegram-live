import os
import requests
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8669179456:AAEpPtpcWq3zPvaiLVLm5yrR4YRVBRoM_Og"
FIREBASE_URL = "https://gen-lang-client-0150193289-default-rtdb.firebaseio.com/vault"

SECTION_MAP = {
    "১. ফ্যামিলি ফটো": "part1",
    "২. পার্সোনাল ডকুমেন্ট": "part2",
    "৩. বেস্ট ফটো": "part3",
    "৪. সিক্রেট পার্ট ৪": "part4",
    "৫. সিক্রেট পার্ট ৫": "part5",
    "৬. সিক্রেট পার্ট ৬": "part6",
    "৭. সিক্রেট পার্ট ৭": "part7"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("👨‍👩‍👧‍👦 ১. ফ্যামিলি ফটো"), KeyboardButton("📄 ২. পার্সোনাল ডকুমেন্ট")],
        [KeyboardButton("⭐ ৩. বেস্ট ফটো"), KeyboardButton("📁 ৪. সিক্রেট পার্ট ৪")],
        [KeyboardButton("📁 ৫. সিক্রেট পার্ট ৫"), KeyboardButton("📁 ৬. সিক্রেট পার্ট ৬")],
        [KeyboardButton("📁 ৭. সিক্রেট পার্ট ৭")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 সেকশন বেছে নিয়ে ছবি বা ভিডিও পাঠাও:", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    matched_key = None
    for key in SECTION_MAP:
        if key in text:
            matched_key = key
            break

    if matched_key:
        context.user_data['selected_section'] = SECTION_MAP[matched_key]
        context.user_data['selected_name'] = matched_key
        await update.message.reply_text(f"✅ তুই **{matched_key}** সিলেক্ট করেছিস। এবার তোর ছবি বা ভিডিও পাঠা!")
    else:
        await update.message.reply_text("⚠️ নিচের মেনু থেকে কোনো সেকশন সিলেক্ট কর।")

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_section = context.user_data.get('selected_section')
    selected_name = context.user_data.get('selected_name')

    if not selected_section:
        await update.message.reply_text("⚠️ আগে নিচের মেনু থেকে কোনো সেকশন সিলেক্ট কর!")
        return

    file_id = None
    file_type = None

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_type = "image"
    elif update.message.video:
        file_id = update.message.video.file_id
        file_type = "video"

    if file_id:
        msg = await update.message.reply_text("⏳ প্রসেস হচ্ছে...")
        file_obj = await context.bot.get_file(file_id)
        direct_url = file_obj.file_path

        file_data = {'url': direct_url, 'type': file_type}
        target_url = f"{FIREBASE_URL}/{selected_section}.json"
        response = requests.post(target_url, json=file_data)

        if response.status_code == 200:
            await msg.edit_text(f"🚀 সফলভাবে **{selected_name}** সেকশনে আপলোড হয়ে গেছে!")
        else:
            await msg.edit_text("❌ আপলোড করতে সমস্যা হয়েছে!")

if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("বট ক্লাউডে চালু হয়েছে...")
    app.run_polling()
