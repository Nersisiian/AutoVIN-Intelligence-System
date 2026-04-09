import os
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

API_BASE = os.getenv("API_BASE", "http://backend:8000")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a VIN (17 characters) to decode.")

async def handle_vin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vin = update.message.text.strip().upper()
    if len(vin) != 17:
        await update.message.reply_text("Invalid VIN. Must be 17 characters.")
        return
    await update.message.reply_text("Decoding VIN...")
    async with aiohttp.ClientSession() as session:
        # Decode
        async with session.post(f"{API_BASE}/decode-vin?vin={vin}") as resp:
            decode_data = await resp.json()
        # ML prediction
        async with session.post(f"{API_BASE}/predict-specs?vin={vin}") as resp:
            ml_data = await resp.json()
        # Auction data
        async with session.get(f"{API_BASE}/auction-data?vin={vin}") as resp:
            auction_data = await resp.json()
    
    message = f"*VIN:* {vin}\n"
    message += f"*Decoded:* {decode_data.get('make', 'N/A')} {decode_data.get('model', '')} ({decode_data.get('year', '')})\n"
    message += f"*ML Predicted:* Trim: {ml_data.get('trim')}, Engine: {ml_data.get('engine')}, Trans: {ml_data.get('transmission')}\n"
    message += f"*Auction:* Copart: {auction_data.get('copart')}, IAAI: {auction_data.get('iaai')}"
    await update.message.reply_text(message, parse_mode='Markdown')

def main():
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_vin))
    app.run_polling()

if __name__ == "__main__":
    main()