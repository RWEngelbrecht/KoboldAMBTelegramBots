import telebot, os
from dotenv import load_dotenv
from pymongo import MongoClient

from Classes.Kobold import *
from Classes.Dice import Dice

load_dotenv()


token = os.getenv("TOKEN")
client = MongoClient(os.getenv("MDB_CON_CTR"))
db = client.kobold
col = db.kobolds

bot = telebot.TeleBot(token)

kobolds = []

def kobold_exists(kobold_name):
  for kobold in kobolds:
    if kobold.name == kobold_name:
      return True


def find_my_kobold(from_user, kobold_name=""):
  if len(kobold_name) > 0:
    for kobold in kobolds:
      if kobold.player == from_user and kobold.name == kobold_name:
        return kobold
  else:
    for kobold in kobolds:
      if kobold.player == from_user:
        return kobold


def remove_local_kobold(from_user, kobold_name):
  del kobolds[kobolds.index(find_my_kobold(from_user, kobold_name))]


def save_to_db(kobold):
  col.insert_one(kobold.get_info())


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


@bot.message_handler(commands=['start'])
def handle_start(message):
  bot.send_message(message.chat.id, "Hey you dirty Kobolds, I'll manage your life for you.")

@bot.message_handler(commands=['help'])
def handle_help(message):
  bot.send_message(message.chat.id, """
  Commands:
  /help : Guess you know what this does, since you're looking at it.
  /register <name brawn ego extraneous reflexes [deathcheck count (optional)]>: register new Kobold
  /load <[kobold name (optional)]> loads your kobold from the databas
  /roll <attribute> <difficulty>: rolls <difficulty>d6 and compares to your attribute
  /deathcheck : rolls 2d6 + kobold horrible death record
  /add_skills <skills> : adds skills to profile
  /add_edges <edges> : adds edges to profile
  /add_bogies <bogies> : adds bogies to profile
  /delete_kobold <kobold name> : deletes kobold
  /slap <Name>: slap someone silly
  """)

@bot.message_handler(commands=['register'])
def register_handler(message):
  try:
    parts = message_splitter(message.text)
    if kobold_exists(parts["name"]) == True:
      raise NameExists('')
    kb = Kobold(
      message.from_user.username,
      parts["name"], parts["brawn"],
      parts["ego"], parts["extraneous"],
      parts["reflexes"],
      parts["deathcheck_count"])
    kobolds.insert(0, kb)
    save_to_db(kb)
    bot.reply_to(message, parts["name"]+" has joined the horde of King Torg!")
  except (UnboundLocalError, ValueError) as e:
    bot.reply_to(message, """Tell me about your Kobold, like this:
    /register koboldName brawn ego extraneous reflexes deathCheckCount(optional)""")
  except NameExists:
    bot.reply_to(message, "That seems to be another Kobold's name. Be more creative!")


@bot.message_handler(commands=['load'])
def load_handler(message):
  msg = message.text.split()
  if (len(msg) > 1):
    loaded_kb = col.find_one({"player": message.from_user.username, "name": msg[1]})
  else:
    loaded_kb = col.find_one({"player": message.from_user.username})
  try:
    if (kobold_exists(loaded_kb['name'])):
      remove_local_kobold(loaded_kb['player'],loaded_kb['name'])
    kobolds.insert(0, Kobold(
      loaded_kb['player'], loaded_kb['name'],
      loaded_kb['brawn'], loaded_kb['ego'],
      loaded_kb['extraneous'], loaded_kb['reflexes'],
      loaded_kb['death_check_count']))
    bot.reply_to(message, loaded_kb['name']+" has rejoined the horde of King Torg!")
  except (ValueError, TypeError) as e:
    bot.reply_to(message, "I couldn't find that Kobold!")


@bot.message_handler(commands='roll')
def roll_handler(message):
  try:
    command, attribute, difficulty = message.text.split()
    kobold = next(filter(lambda kobold: find_my_kobold(message.from_user.username), kobolds))
    bot.reply_to(message, kobold.roll(attribute, int(difficulty)))
  except ValueError:
    bot.reply_to(message, "I don't understand! Try again... Maybe read the instructions?")

# TODO: remove character specification, user must use /load to switch characters
@bot.message_handler(commands='deathcheck')
def deathcheck_handler(message):
  try:
    command, character = message.text.split()
    my_kobolds = filter(lambda kobold: find_my_kobold(message.from_user.username, character), kobolds)
    for kobo in my_kobolds:
      if kobo.name == character:
        kobold = kobo
        break
    bot.reply_to(message, kobold.deathcheck())
    col.update_one(
      {"player": kobold.player, "name": kobold.name},
      {"$set": {"death_check_count": kobold.death_checks_count}}
      )
  except ValueError:
    try:
      kobold = next(filter(lambda kobold: find_my_kobold(message.from_user.username), kobolds))
      bot.reply_to(message, kobold.deathcheck())
      col.update_one(
        {"player": kobold.player, "name": kobold.name},
        {"$set": {"death_check_count": kobold.death_checks_count}}
        )
    except StopIteration:
      bot.reply_to(message, "Silly Kobold! You need to /register to King Torg's army first...")
  except (StopIteration, UnboundLocalError) as e:
    bot.reply_to(message, "Silly Kobold! You need to /register that specific Kobold to King Torg's army first...")


# @bot.message_handler(commands='slap')
# def slap_handler(message):
#   bot.
#   pass

bot.polling()