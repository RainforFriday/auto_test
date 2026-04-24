def read_csv():
    with open(csv_name1,encoding='gb18030', errors='ignore') as CSV:
        txt1=CSV.read().split("\n")
    with open(csv_name2,encoding='gb18030', errors='ignore') as CSV:
        txt2=CSV.read().split("\n")
    with open(csv_name,encoding='gb18030', errors='ignore') as CSV:
        txt=CSV.read().split("\n")
    for i in range(1,len(txt),1):
        if txt[i]!="":
            item=txt[i]
    for i in range(0, len(txt1), 1):
        item = txt1[i].split(",")
        BOR=item[0]
        NAME=item[1]
        MODE=item[3]
        dvdd1=item[2]
        dvdd=item[2]+","+item[3]+","+item[4]
        if dvdd1=="null":
            dvdd=txt2[i].split(",")[2]+","+txt2[i].split(",")[3]+","+txt2[i].split(",")[4]
        with open(csv_name, encoding='gb18030', errors='ignore') as CSV:
            txt3 = CSV.readlines()
            with open("./" + csv_name3, "a+", ) as  CSVFILE:
                if i ==0:
                    CSVFILE.write(txt3[0])
                    CSVFILE.write(txt3[1])
                    CSVFILE.write(txt3[i+2].split("\n")[0] + "," + str(dvdd)+"\n")
                else:
                    CSVFILE.write(txt3[i + 2].split("\n")[0] + "," + str(dvdd) + "\n")

if __name__ == "__main__":
    #dvdd_wifi_result = "aic8820h1_wifi1515.csv"
    #dvdd_bt_result = "aic8820h1_bt.csv"
    csv_name1 = "aic8820h1_wifi_70.csv"
    csv_name2 = "aic8820h1_bt_70.csv"
    csv_name = "aic8820h_spec_testability.csv"
    csv_name3="aic8820h_key_volte_70.csv"
    read_csv()

