import os


class Bin:
    def __init__(self, bin_path):
        self.path = bin_path

    def read_to_list(self):
        # read ref bin data
        ref_bin_file = open(self.path, "rb")
        ref_bin_size = os.path.getsize(self.path)
        ref_bin_data = []
        for i in range(ref_bin_size):
            ref_bin_data.append(ref_bin_file.read(1))
        ref_bin_file.close()
        return ref_bin_data

    def add0(self, strin):
        if len(strin) == 1:
            return "0"+strin
        else:
            return strin

    def replace_list(self, lb_pa=int(110), lb_padrv=int(18), hb_pa=int(120), hb_padrv=int(40)):
        l_old = [b'\x6e', b'\x12', b'\x78', b'\x28']
        lb_pa_new = bytes.fromhex(self.add0(str(hex(lb_pa))[2:]))
        lb_padrv_new = bytes.fromhex(self.add0(str(hex(lb_padrv))[2:]))
        hb_pa_new = bytes.fromhex(self.add0(str(hex(hb_pa))[2:]))
        hb_padrv_new = bytes.fromhex(self.add0(str(hex(hb_padrv))[2:]))
        l_new = [lb_pa_new, lb_padrv_new, hb_pa_new, hb_padrv_new]
        max = 10

        # replace cal ipa target current
        l_bin_data = self.read_to_list()
        flag_index = []
        for i in range(len(l_bin_data) - len(l_old)):
            if l_bin_data[i:i + len(l_old)] == l_old:
                flag_index.append(i)
            if len(flag_index) == max:
                break
        print(flag_index)
        for index in flag_index:
            l_bin_data[index:index+len(l_old)] = l_new

        return l_bin_data

    @staticmethod
    def write_bin(l_bin_data, bin_name):
        # write new bin to file
        new_bin_file = open(bin_name, "wb")
        for data_byte in l_bin_data:
            new_bin_file.write(data_byte)
        new_bin_file.close()

    def create_newbin(self, lb_pa=int(110), lb_padrv=int(18), hb_pa=int(120), hb_padrv=int(40)):
        new_bin_list = self.replace_list(lb_pa, lb_padrv, hb_pa, hb_padrv)
        new_str = str(lb_pa)+"_"+str(lb_padrv)+"_"+str(hb_pa)+"_"+str(hb_padrv)
        old_bin_name = os.path.basename(self.path)
        namex,extname = os.path.splitext(old_bin_name)
        new_bin_name = namex+"_"+new_str+extname
        self.write_bin(new_bin_list, new_bin_name)



if __name__ == "__main__":
    old_bin = "./testmode22_2025_0305_ipa.bin"
    # new_bin = "./testmode22_2025_0305.bin"

    BINX = Bin(old_bin)
    BINX.create_newbin(lb_pa=int(100), lb_padrv=int(10), hb_pa=int(110), hb_padrv=int(30))