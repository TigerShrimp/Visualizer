from argparse import ArgumentParser
from constants import CLASS_FILE_PLACEHOLDER, Color, CMD_FILE_PATH, TEMPLATE_CMD_FILE_PATH
from gdb import GDB
from parser import Parser
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
        "--sleep", "-s", help="Sleep time between info frames, default 0.1", type=float, default=.1)
    args = arg_parser.parse_args()
    classFile = args.file
    if classFile.endswith(".class"):
        return classFile, args.sleep
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
    classFile, sleepytime = parse_args()
    configure_gdb_commands_file(classFile)
    try:
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
    finally:
        remove(CMD_FILE_PATH)
        gdb.stop()


main()
