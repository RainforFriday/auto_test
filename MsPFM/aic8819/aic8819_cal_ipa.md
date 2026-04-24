### cal_ipa_hb(itgt=60)
1. setch 100
2. fix apc high_rate index_c
3. tone_on 0 0, tone_amp = 0
4. msadc initial
5. isense_config (isense_en = 1, isense_rbit = 4)
6. test_port_config (test_mode=3, test_bit= , pa_test_enable=1)
7. pa_hb_gain_en_dr=1, and set pa_hb_gain_en = 0
8. cal_ipa_vofst = volt_ms_avg(3)
9. pa_hb_gain_en_dr=1, and set pa_hb_gain_en = 1
10. cal_ipa_v = volt_ms_avg(3)
11. cal_ipa_init = (cal_ipa_v - cal_ipa_vofst)/res0
12. if cal_ipa_init < itgt:
        cal_ipa_sign = 1
    elif cal_ipa_init > itgt:
        cal_ipa_sign = -1
    else:
        cal_ipa_sign = 0
13. cal_ipa_ref = cal_ipa_init
14. cal_ipa_reg_ofst = 0
15. cal_ipa_reg_def = 32
16. if cal_ipa_sign == 0:
        cal_ipa_ires = cal_ipa_init
    else:
        for i in range(64):
            cal_ipa_reg_ofst = cal_ipa_reg_ofst + cal_ipa_sign
            cal_ipa_reg_value = cal_ipa_reg_def + cal_ipa_reg_ofst
            if cal_ipa_reg_value < 0:
                cal_ipa_reg_value = 0
            elif cal_ipa_reg_value > 63
                cal_ipa_reg_value = 63
            cal_ipa_reg_ofst = cal_ipa_reg_value - cal_ipa_reg_def

            write_reg(reg_name, posbit, cal_ipa_reg_value)

            cal_ipa_i = (volt_ms_avg(3) - cal_ipa_vofst)/res0
            print(cal_ipa_i, cal_ipa_reg_value)

            if (cal_ipa_i - itgt)\*(cal_ipa_ref - itgt) <= 0:
                if abs(cal_ipa_i - itgt) < abs(cal_ipa_ref - itgt):
                    cal_ipa_reg_ofst = cal_ipa_reg_ofst
                    cal_ipa_ires = cal_ipa_i
                else:
                    cal_ipa_reg_ofst = cal_ipa_reg_ofst - cal_ipa_sign
                    cal_ipa_ires = cal_ipa_ref
                print("cal done!!!")
                break
            else:
                cal_ipa_ref = cal_ipa_i

            if cal_ipa_reg_value == 63 || cal_ipa_reg_value == 0:
                cal_ipa_reg_ofst = cal_ipa_reg_ofst
                cal_ipa_ires = cal_ipa_i
                print("cal done!!!")
                break

17. release apc
18. isense_en = 0, isense_rbit=4
19. pa_test_enable = 0, test_bit=0, test_mode=0
20. pa_hb_gain_en_dr = 0
21. pa_hb_gain_en_reg = 0


