import sys
import subprocess

sep = "'''"

for line in sys.stdin:
    stext = line.strip()

    # 頭が # はコメント行
    if stext.startswith('#'):
        print(stext)
    
    # 空行と、頭がスペースの行は読み飛ばす
    elif stext and not stext.startswith(' '):
        sep = '"'
        if '"' in stext:
            sep = "'"
            # if "'" in stext:
            #     sep = "'''"
            #     print("3!!")

        testcmd = "echo " + stext
        print(testcmd)
        subprocess.run('bash -c ' + "'''" + testcmd + "'''", shell=True)

        print("btest.py " + sep + stext + sep)

        testcmd2 = "btest.py " + sep + stext + sep
        # testcmd2 = "btest.py"
        # print(__file__)
        subprocess.run('python3 ' + testcmd2, shell=True)
        print()
        print()
