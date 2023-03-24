import matplotlib.pyplot as plt


with open('./results.txt') as f:
    lines = f.read().splitlines()

print(lines)

ratio = []
wins = 0
loses = 0

for game in lines:
    if game == "Result.Defeat":
        loses += 1
    elif game == "Result.Victory":
        wins += 1
    ratio.append(wins/(wins+loses))

plt.plot(ratio)

plt.xlabel('Games played')
plt.ylabel('Win/loss ratio')
plt.title('Bot win/loss ratio during training')

plt.show()