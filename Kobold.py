from Dice import Dice

class NameExists(Exception):
  '''Raised when Kobold's name exists'''
  pass

class Kobold:
  def __init__(self, player, name, brawn, ego, extraneous, reflexes, death_check_count=0):
    self.player = player
    self.name = name
    self.brawn = brawn
    self.ego = ego
    self.extraneous = extraneous
    self.reflexes = reflexes
    self.death_checks_count = death_check_count
    self.dice = Dice()

  def deathcheck(self):
    self.death_checks_count += 1
    rolls = self.dice.roll(2)
    total = self.death_checks_count + rolls[-1]
    check_str = f'Kobold:\t\t{self.name}\nDeath Check Count:\t{str(self.death_checks_count)}\n{str(rolls[:-1])} + {str(self.death_checks_count)} = {str(total)}'
    if total >= 13: check_str += "\n"+self.name+" died horribly"
    return check_str
    # print(str(rolls[:-1])+" + "+" = "+str(rolls[-1]))