## ATTENTION: cal_pa5g_cbit calibration must be done before DPD calibration

def cal_pa5g_cbit():
    reg_dict = {0:"0", 1:"1", 2:"2", 3:"3", 4:"4", 5:"5", 6:"6", 7:"7", 8:"8", 9:"9", 10:"a", 11:"b", 12:"c", 13:"d", 14:"e", 15:"f"}
    #step1: open dpd path

    ########### cal high rate apc table
    #step2.1: load high rate apc

    #step2.2: set dig tone pwr, fix analog gain index : c

    #step2.3: tone_on

    #step2.4: cal rate apc cbit
    pwr_max = 0
    reg_max = 0
    for cbit in range(0, 4, 1):
        uart_sendcmd("setapc 32 31 " + str(cbit))
        pwr = pwr_measure()
        if pwr > pwr_max:
            pwr_max = pwr
            reg_max = cbit
    
    #step2.5: update high rate apc 32:31 --> cbit

    ########### cal mid rate apc table
    #step3.1: load mid rate apc

    #step3.2: set dig tone pwr, fix analog gian index : c

    #step3.3: tone_on

    #step3.4: cal rate apc cbit
    pwr_max = 0
    reg_max = 0
    for cbit in range(0, 16, 1):
        uart_sendcmd("setapc 80 77 " + reg_dict[cbit])
        pwr = pwr_measure()
        if pwr > pwr_max:
            pwr_max = pwr
            reg_max = cbit
    
    #step3.5: update mid rate apc 80:77 --> cbit


    ########### cal low rate apc table
    #step4.1: load low rate apc

    #step4.2: set dig tone pwr, fix analog gain index ： c

    #step4.3: tone_on

    #step4.4: cal rate apc cbit
    pwr_max = 0
    reg_max = 0
    for cbit in range(0, 16, 1):
        uart_sendcmd("setapc 80 77 " + reg_dict[cbit])
        pwr = pwr_measure()
        if pwr > pwr_max:
            pwr_max = pwr
            reg_max = cbit
    
    #step4.5: update low rate apc 80:77 --> cbit


    ########### cal done!
    #step5: close dpd path
    #step6: close tone