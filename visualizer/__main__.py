from argparse import ArgumentParser
from constants import CLASS_FILE_PLACEHOLDER, Color, CMD_FILE_PATH, TEMPLATE_CMD_FILE_PATH
from lldb import LLDB
from parser import Parser
from state import State
from printer import Printer
from os import remove
from time import sleep


def parse_args():
    """ Parse and validates command line arguments

    Returns:
      classFile, sleep
    """
    arg_parser = ArgumentParser(
        description="visualizer: visualize run-time behavior of TigerShrimp's Tracing JIT Compiler")
    arg_parser.add_argument(
        "file", help="JVM class file that the JIT compiler should run", type=str)
    arg_parser.add_argument(
        "--asm", help="Predefined native code for program form (file.asm method_id trace_start trace_end)", nargs=4, type=str, default=[""])
    group = arg_parser.add_mutually_exclusive_group()
    group.add_argument(
        "--sleep", "-s", help="Sleep time between info frames, default 0.1", type=float, default=.1)
    group.add_argument(
        "--manual", "-m", help="Manually step through the program", action='store_true')
    args = arg_parser.parse_args()
    classFile = args.file
    if classFile.endswith(".class"):
        return " ".join([classFile] + args.asm), args.sleep, args.manual
    else:
        print("visualizer: {}error{}: given file should be an .class file".format(
            Color.RED, Color.END))
        exit(-1)


def configure_gdb_commands_file(classFile):
    """ Puts the classFile into the list of commands to GDB
    """
    with open(TEMPLATE_CMD_FILE_PATH, 'r') as template_file, open(CMD_FILE_PATH, 'w') as cmd_file:
        contents = template_file.read()
        contents = contents.replace(CLASS_FILE_PLACEHOLDER, classFile)
        cmd_file.write(contents)


def main():
    classFile, sleepytime, manual = parse_args()
    configure_gdb_commands_file(classFile)
    try:
        lldb = LLDB()
        parser = Parser()
        state = State()
        printer = Printer()
        lldb.start()
        stopped = None
        while not stopped:
            lldb.write("continue\n")
            output = lldb.read()
            registers, stack, local_variables, interpreter_variables, loop_record, stopped = parser.parse(
                output)
            state.update(registers, interpreter_variables, loop_record,
                         local_variables, stack)
            printer.print(state)
            if manual:
                input("Press ENTER to proceed")
            else:
                sleep(sleepytime)
    finally:
        remove(CMD_FILE_PATH)
        lldb.stop()


main()
