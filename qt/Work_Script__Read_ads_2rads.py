
import serial
from   struct            import unpack
import numpy             as     np
import time
import sys
#=====================================================
# PARAMETERS:

dt_ms = 4       # period between samples (Timer value which must be > 2*conversion_delay+2ms)

sF = round(1/(dt_ms * 0.001 ))

T_mins = 1      # define duration of the file record in [minutes]

recDuration = 12 # define duration of the whole record in [hours]

   
#=====================================================
# Initialize Serial connection:   
ser1 = serial.Serial("COM4", baudrate=34800)
ser2 = serial.Serial("COM5", baudrate=34800)

time.sleep(2)

file_name = str(input("Name of file without extension: "))


# SEND the Start command:
num_bytes   = ser1.write(b'5') # char, 1 byte # '5' was chosen arbitrarily
num_bytes   = ser2.write(b'5') # char, 1 byte # '5' was chosen arbitrarily

#=====================================================
# READ data from Arduino:
print("Start ==============")

file_number = 0
max_file_num = 1
#max_file_num = round(recDuration*60/T_mins); 


# Try read:
try:
    
    while file_number < max_file_num: # добавить подсчет необходимого количества файлов исходя из требуемой продолжительности
        file_number = file_number + 1
        # print ('file_number = ', file_number)
        # time.sleep(2)
        # Empty lists:    
        a_ch0       = []
        a_ch1       = []
        a_ch20       = []
        a_ch21       = []
        Time_meas   = []
        T_ms        = 0
        file_duration_in_s = 90
        T_ms_limit  = round(T_mins * file_duration_in_s  * sF * dt_ms) # duration of a single file in samples

        while T_ms < T_ms_limit:
            # Get the binary data, convert to decimal and [mV]:
            a0_mV  = (unpack('<H' , ser1.read(2))[0])  # ads voltage = 2 bytes
            a1_mV  = (unpack('<H' , ser1.read(2))[0]) 
            
            a20_mV  = (unpack('<H' , ser2.read(2))[0])  # ads voltage = 2 bytes
            a21_mV  = (unpack('<H' , ser2.read(2))[0]) 
    
            # Add new values to lists:
            a_ch0.append(a0_mV)
            a_ch1.append(a1_mV)
            a_ch20.append(a20_mV)
            a_ch21.append(a21_mV)
            
    
            T_ms += dt_ms            # increment time
            Time_meas.append(T_ms)
            
            # Print conversion results:
            print("Arduino says: ch_0 ", a0_mV, "mV")   
            print("Arduino says: ch_1 ", a1_mV, "mV\n\n")
            print('time = ', T_ms)
        # Stop when time is up:
        #ser.write(b'0')              # Send the Stop command to Arduino
        #ser.close()                  # Break the Serial connection
        print("\n==========================================================\n")
        print("Stop command sent\n")  
        np.savez_compressed(file_name +'_Rad1_' + str(file_number) , ch0=a_ch0, ch1=a_ch1, T=Time_meas)
        np.savez_compressed(file_name +'_Rad2_' + str(file_number) , ch0=a_ch20, ch1=a_ch21, T=Time_meas)
# If interrupted from keyboard:
except KeyboardInterrupt:        # Ctrl+C
    ser1.write(b'0')              # Send the Stop command to Arduino
    ser1.close()                  # Break the Serial connection 
    ser2.write(b'0')
    ser2.close()
    print("\n==========================================================\n")
    print("Stop command sent\n")
    sys.exit()
    
finally:
    # In any case, write data to a file:
    np.savez_compressed(file_name +'_Rad1_' + str(file_number) , ch0=a_ch0, ch1=a_ch1, T=Time_meas)
    np.savez_compressed(file_name +'_Rad2_' + str(file_number) , ch0=a_ch20, ch1=a_ch21, T=Time_meas)
    ser1.write(b'0')              # Send the Stop command to Arduino
    ser1.close()                  # Break the Serial connection
    ser2.write(b'0')
    ser2.close()

    



