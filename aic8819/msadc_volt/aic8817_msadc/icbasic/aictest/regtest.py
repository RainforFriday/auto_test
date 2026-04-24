import os
import sys
from enum import Enum


class wf_rf_intf(Enum):
    pu_trx = "40344000,12:11,2"

    def __str__(self):
        return self.value

    @property
    def address(self):
        return self.value.split(",")[0]


if __name__ == "__main__":
    print(wf_rf_intf.pu_trx)
    print(wf_rf_intf.pu_trx.address)