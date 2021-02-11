import subprocess
import threading
import re
from queue import Queue, Empty
from time import sleep


def reader(process, queue):
    for line in iter(process.stdout.readline, b''):
        queue.put(line.decode('Utf8'))


def read(queue):
    lines = ""
    while True:
        line = queue.get()
        lines += line
        if "(gdb)" in line and queue.empty():
            return lines


def write(process, command):  # Assure endl of command
    encodedCommand = command.encode('Utf8')
    print("Writing: {} to gdb".format(command[:-1]))
    process.stdin.write(encodedCommand)
    process.stdin.flush()
    sleep(0.5)


def najs_print(variables):
    for v in variables:
        v = v.split(" = ")
        print("The variable with name {} has value {} :)".format(v[0], v[1]))


cmd = ["gdb", "../TracingJITCompiler/build/TigerShrimp",
       "-x", "commands.txt", "-q", "--interpreter=mi"]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
readQueue = Queue()
reader = threading.Thread(target=reader, args=(p, readQueue))
reader.daemon = True
reader.start()
for i in range(10):
    write(p, "next\n")
    res = read(readQueue)
    pattern = r"\d+:\s(\w[0-9a-zA-Z]*\s=\s-?\d+)"
    regex = re.compile(pattern)
    variables = regex.findall(res)
    najs_print(variables)
sleep(10)
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
