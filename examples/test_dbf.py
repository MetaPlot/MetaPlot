
import metaplot as mp
import matplotlib.pyplot as plt

mp.mplintercept.start()
plt.plot([1,2,3,4,5], [6,7,8,9,10], color='k', linestyle='dashed')
mp.mplintercept.write_data_table(filename='send_to_journal.ecsv')