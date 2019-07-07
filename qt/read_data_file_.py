
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio

plt.close("all")

timeSeria = 1# запись состоит из фрагментов по 1 минуты, записанных  в течение 3х минут
#filename = 'fall_toR'
#filename = 'noFalls'
#filename = 'fall_serg_toR'
#filename = 'breath_1'
#filename = 'breath_2apnea'
#filename = 'test_lying2'

filename = 'Efremova_f'
#filename = 'moving'

for fileInd in range(1,timeSeria+1):
    # Load from numpy_savez_compressed file:
    npzfile_1     = np.load(filename + '_Rad1_' + str(fileInd) + '.npz')
    rad1_T_s      = npzfile_1["T"]
    rad1_Ch0      = npzfile_1["ch0"]
    rad1_Ch1      = npzfile_1["ch1"]
    rad1_Ch1 [0]=rad1_Ch1 [1]
    rad1_Ch0 [0]=rad1_Ch0 [1]
    sio.savemat(filename + '_Rad1_' + str(fileInd) + '.mat', mdict=npzfile_1)
    
    
    npzfile_2     = np.load(filename + '_Rad2_' + str(fileInd) + '.npz')
    rad2_T_s      = npzfile_2["T"]
    rad2_Ch0      = npzfile_2["ch0"]
    rad2_Ch1      = npzfile_2["ch1"]
    rad2_Ch1 [0]=rad2_Ch1 [1]
    rad2_Ch0 [0]=rad2_Ch0 [1]
    sio.savemat(filename + '_Rad2_' + str(fileInd) + '.mat', mdict=npzfile_2)
    

# Convert to [V] and [s], if needed:
rad1_T_s    = rad1_T_s/1000  # 1000   [ms] > [s]
rad1_Ch0    = rad1_Ch0/8000  # 8 conversion coeff
rad1_Ch1    = rad1_Ch1/8000  # 1000   [mV] > [V]

rad2_T_s    = rad2_T_s/1000
rad2_Ch0    = rad2_Ch0/8000
rad2_Ch1    = rad2_Ch1/8000



# Equidistant time for plotting:
T_ms = np.arange(0, len(rad1_Ch0)*4, 4)
T_s  = T_ms/1000



# PLOT:
fig = plt.figure(1)
ax = fig.add_subplot(1, 1, 1)
ax.plot(T_s, rad1_Ch0,'g', markersize=10.0, label="Ch_0")
ax.plot(T_s, rad1_Ch1,'r', markersize=10.0, label="Ch_1")
ax.set_xticks(np.arange(0, 15, 0.2))
ax.legend(loc='best')   #'best'/'upper right'
plt.xlabel('Time, s')
plt.ylabel('Voltage, V')
plt.title('Rad1 meas results')
plt.grid()


fig = plt.figure(num=None, figsize=(25, 10), dpi=80, facecolor='w', edgecolor='k')

ax = fig.add_subplot(1, 1, 1)
ax.plot(T_s, rad2_Ch0,'g', markersize=10.0, label="Ch_0")
ax.plot(T_s, rad2_Ch1,'r', markersize=10.0, label="Ch_1")
ax.set_xticks(np.arange(0, 20, 0.3))
ax.legend(loc='best')   #'best'/'upper right'
plt.xlabel('Time, s')
plt.ylabel('Voltage, V')
plt.title('Rad2 meas results')
plt.grid()


plt.plot()
