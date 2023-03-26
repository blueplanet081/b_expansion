import sys
import subprocess

for line in sys.stdin:
    text = line.strip()
    if text.startswith('#'):
        print(text)
    elif text and not text.startswith(' '):
        testcmd = "echo " + line.rstrip()
        print(testcmd)
        subprocess.run('bash -c ' + "'''" + testcmd + "'''", shell=True)
        # print()
        testcmd2 = "btest.py " + "'''" + line.rstrip() + "'''"
        # testcmd2 = "btest.py"
        print(testcmd2)
        # print(__file__)
        subprocess.run('python3 ' + testcmd2, shell=True)
        print()
        print()
