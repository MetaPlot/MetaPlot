
import metaplot as mp
import matplotlib.pyplot as plt


mp.mplintercept.start()

plt.plot([1,2,3], [1,2,3], 'ro-')
plt.plot([4,5,6], [4,5,6], color='k', linestyle='dashed')
plt.xlabel('custom xlabel')
plt.ylabel('custom ylabel')

mp.mplintercept.save('test_interactive.out')



mp.mplintercept.show('test_interactive.out')