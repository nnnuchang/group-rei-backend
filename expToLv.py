def expToLv(exp):
    lvExpList = [6896, 8192, 14744, 16384, 26212, 32768, 39320, 65536, 91748, 131072]
    needExpList = [431, 432, 819, 820, 1638, 1639, 3276, 3277, 6553, 6554]
    lvList = [1, 17, 20, 28, 30, 36, 40, 42, 50, 54]

    for i in range(len(lvExpList)):
        lvExp = lvExpList[i]
        needExp = needExpList[i]

        if(i >0): previousOne = lvExpList[i - 1]
        else: previousOne = 0

        if(exp <= lvExp):
            lv = int((exp - previousOne) / needExp) + lvList[i]
            return lv