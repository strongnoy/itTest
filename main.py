import telebot
api = '7008780571:AAH3BlCFSYbDwxibIGmdXcMM0Oqq7klunEE'
bot = telebot.TeleBot(api)

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, "прив, я эхо бот")

@bot.message_handler(content_types=['text'])
def echo(message):
    bot.reply_to(message, message.text)
bot.polling(none_stop=True, interval=0)
