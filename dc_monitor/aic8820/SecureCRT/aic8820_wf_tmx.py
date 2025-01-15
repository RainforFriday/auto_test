import os
def GetCommandResult(command):
  crt.Screen.Send(command + "\n")
  crt.Screen.WaitForString("\n")
  crt.Screen.WaitForString("\n")
  return crt.Screen.ReadString("\n").strip()
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
def sleep_msecs(msecs):
  crt.Sleep(msecs)
def send_string(string):
  crt.Screen.Send(string)
def read_string():
  hexval = crt.Screen.ReadString()
def run_ms():
  send_string("w 4010d004 1\r\n")
  sleep_msecs(200)
  crt.Screen.Synchronous = True
  crt.Screen.IgnoreEscape = True
  result = GetCommandResult("r 4010d010\r")
  ###crt.Dialog.MessageBox(result)
  hexval = result.split("= 0x",1)[1]
  decval = int(hexval, 16)
  vout = (decval-131328)*0.009244
  return vout

def dtmx_testenable_on():
  send_string("w 40344088 01600000\r\n")   ## txon_dr
  send_string("w 40100038 000001A0\r\n")   ## clk cfg
  send_string("w 4010d008 04003000\r\n")   ## msadc set
  send_string("w 4010d00c 0a0e95e7\r\n")   ## msadc set
  send_string("w 4034400c 01002d65\r\n")   ## dtmx test_enable on


def dtmx_testenable_off():
  send_string("w 4034400c 00002d65\r\n")   ## dtmx test_enable off
  send_string("w 40344088 01200000\r\n")   ## tx on dr release


def ms_net(netname, testbit, mult=1.0):
  dtmx_testenable_on()
  ### dvdd_sw
  send_string("w 40344008 0176aa7{}\r\n".format(testbit))   ## test bit
  sleep_msecs(100)
  net_volt = run_ms()*mult
  str_net_volt = "{} =  ".format(netname) + "%.1f" % round(net_volt, 1) + " mV\n"
  dtmx_testenable_off()
  return(str_net_volt)


def main():
  #resx = ms_net("dvdd_sw", "0", 1.0)
  #resx = ms_net("vref_lo", "1", 1.0)
  #resx = ms_net("dac_vb", "2", 1.0)
  resx = ms_net("dac_vcscd", "3", 3.0)

  ##crt.Dialog.MessageBox(str_dvddsw+str_vref_lo+str_dac_vb+str_dac_vcscd)
  crt.Dialog.MessageBox(resx)

  """
  ### dvdd_sw
  send_string("w 40344008 0176aa70\r\n")   ## test bit
  dvdd_sw = run_ms()
  str_dvddsw = "dvdd_sw =  " + "%.1f" % round(dvdd_sw, 1) + " mV\n"
  sleep_msecs(100)
 
  ### vref_lo
  send_string("w 40344008 0176aa71\r\n")   ## test bit
  vref_lo = run_ms()
  str_vref_lo = "vref_lo =  " + "%.1f" % round(vref_lo, 1) + " mV\n"
  sleep_msecs(100)

  ### dac_vb
  send_string("w 40344008 0176aa72\r\n")   ## test bit
  dac_vb = run_ms()
  str_dac_vb = "dac_vb =  " + "%.1f" % round(dac_vb, 1) + " mV\n"
  sleep_msecs(100)

  ### dac_vcscd
  send_string("w 40344008 0176aa73\r\n")   ## test bit
  dac_vcscd = run_ms()*3.0
  str_dac_vcscd = "dac_vcscd =  " + "%.1f" % round(dac_vcscd, 1) + " mV\n"
  sleep_msecs(100)
  """

main()