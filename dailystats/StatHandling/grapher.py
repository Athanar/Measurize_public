import matplotlib.pyplot as plt 
import numpy as np
import datetime




def plotData(input_list, goal_list, date_list, source):
    f = plt.figure()
    ax = f.add_subplot(111)
    ax.clear()
    ax.plot(date_list, input_list,'b-', label="Results")
    ax.plot(date_list, goal_list, 'r', label="Goals")
    f.autofmt_xdate()
    plt.ylabel("Score")
    plt.ylim(bottom=0)
    plt.legend()
    f.savefig('dailystats/static/' + source)