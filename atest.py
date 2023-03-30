'''
    文字列パラメーターとか、文字列リテラルがどのように Pythonに認識されているか
    確認するためだけの、あほらしいプログラム
'''
import sys


def printdata(sdata: str) -> None:
    print(sdata)
    for i, chr in enumerate(sdata):
        print(f'{i}: [{chr}]')


# 指定されたパラメーターを表示する
if len(sys.argv) > 1:
    for sdata in sys.argv[1:]:
        printdata(sdata)
        print()

# パラメーターが無い時は、以下で指定した文字列リテラルを表示する
else:
    ldata = [
        '''{ABC\DEF"''}' ''',
        "ABC\"DEF\\'",
    ]
    for sdata in ldata:
        printdata(sdata)
        print()

    # print("引数を指定してください")
