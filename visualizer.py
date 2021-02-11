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


def check_gdb_startup(queue):
    while True:
        try:
            line = queue.get(timeout=1)
            print(line)
        except Empty:
            return False
        else:
            if "(gdb)" in line and queue.empty():
                return True


def restart_gdb(process, thread):
    process.kill()
    # TODO Take care of thread so that they do not cause any further problems
    return start_gdb()


def start_gdb():
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
    p, read_queue = start_gdb()
    for (_, _) in enumerate(range(10)):
        write(p, "next\n")
        res = read(read_queue)
        pattern = r"\d+:\s(\w[0-9a-zA-Z]*\s=\s-?\d+)"
        regex = re.compile(pattern)
        variables = regex.findall(res)
        najs_print(variables)
    sleep(10)
    p.stdin.close()
    p.wait()
    print("Done")


main()
