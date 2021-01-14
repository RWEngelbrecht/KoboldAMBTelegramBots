import telebot

token = "1527405068:AAFX_STJtIMptJmZl3_RvqxbdDyTK9QKZa4"

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Hey you dirty Kobolds, you ready to hail the King?")

@bot.message_handler(regexp=r'(?i)(.*king torg.*)|(.*torg.*)')
def handle_message(message):
    bot.reply_to(message, "All hail King Torg!")


bot.polling()
