'''
    b_extension 試験用プログラム        2023/03/25 by te.
'''
import sys
from b_expansion import b_expansion

if len(sys.argv) > 1:
    sdata = sys.argv[1]

    items = b_expansion(sdata)

    for it in items:
        print(it, end=" ")
    print()

else:
    print("b_extension 試験用プログラム")
    print('usage: btest "試験文字列"')
