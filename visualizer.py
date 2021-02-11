import subprocess
import threading
import re
import sys
import os
from queue import Queue, Empty
from time import sleep
import numpy as np

variables_pattern = r"\d+:\s(\w[0-9a-zA-Z]*\s=\s-?\d+)"
registers_pattern = r"r[0-9a-z]+\s+0x[^\s]*"
stopped_reason_pattern = r"\*stopped,reason=\"([^\"]*)"
variables_regex = re.compile(variables_pattern)
registers_regex = re.compile(registers_pattern)
stopped_reason_regex = re.compile(stopped_reason_pattern)
height = 8
strlen = 21


def reader(process, queue):
    for line in iter(process.stdout.readline, b''):
        queue.put(line.decode('Utf8'))


def read(queue):
    lines = ""
    while True:
        line = queue.get()
        # print("Read: {}".format(line))
        lines += line
        if "(gdb)" in line and queue.empty():
            return lines


def write(process, command):  # Assure endl of command
    encodedCommand = command.encode('Utf8')
    process.stdin.write(encodedCommand)
    process.stdin.flush()


def najs_print(variables):
    for v in variables:
        v = v.split(" = ")
        print("The variable with name {} has value {} :)".format(v[0], v[1]))


def check_gdb_startup(queue):
    while True:
        try:
            line = queue.get(timeout=1)
        except Empty:
            return False
        else:
            if "(gdb)" in line and queue.empty():
                return True


def restart_gdb(process, thread):
    process.kill()
    # TODO Take care of thread so that they do not cause any further problems
    return start_gdb()


def format_value(val):
    if not val:
        return "".join([" "]*strlen)
    s = ""
    s += val[0]
    s += " = "
    s += str(val[1])
    for _ in range(strlen - len(s)):
        s += " "
    return s


def output(variables, registers):
    os.system('clear')
    rem = len(variables) % height
    if rem != 0:
        variables.extend([None]*(height-rem))

    variable_columns = len(variables) // height
    for i in range(height):
        regstr1 = format_value(registers[i])
        regstr2 = format_value(registers[i+8])
        varstr = ""
        # registers[i], resgisters[i+(8 or 16)], [variables[i+8*k]] k = {..j}
        for j in range(variable_columns):
            varstr += format_value(variables[i + (j*height)])
        print("{}   {}   {}".format(regstr1, regstr2, varstr))


def start_gdb():
    """
    Starts gdb and listens to its output to determine wether it started up without issues.
    If issues occurs with gdb, it will be restared until issues not occur.
    Runs gdb ../TracingJITCompiler/build/TigerShrimp -x commands.txt -q --interpreter=mi
    """
    cmd = ["gdb", "../TracingJITCompiler/build/TigerShrimp",
           "-x", "commands.txt", "-q", "--interpreter=mi"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    read_queue = Queue()
    reader_t = threading.Thread(target=reader, args=(p, read_queue))
    reader_t.daemon = True
    reader_t.start()
    if check_gdb_startup(read_queue):
        return p, read_queue
    else:
        return restart_gdb(p, reader_t)


def main():
    sleepytime = float(sys.argv[1]) if len(sys.argv) > 1 else 0
    p, read_queue = start_gdb()
    stopped_reason = ""
    while stopped_reason != "exited-normally":
        write(p, "continue\n")
        res = read(read_queue)
        variables = [v.split(" = ") for v in variables_regex.findall(res)]
        stopped_reasons = stopped_reason_regex.findall(res)
        stopped_reason = stopped_reasons[-1] if stopped_reasons else ""
        registers = [list(filter(None, r.split(" ")))
                     for r in registers_regex.findall(res)]
        if registers and variables:
            output(variables, registers)
        sleep(sleepytime)
    p.stdin.close()
    p.wait()
    print("Done")


main()
