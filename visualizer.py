import subprocess
import threading
from time import sleep


def read(process):
    res = ""
    for line in iter(process.stdout.readline, b'(gdb) \n'):
        res += line.decode('Utf8')
    return res


def write(process, command):
    encodedCommand = command.encode('Utf8')
    print("Writing:", encodedCommand)
    process.stdin.write(encodedCommand)
    process.stdin.flush()
    sleep(0.5)


cmd = ["gdb", "/Users/jakoberlandsson/Documents/MasterThesis/TracingJITCompiler/build/TigerShrimp",
       "-x", "commands.txt", "-q", "--interpreter=mi"]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                     stdin=subprocess.PIPE)
# p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
res = read(p)
print(res)
write(p, "next\n")
res = read(p)
print(res)
p.stdin.close()
p.wait()
print("Done")
# sleep(5)
# write(p, "next\n\0")
# write(p, "next\n\0")
# write(p, "next\n\0")
# write(p, "next\n\0")
# write(p, "next\n\0")
# write(p, "next\n\0")
# sleep(10)
# read(p)

# from pygdbmi.gdbcontroller import GdbController
# from pprint import pprint

# # Start gdb process
# gdbmi = GdbController()
# # print(gdbmi.get_subprocess_cmd())  # print actual command run as subprocess

# # Load binary a.out and get structured response
# response = gdbmi.write(
#     '-file-exec-file /Users/jakoberlandsson/Documents/MasterThesis/TracingJITCompiler/build/TigerShrimp')
# pprint(response)

# response = gdbmi.write(
#     'break Interpreter.cpp:interpret')
# pprint(response)
# response = gdbmi.write(
#     'run /Users/jakoberlandsson/Documents/MasterThesis/TracingJITCompiler/test/java.class')
# pprint(response)
