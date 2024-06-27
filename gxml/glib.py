import re

def str2int(str0='0', vbase=None):
    '''
    string to int value:
        if   exist prefix-base, use prefix-base
        elif assign param-base, use param-base
        elif all [0-9]        , use 10-base
        else                  , use 16-base
    :param str0: string number
        (\d*d:)?\d+            dec number
        (\d*h:)?[a-f0-9]+   hex number
        (\d*x:)?[a-f0-9]+   hex number
        (\d*b:)?[01]+          bin number  <remove>
        else                0
    :param vbase: 2/10/16
        if not assign a prefix, then use @vbase to trans
    :return: dec integer
    '''

    mstr = re.sub(r'[\s_]', '', str0.lower())
    mch_obj = re.match(r'(\d*[bdhx]:)?([a-f0-9]+)', mstr)

    # parse code & base
    if (mch_obj is None) or (mch_obj.group(2) is None):
        code = '0'
        base = 16
    else:
        code = mch_obj.group(2)
        if mch_obj.group(1) is not None:
            mmap = {'h': 16, 'x': 16, 'd': 10, 'b': 2}
            base = mmap[mch_obj.group(1)[-2]]
        elif vbase is not None:
            base = vbase
        elif re.match(r'^\d+$', code):
            base = 10
        else:
            base = 16
    # valid code with base
    if ((base ==  2) and (not re.match(r'^[0-1]+$', code))) or \
       ((base == 10) and (not re.match(r'^[0-9]+$', code))) or \
       ((base == 16) and (not re.match(r'^[0-9a-f]+$', code))) :
        mval = 0
    else:
        mval = int(code, base)

    return mval


def hget(x, msb, lsb):
    # return x[msb:lsb]
    msk = (1 << (msb+1)) - (1 << lsb)
    return (x & msk) >> lsb


def hset(x, msb, lsb, val):
    # return x[msb:lsb] = val
    msk = (1 << (msb+1)) - (1 << lsb)
    y = (x & ~msk) | ((val << lsb) & msk)
    return y

