from scipy import signal
from numpy.fft import rfft, rfftfreq, fft
import numpy as np
from scipy.signal import butter, find_peaks

"""" Объявляем константы """
fsB = 250  # частота дисретизации БРЛ
lowcut_hb = 0.7
highcut_hb = 2.5
lowcut_br = 0.01
highcut_br = 0.4


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs  # приведение к удобному формату ввода частоты среза
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def fourier_analysis(signal1, signal2, fs, freq_low, freq_high):
    sum_signal = []
    for i in range(0, min(len(signal1), len(signal2))):  # собираем общий сигнал из двух квадратур
        sum_signal.append(complex(signal1[i], signal2[i]))

    fsignal = fft(sum_signal)  # используем преобразование Фурье
    fsignal = np.abs(fsignal)  # только положительную часть спектра
    time_step = 1 / fs
    freqs = np.fft.fftfreq(len(sum_signal), time_step)  # находим частоты составляющих спектра
    freqs = np.abs(freqs)
    freq_low = min(freqs, key=lambda x: abs(x - freq_low))  # находим в массиве частот ближайшие
    freq_high = min(freqs, key=lambda x: abs(x - freq_high))  # к частотам среза
    freq_low_ind = np.where(freqs == freq_low)[0][0]
    freq_high_ind = np.where(freqs == freq_high)[0][0]
    fsignal_max = max(fsignal[freq_low_ind:freq_high_ind])  # находим максимальную составляющую частоты
    freq_max_ind = np.where(fsignal == fsignal_max)
    freq_max = freqs[freq_max_ind]
    return freq_max[0]


def find_bigger_signal(signal1, signal2, signal3, signal4):
    mean1 = 0
    mean2 = 0
    mean3 = 0
    mean4 = 0
    for i in range(0, len(signal1)):
        mean1 += abs(signal1[i])
        mean2 += abs(signal2[i])
        mean3 += abs(signal3[i])
        mean4 += abs(signal4[i])
    mean1 /= len(signal1)
    mean2 /= len(signal2)
    mean3 /= len(signal3)
    mean4 /= len(signal4)
    max_mean = max(mean1, mean2, mean3, mean4)
    if mean1 == max_mean:
        return 0
    elif mean2 == max_mean:
        return 0
    elif mean3 == max_mean:
        return 1
    elif mean4 == max_mean:
        return 1


def breath_filter(signal1, signal2, signal3, signal4):
    order = 2
    global lowcut_br
    global highcut_br

    freq_br_r1 = fourier_analysis(signal1, signal2, fsB, lowcut_br, highcut_br)
    freq_br_r2 = fourier_analysis(signal3, signal4, fsB, lowcut_br, highcut_br)
    '''Находим сигнал с большей амплитудой'''
    who = find_bigger_signal(signal1, signal2, signal3, signal4)
    if who == 0:
        freq_sum = freq_br_r1
    elif who == 1:
        freq_sum = freq_br_r2
    lowcut_br = freq_sum - 0.1
    highcut_br = freq_sum + 0.1
    if (freq_sum - 0.1) <= 0:
        lowcut_br = 0.01

    B_br, A_br = butter_bandpass(lowcut_br, highcut_br, fsB, order=order)

    signalfilt_r1_1 = signal.filtfilt(B_br, A_br, signal1)
    signalfilt_r1_2 = signal.filtfilt(B_br, A_br, signal2)
    signalfilt_r2_1 = signal.filtfilt(B_br, A_br, signal3)
    signalfilt_r2_2 = signal.filtfilt(B_br, A_br, signal4)
    return signalfilt_r1_1, signalfilt_r1_2, signalfilt_r2_1, signalfilt_r2_2


def signal_without_breath(sig1, sig2):
    sig_res = []
    for i in range(0, min(len(sig1), len(sig2))):
        sig_res = np.append(sig_res, sig1[i] - sig2[i])
    return sig_res


