import telebot
import requests

BOT_TOKEN = 'YOUR_BOT_TOKEN'  # 🔐 Replace with your bot token
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "👋 Hello! I'm ChatGPT (via SafoneAPI).\n\n"
        "💬 Just send a message and I'll reply smartly.\n"
        "⚡ No memory, no tracking — lightning-fast replies!"
    )

@bot.message_handler(func=lambda msg: True)
def chat_reply(message):
    user_msg = message.text.strip()
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        response = requests.post(
            "https://api.safone.co/chatgpt",
            headers={
                "accept": "application/json",
                "Content-Type": "application/json"
            },
            json={
                "message": user_msg,
                "version": 3,
                "chat_mode": "assistant",
                "dialog_messages": [{"bot": "", "user": ""}]
            }
        )
        reply = response.json().get("message", "⚠️ No response.")
    except Exception as e:
        reply = f"❌ Error: {e}"

    bot.send_message(message.chat.id, reply)

bot.polling(non_stop=True)