import sys
import subprocess

sep = "'''"


def printdata(sdata: str) -> None:
    print(sdata)
    for i, chr in enumerate(sdata):
        print(f'{i}: [{chr}]')


testcmd = "echo " + "{1,,'2,\3'}"
tt = 'bash -c ' + '"' + testcmd + '"'
# tt = 'bash -c ' + "'''" + testcmd + "'''"
# tt = '''bash -c "echo {1,,'2,'"\'}' '''
tt = '''bash -c "echo {1,,'2,\\3'}" '''
print(tt)
subprocess.run(tt, shell=True)

tt = '''bash -c "echo {1,,'2,\\"3'}" '''
print(tt)
# subprocess.run('bash -c echo {1,,2,\3}', shell=True)
subprocess.run(tt, shell=True)
# subprocess.run('bash -c ' + "'''" + testcmd + "'''", shell=True)

# stt = "{1,,'2,\\3'}"
# {1,,'2,\"3'}
# echo {1,,'2,\"3'} -> 1 2,\"3
stt = '''{1,,'2,\\"3'} '''
print(stt)
stt = '''{1,,'2,\\"3'} '''
# stt = '''{1,,'2,\\ '''
# tt = 'bash -c "echo ' + stt + '"'
tt = 'bash -c "echo ' + stt + '"'
print(tt)
subprocess.run(tt, shell=True)

print("----")
# ttt = '''{1,,'2,\\"'"'"3'} '''
ttt = '"' + '''{1,,'2,\\"3'} ''' + '"'
print(ttt)
# subprocess.run('python3 btest.py ' + '"' + ttt + '"', shell=True)
subprocess.run('python3 btest.py ' + ttt, shell=True)
print()
