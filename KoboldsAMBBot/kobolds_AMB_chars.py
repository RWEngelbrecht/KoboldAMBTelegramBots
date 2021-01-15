import telebot, os
from Classes.Kobold import *
from Classes.Dice import Dice
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("TOKEN")

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
  /slap <Name>: slap someone silly
  """)

kobolds = []

def kobold_exists(kobold_name):
  for kobold in kobolds:
    if kobold.name == kobold_name:
      return True


def find_my_kobold(kobolds, message, kobold_name=""):
  for kobold in kobolds:
    if kobold.player == message.from_user.username:
      return kobold


def message_splitter(message):
  try:
    pieces = message.split()
    if len(pieces) == 7:
      command, name, brawn, ego, extraneous, reflexes, deathcheck_count = pieces
      parts = {
        "command": command, "name": name, "brawn": int(brawn),
        "ego": int(ego), "extraneous": int(extraneous), "reflexes": int(reflexes),
        "deathcheck_count": int(deathcheck_count)
      }
    elif len(pieces) == 6:
      command, name, brawn, ego, extraneous, reflexes = pieces
      parts = {
        "command": command, "name": name, "brawn": int(brawn),
        "ego": int(ego), "extraneous": int(extraneous), "reflexes": int(reflexes),
        "deathcheck_count": 0
      }
  except ValueError:
    raise ValueError
  return parts


@bot.message_handler(commands=['register'])
def register_handler(message):
  try:
    parts = message_splitter(message.text)
    if kobold_exists(parts["name"]) == True:
      raise NameExists('')
    kobolds.insert(0, Kobold(
      message.from_user.username,
      parts["name"], parts["brawn"],
      parts["ego"], parts["extraneous"],
      parts["reflexes"],
      parts["deathcheck_count"]))
    bot.reply_to(message, parts["name"]+" has joined the horde of King Torg!")
  except (UnboundLocalError, ValueError) as e:
    bot.reply_to(message, """Tell me about your Kobold, like this:
    /register koboldName brawn ego extraneous reflexes deathCheckCount(optional)""")
  except NameExists:
    bot.reply_to(message, "That seems to be another Kobold's name. Be more creative!")


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
  except (StopIteration, UnboundLocalError) as e:
    bot.reply_to(message, "Silly Kobold! You need to /register that specific Kobold to King Torg's army first...")




bot.polling()