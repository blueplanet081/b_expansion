'''
    b_extension 試験用プログラム（一項目ずつ改行して表示）        2023/03/25 by te.
'''
import sys
from b_expansion import b_expansion

if len(sys.argv) > 1:
    sdata = sys.argv[1]

    items = b_expansion(sdata)

    for it in items:
        print(it)

else:
    print("b_extension 試験用プログラム（一項目ずつ改行して表示）")
    print('usage: btest "試験文字列"')