def heart_filter(signal_r1_1, signal_r1_2, signal_r2_1, signal_r2_2):
    """фильтрация по широкой полосе"""
    order = 3
    global lowcut_hb
    global highcut_hb

    B_hb_w, A_hb_w = butter_bandpass(lowcut_hb, highcut_hb, fsB, order=order)
    signalfilt_hb_r1_1_w = signal.filtfilt(B_hb_w, A_hb_w, signal_r1_1)
    signalfilt_hb_r1_2_w = signal.filtfilt(B_hb_w, A_hb_w, signal_r1_2)
    signalfilt_hb_r2_1_w = signal.filtfilt(B_hb_w, A_hb_w, signal_r2_1)
    signalfilt_hb_r2_2_w = signal.filtfilt(B_hb_w, A_hb_w, signal_r2_2)

    freq_hb_r1 = fourier_analysis(signal_r1_1, signal_r1_2, fsB, lowcut_hb, highcut_hb)
    freq_hb_r2 = fourier_analysis(signal_r2_1, signal_r2_2, fsB, lowcut_hb, highcut_hb)
    freq_sum = np.mean([freq_hb_r1, freq_hb_r2])

    lowcut_hb = freq_sum - 0.3
    if lowcut_hb < 0:
        lowcut_hb = 0.7
    highcut_hb = freq_sum + 0.4

    B_hb, A_hb = butter_bandpass(lowcut_hb, highcut_hb, fsB, order=order)
    signalfilt_hb_r1_1 = signal.filtfilt(B_hb, A_hb, signal_r1_1)
    signalfilt_hb_r1_2 = signal.filtfilt(B_hb, A_hb, signal_r1_2)
    signalfilt_hb_r2_1 = signal.filtfilt(B_hb, A_hb, signal_r2_1)
    signalfilt_hb_r2_2 = signal.filtfilt(B_hb, A_hb, signal_r2_2)

    return (signalfilt_hb_r1_1, signalfilt_hb_r1_2, signalfilt_hb_r2_1, signalfilt_hb_r2_2,
            signalfilt_hb_r1_1_w, signalfilt_hb_r1_2_w, signalfilt_hb_r2_1_w, signalfilt_hb_r2_2_w)


def breath_rate_counter(signal_r1_1, signal_r1_2, signal_r2_1, signal_r2_2, time):
    """
    Предварительная обработка данных
    """
    signal_r1_1 = signal.detrend(signal_r1_1)  # удаляем тренд средней линии
    signal_r1_2 = signal.detrend(signal_r1_2)
    signal_r2_1 = signal.detrend(signal_r2_1)
    signal_r2_2 = signal.detrend(signal_r2_2)
    signalfilt_br_r1_1, signalfilt_br_r1_2, signalfilt_br_r2_1, \
    signalfilt_br_r2_2 = breath_filter(signal_r1_1, signal_r1_2, signal_r2_1, signal_r2_2)

    signalfilt_hb_r1_1 = signal_without_breath(signal_r1_1, signalfilt_br_r1_1)
    signalfilt_hb_r1_2 = signal_without_breath(signal_r1_2, signalfilt_br_r1_2)
    signalfilt_hb_r2_1 = signal_without_breath(signal_r2_1, signalfilt_br_r2_1)
    signalfilt_hb_r2_2 = signal_without_breath(signal_r2_2, signalfilt_br_r2_2)

    signalfilt_hb_r1_1, signalfilt_hb_r1_2, signalfilt_hb_r2_1, signalfilt_hb_r2_2, \
    signalfilt_hb_r1_1_w, signalfilt_hb_r1_2_w, signalfilt_hb_r2_1_w, signalfilt_hb_r2_2_w \
        = heart_filter(signalfilt_hb_r1_1, signalfilt_hb_r1_2, signalfilt_hb_r2_1, signalfilt_hb_r2_2)

    '''Поиск пиков'''
    # peaks_hb_r1_1_w = find_peaks(signalfilt_hb_r1_1_w, distance=fsB / highcut_hb)[0]
    # peaks_hb_r1_2_w = find_peaks(signalfilt_hb_r1_2_w, distance=fsB / highcut_hb)[0]
    # peaks_hb_r2_1_w = find_peaks(signalfilt_hb_r2_1_w, distance=fsB / highcut_hb)[0]
    # peaks_hb_r2_2_w = find_peaks(signalfilt_hb_r2_2_w, distance=fsB / highcut_hb)[0]

    peaks_hb_r1_1 = find_peaks(signalfilt_hb_r1_1, distance=fsB / highcut_hb)[0]
    peaks_hb_r1_2 = find_peaks(signalfilt_hb_r1_2, distance=fsB / highcut_hb)[0]
    peaks_hb_r2_1 = find_peaks(signalfilt_hb_r2_1, distance=fsB / highcut_hb)[0]
    peaks_hb_r2_2 = find_peaks(signalfilt_hb_r2_2, distance=fsB / highcut_hb)[0]

    peaks_br_r1_1 = find_peaks(signalfilt_br_r1_1, distance=fsB / highcut_br)[0]
    peaks_br_r1_2 = find_peaks(signalfilt_br_r1_2, distance=fsB / highcut_br)[0]
    peaks_br_r2_1 = find_peaks(signalfilt_br_r2_1, distance=fsB / highcut_br)[0]
    peaks_br_r2_2 = find_peaks(signalfilt_br_r2_2, distance=fsB / highcut_br)[0]

    total_breath_rate = (len(peaks_br_r1_1) + len(peaks_br_r1_2) + len(peaks_br_r2_1) + len(peaks_br_r2_2)) / 4
    total_breath_rate = total_breath_rate / time * 60

    total_heart_rate = (len(peaks_hb_r1_1) + len(peaks_hb_r1_2) + len(peaks_hb_r2_1) + len(peaks_hb_r2_2)) / 4
    total_heart_rate = total_heart_rate / time * 60

    return total_heart_rate, total_breath_rate
