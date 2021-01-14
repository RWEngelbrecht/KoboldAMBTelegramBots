# Dice.roll():
#
#  #

import random

class Dice:
  def roll(self, amnt):
    rolls = random.sample(range(1,7), amnt)
    total = sum(int(roll) for roll in rolls)
    rolls.append(total)
    return rolls