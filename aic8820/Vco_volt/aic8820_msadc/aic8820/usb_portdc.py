import os

def GetCommandResult(command):
    crt.Screen.Send(command + "\n")
    #crt.Screen.WaitForString("\n" )
    crt.Screen.WaitForString("\n")
    return crt.Screen.ReadString("\n").strip()
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def send_string(string):
    crt.Screen.Send(string)
def read_string():
    hexval = crt.Screen.ReadString()

def sleep_msecs(msecs):
    crt.Sleep(msecs)


def run_ms():
    send_string("w 4010d004 1\r\n")
    sleep_msecs(100)
    crt.Screen.Synchronous = True
    crt.Screen.IgnoreEscape = True
    result = GetCommandResult("r 4010d010\r")
    crt.Dialog.MessageBox(result)
    hexval = result.split("= 0x",1)[1]
    #crt.Dialog.MessageBox(hexval)
    decval = int(hexval, 16)
    vout = (decval-131328)*0.009244
    return vout



def main():
  send_string("w 4024100c 00030000\r\n")
  send_string("w 40241054 b5404223\r\n")
  send_string("w 40502018 000020e1\r\n")    #usb test en
  send_string("w 40100038 000001a0\r\n")    #1f0
  send_string("w 4010d008 0400300c\r\n")    #200
  send_string("w 4010d00c 0a0e95e7\r\n")
  usb_amp=run_ms()
  #sb_amp_str=p'%s' % usb_amp)
  crt.Dialog.MessageBox(str(usb_amp))
 # send_string("w 4010d004 00000001\r\n")
 # sleep_msecs(200)
 # send_string("r 4010d010\r\n")
main()
