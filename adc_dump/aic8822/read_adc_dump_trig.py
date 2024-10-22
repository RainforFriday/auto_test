import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.fft import fft, fftshift

# Clear variables
# No direct equivalent in Python, variables are scoped


def dump_log_plot(log_file):
    fpga_dump = 0
    dac150_dump = 0
    phy_dump = 0
    fc = 5210
    host = 1
    
    if dac150_dump == 1:
        Fs = fc / 16
    elif fpga_dump == 1 or phy_dump == 1:
        Fs = 80  # 80MHz
    else:
        if fc > 5000:
            Fs = fc / 63.75
        else:
            Fs = fc / 29.375
    
    Xlabel_unit = 1  # 1:us 0:sample
    
    # File reading
    with open(log_file, 'r') as fid:
        lines = fid.readlines()
    
    lnum = 0
    read_len = 128 * 1024 // 4
    dump_finish_addr = []
    data_i_unsigned = []
    data_q_unsigned = []
    
    for tline in lines:
        if '[0x40342228]' in tline:
            tline = tline.split(']')[-1]
            addr0 = tline.replace(' ', '').replace('=', '').replace('0x', '').replace('aic>', '')
            addr = int(addr0, 16)
            dump_finish_addr.append(addr)
        else:
            tline = tline.split(']')[-1]
    
        if 'r' in tline or 'Write' in tline or 'aic' in tline or '=' in tline or 'w' in tline or not tline.strip():
            continue
        else:
            lnum += 1
            a = tline.replace(' ', '').split(':')[-1]
            for n in range(4):
                if host == 1:
                    data_i_unsigned.append(int(a[n*8:n*8+4], 16))
                    data_q_unsigned.append(int(a[n*8+4:n*8+8], 16))
                else:
                    data_q_unsigned.append(int(a[n*8+2:n*8+4] + a[n*8:n*8+2], 16))
                    data_i_unsigned.append(int(a[n*8+6:n*8+8] + a[n*8+4:n*8+6], 16))
    
    data_i_unsigned = np.array(data_i_unsigned)
    data_q_unsigned = np.array(data_q_unsigned)
    
    L = len(data_i_unsigned)
    data_q_unsigned_floor = np.floor(data_q_unsigned / 2**4)
    data_i_unsigned_floor = np.floor(data_i_unsigned / 2**4)
    
    gain_index = data_i_unsigned - data_i_unsigned_floor * 2**4
    gain_2db = data_q_unsigned - data_q_unsigned_floor * 2**4
    
    gain = gain_index * 6 + gain_2db * 2
    
    if fpga_dump == 0 or dac150_dump == 1 or phy_dump == 1:
        data_i_unsigned = data_i_unsigned_floor
        data_q_unsigned = data_q_unsigned_floor
    else:
        data_i_unsigned = data_q_unsigned_floor
        data_q_unsigned = data_i_unsigned_floor
    
    N = 12  # s1.11
    if fpga_dump == 1 or dac150_dump == 1 or phy_dump == 1:
        data_i = np.where(data_i_unsigned >= 2**(N-1), data_i_unsigned - 2**N, data_i_unsigned)
        data_q = np.where(data_q_unsigned >= 2**(N-1), data_q_unsigned - 2**N, data_q_unsigned)
    else:
        data_i = data_i_unsigned - 2**(N-1)
        data_q = data_q_unsigned - 2**(N-1)
    
    if dump_finish_addr:
        if dump_finish_addr[0] == 0x80000000:
            print('NoStopTrig')
        else:
            data_i = np.concatenate((data_i[dump_finish_addr[0]:], data_i[:dump_finish_addr[0]]))
            data_q = np.concatenate((data_q[dump_finish_addr[0]:], data_q[:dump_finish_addr[0]]))
            gain = np.concatenate((gain[dump_finish_addr[0]:], gain[:dump_finish_addr[0]]))
    
    data = data_i + 1j * data_q
    dump_num = len(data) // read_len
    N1 = N
    
    with open('dump_result.txt', 'w') as fileID:
        data_store = np.zeros((dump_num, read_len), dtype=complex)
        for m in range(dump_num):
            d_i = data_i[m*read_len:(m+1)*read_len]
            d_q = data_q[m*read_len:(m+1)*read_len]
            i_dc = np.mean(d_i)
            q_dc = np.mean(d_q)
            pow = 10 * np.log10(np.sum(np.abs(((d_i-i_dc)/2**(N1-1) + 1j*(d_q-q_dc)/2**(N1-1))**2)) / len(d_i))
            # fileID.write(f';{round(i_dc):.1f};{round(q_dc):.1f};{np.floor(pow):.1f};\n')
            data_store[m] = d_i + 1j * d_q
    
    if Xlabel_unit == 1:
        T = np.arange(1, L+1) / Fs  # us
    else:
        T = np.arange(1, L+1)  # sample
    
    # time domain waveform
    plt.figure()
    plt.subplot(3, 1, 1)
    plt.plot(T, data_i[:L] / 2**12)
    plt.ylabel('DataI (normalized)')
    plt.xlabel('Time (us)' if Xlabel_unit == 1 else 'Time (sample)')
    
    plt.subplot(3, 1, 2)
    plt.plot(T, data_q[:L] / 2**12, 'm')
    plt.ylabel('DataQ (normalized)')
    plt.xlabel('Time (us)' if Xlabel_unit == 1 else 'Time (sample)')
    
    plt.subplot(3, 1, 3)
    plt.plot(T, gain[:L], 'r')
    plt.ylabel('GAIN dB')
    plt.xlabel('Time (us)' if Xlabel_unit == 1 else 'Time (sample)')

    # fft, frequency domain
    fs = np.linspace(-len(data_i)/2, len(data_i)/2-1, len(data_i)) / len(data_i) * Fs * 1e6
    
    plt.figure()
    plt.plot(fs, 20 * np.log10(np.abs(fftshift(fft(data_i + 1j * data_q)))))
    # plt.grid(which='minor')
    plt.grid(linestyle="--")

    # plt.show()
    

if __name__ == "__main__":
    # logFile1 = './data/loft_dump_20240911_1808_before.log'
    # logFile2 = './data/loft_dump_20240911_1808_after.log'
    # dump_log_plot(logFile1)
    # dump_log_plot(logFile2)

    log_file1 = "D:\\log\\aic8820_fem_loft_dbg_20240912_1957.log"
    dump_log_plot(log_file1)

    log_file2 = "D:\\log\\aic8820_fem_loft_dbg_20240912_1958.log"
    dump_log_plot(log_file2)

    plt.show()