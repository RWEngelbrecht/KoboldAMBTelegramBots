import random

class Dice:
  # returns [<roll 1>, <roll 2>, ..., <total>]
  # #
  def roll(self, amnt):
    rolls = random.choices(range(1,7), k=amnt)
    total = sum(int(roll) for roll in rolls)
    rolls.append(total)
    return rolls