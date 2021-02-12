from gdb import GDB
from parser import Parser
from printer import Printer
import sys
from time import sleep


def main():
    sleepytime = float(sys.argv[1]) if len(sys.argv) > 1 else 0
    gdb = GDB()
    parser = Parser()
    printer = Printer()
    gdb.start()
    stopped_reason = ""
    while stopped_reason != "exited-normally":
        gdb.write("continue\n")
        output = gdb.read()
        variables, registers, stopped_reason = parser.parse(output)
        printer.print(variables, registers)
        sleep(sleepytime)
    gdb.stop()


main()
