import matplotlib.pyplot as plt

##plotting precomputed values

x = [10, 20, 30]
data = [20, 14, 6]
#ax = figure.add_subplot(111)
plt.plot(x, data, 'r-')
plt.xlabel('size of warfield')
plt.ylabel('number of times goal reached')
plt.show()
#plt.set_title('No.of times goal state achieved')
