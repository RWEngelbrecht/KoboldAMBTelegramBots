import telebot, os
from dotenv import load_dotenv

from Classes.Game import *
from Classes.Kobold import *
from Classes.Dice import Dice

load_dotenv()

token = os.getenv("TOKEN")
bot = telebot.TeleBot(token)
game = Game()
dice = Dice()

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
  /kill <kobold name> : deletes kobold
  /slap <Name>: slap someone silly
  """)


@bot.message_handler(commands=['register'])
def register_handler(message):
  try:
    parts = game.message_splitter(message.text)
    if game.kobold_exists(parts["name"]) == True:
      raise NameExists('')
    kb = Kobold(
      message.from_user.id,
      parts["name"], parts["brawn"],
      parts["ego"], parts["extraneous"],
      parts["reflexes"],
      parts["deathcheck_count"])
    game.add_kobold(kb)
    print(str(game.get_all_kobolds()))
    game.save_to_db(kb)
    bot.reply_to(message, parts["name"]+" has joined the horde of King Torg!")
  except (UnboundLocalError, ValueError) as e:
    bot.reply_to(message, """Tell me about your Kobold, like this:
    /register koboldName brawn ego extraneous reflexes deathCheckCount(optional)""")
  except NameExists:
    bot.reply_to(message, "That seems to be another Kobold's name. Be more creative!")


@bot.message_handler(commands=['load'])
def load_handler(message):
  msg = message.text.split()
  if len(msg) > 1:
    loaded_kb = game.load_kobold(message.from_user.id, msg[1])
  else:
    loaded_kb = game.load_kobold(message.from_user.id)
  try:
    if game.kobold_exists(loaded_kb['name']):
      print(f'Kobold {loaded_kb["name"]} exists in global var! ')
      game.remove_local_kobold(loaded_kb['player'],loaded_kb['name'])
    game.add_kobold(Kobold(
      loaded_kb['player'], loaded_kb['name'],
      loaded_kb['brawn'], loaded_kb['ego'],
      loaded_kb['extraneous'], loaded_kb['reflexes'],
      loaded_kb['death_check_count']))
    bot.reply_to(message, loaded_kb['name']+f' has rejoined the horde of King Torg!\nBrawn: {loaded_kb["brawn"]}')
  except (ValueError, TypeError) as e:
    print(e)
    bot.reply_to(message, "I couldn't find that Kobold!")


@bot.message_handler(commands='roll')
def roll_handler(message):
  try:
    command, attribute, difficulty = message.text.split()
    # kobold = next(filter(lambda kobold: find_my_kobold(message.from_user.id, kobolds), kobolds))
    kobold = game.find_my_kobold(message.from_user.id)
    print(f'roll_handler: kobold == {str(kobold)}')
    ans = kobold.roll(attribute, int(difficulty))
    bot.reply_to(message, f'{str(ans)}')
  except ValueError as e:
    print(f'roll_handler err: {e}')
    try:
      command, difficulty = message.text.split()
      ans = dice.roll(int(difficulty))
      bot.reply_to(message, f'You rolled {str(ans[:-1])}\nTotal: {ans[-1]}')
    except ValueError:
      bot.reply_to(message, "At least tell me how many times to roll...")
  except (StopIteration, Exception) as e:
    bot.reply_to(message, "Something went horribly wrong! Ask your friendly neighbourhood dev about it...")
    print(str(message.from_user.username)+"said: "+message.text)
    print(e)


# TODO: remove character specification, user must use /load to switch characters
@bot.message_handler(commands='deathcheck')
def deathcheck_handler(message):
  try:
    command, character = message.text.split()
    kobold = game.find_my_kobold(message.from_user.id, character)
    bot.reply_to(message, kobold.deathcheck())
    game.update_kobold(message.from_user.id, kobold, character)
  except ValueError:
    print(f'deathcheck: no character specified')
    try:
      kobold = game.find_my_kobold(message.from_user.id)
      bot.reply_to(message, kobold.deathcheck())
      game.update_kobold(message.from_user.id, kobold)
    except AttributeError:
      bot.reply_to(message, "Silly Kobold! You need to /register to King Torg's army first...")
  except (StopIteration, UnboundLocalError) as e:
    bot.reply_to(message, "Silly Kobold! You need to /register that specific Kobold to King Torg's army first...")


@bot.message_handler(commands='kill')
def delete_handler(message):
  try:
    command, kobold = message.text.split()
    game.delete_kobold(message.from_user.id, kobold)
    bot.reply_to(message, f'{kobold} has been violently made to stop living. Its hopes and dreams die with it.')
  except ValueError:
    bot.reply_to(message, "You need to tell me who to kill.")


@bot.message_handler(commands='list')
def list_handler(msg):
  try:
    my_kobs = game.get_my_kobolds(msg.from_user.id)
    bot.reply_to(msg, f'Your kobolds:\n{my_kobs}')
  except Exception as e:
    print(e)
    bot.reply_to(msg, "You have no Kobolds!")


# @bot.message_handler(commands='slap')
# def slap_handler(message):
#   bot.
#   pass



bot.polling(none_stop=True, timeout=30)