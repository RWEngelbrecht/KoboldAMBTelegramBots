import telebot
from Kobold import Kobold
from Dice import Dice

token = "1428539920:AAFINAejO2y8GzGihZ7VyPLKp7blFkjQUZg"

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def handle_start(message):
  bot.send_message(message.chat.id, "Hey you dirty Kobolds, I'll manage your life for you.")

@bot.message_handler(commands=['help'])
def handle_help(message):
  bot.send_message(message.chat.id, """
  Commands:
  /help : Guess you know what this does, since you're looking at it.
  /register <name brawn ego extraneous reflexes [deathcheck count (optional)]>: register new Kobold
  /roll <attribute> <difficulty>: rolls <difficulty>d6 and compares to your attribute
  /deathcheck : rolls 2d6 + kobold horrible death record
  /add_skills <skills> : adds skills to profile
  /add_edges <edges> : adds edges to profile
  /add_bogies <bogies> : adds bogies to profile
  /delete_kobold <kobold name> : deletes kobold
  """)

kobolds = []

@bot.message_handler(commands=['register'])
def register_handler(message):
  try:
    command, name, brawn, ego, extraneous, reflexes = message.text.split()
    kobolds.insert(0, Kobold(
      message.from_user.username,
      name, brawn, ego, extraneous, reflexes))
    bot.reply_to(message, name+" has joined the horde of King Torg!")
  except ValueError:
    bot.reply_to(message, """Tell me about your Kobold, like this:
    /register koboldName brawn ego extraneous reflexes deathCheckCount(optional)""")

def find_my_kobold(kobolds, message, kobold_name=""):
  for kobold in kobolds:
    if kobold.player == message.from_user.username:
      return kobold

@bot.message_handler(commands='deathcheck')
def deathcheck_handler(message):
  try:
    command, character = message.text.split()
    my_kobolds = filter(lambda kobold: find_my_kobold(kobolds, message, character), kobolds)
    for kobo in my_kobolds:
      if kobo.name == character:
        kobold = kobo
        break
    bot.reply_to(message, kobold.deathcheck())
  except ValueError:
    try:
      kobold = next(filter(lambda kobold: find_my_kobold(kobolds, message), kobolds))
      bot.reply_to(message, kobold.deathcheck())
    except StopIteration:
      bot.reply_to(message, "Silly Kobold! You need to /register to King Torg's army first...")
      return
  except StopIteration:
    bot.reply_to(message, "Silly Kobold! You need to /register that specific Kobold to King Torg's army first...")
    return




bot.polling()