import os
from pymongo import MongoClient
from dotenv import load_dotenv

class Game:

  load_dotenv()

  def __init__(self):
    self.kobolds = []
    self.client = MongoClient(os.getenv("MDB_CON_CTR"))
    self.db = self.client.kobold
    self.col = self.db.kobolds


  def kobold_exists(self, kobold_name):
    for kobold in self.kobolds:
      if kobold.name == kobold_name:
        return True


  def find_my_kobold(self, player_id, kobold_name=""):
    if len(kobold_name) > 0:
      for kobold in self.kobolds:
        if kobold.player == player_id and kobold.name == kobold_name:
          print("found "+kobold.name+" for "+str(player_id))
          return kobold
    else:
      for kobold in self.kobolds:
        if kobold.player == player_id:
          print("found "+kobold.name+" for "+str(player_id))
          return kobold


  def add_kobold(self, kobold):
    self.kobolds.insert(0, kobold)


  def remove_local_kobold(self, from_user, kobold_name):
    del self.kobolds[self.kobolds.index(self.find_my_kobold(from_user, kobold_name))]
    print("kobolds left after remove_local: "+str(self.kobolds))


  def save_to_db(self, kobold):
    self.col.insert_one(kobold.get_info())


  def load_kobold(self, player_id, kobold_name=""):
    if len(kobold_name) > 0:
      return self.col.find_one({"player": player_id, "name": kobold_name})
    return self.col.find_one({"player": player_id})


  def update_kobold(self, player_id, kobold):
    self.col.update_one(
      {"player": player_id, "name": kobold.name},
      {"$set": {"death_check_count": kobold.death_checks_count}}
    )
    self.remove_local_kobold(player_id, kobold.name)
    self.add_kobold(kobold)


  def delete_kobold(self, player_id, kobold_name):
    self.col.delete_one(
      {"player": player_id, "name": kobold_name}
      )


  def message_splitter(self, message):
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


  def get_all_kobolds(self):
    return self.kobolds

  def get_my_kobolds(self, player_id):
    return list(self.col.find({"player": player_id}))