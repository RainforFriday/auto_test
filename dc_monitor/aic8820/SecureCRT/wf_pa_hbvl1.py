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
  sleep_msecs(100)
  crt.Screen.Synchronous = True
  crt.Screen.IgnoreEscape = True
  result = GetCommandResult("r 4010d010\r")
  ###crt.Dialog.MessageBox(result)
  hexval = result.split("= 0x",1)[1]
  decval = int(hexval, 16)
  vout = (decval-131328)*0.009244
  return vout


def main():
  send_string("w 40344088 01600000\r\n")
  send_string("w 40100038 000001A0\r\n") 
  send_string("w 4010d008 04003000\r\n") 
  send_string("w 4010d00c 0a0e95e7\r\n")
  send_string("w 4034400c 02002d65\r\n")
  send_string("w 40344008 0176aa71\r\n")
  hbvl1 = run_ms()
  send_string("w 4034400c 00002d65\r\n")
  send_string("w 40344088 01200000\r\n")
  str_hbvl1 = "HBVL1 =  " + "%.1f" % round(hbvl1, 1) + " mV"
  crt.Dialog.MessageBox(str_hbvl1)
main()