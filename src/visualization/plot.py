import csv
import matplotlib.pyplot as plt

with open('../../output/002_11011000010000111110101111100011.txt', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    i = 0
    
    for row in reader:  
        positions = [row[i:i + 2] for i in range(0, len(row) -1, 2)]

        x_values = [float(position[0]) for position in positions]
        y_values = [float(position[1]) for position in positions]
        plt.scatter(x_values, y_values)
        plt.savefig('002_11011000010000111110101111100011_' + str(i) + '.png')
        plt.clf()
        i = i + 1

