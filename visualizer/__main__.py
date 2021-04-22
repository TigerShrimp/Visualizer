from argparse import ArgumentParser
from constants import CLASS_FILE_PLACEHOLDER, Color, CMD_FILE_PATH, TEMPLATE_CMD_FILE_PATH, CompilerState
from lldb import LLDB
from parser import Parser
from state import State
from printer import Printer
from os import remove
from time import sleep, time


BREAKPOINTS = {
    17: "BEFORE_RUN",
    31: "REC_COMPILE_DONE",
    35: "NATIVE_TRACE",
    55: "INIT_RECORDING",
    61: "INTERPRETER"
}


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
    breakpoints = "".join(["b RunTime.cpp:{}\n".format(bp)
                           for bp in BREAKPOINTS])
    with open(TEMPLATE_CMD_FILE_PATH, 'r') as template_file, open(CMD_FILE_PATH, 'w') as cmd_file:
        contents = template_file.read()
        contents = contents.replace(CLASS_FILE_PLACEHOLDER, classFile)
        cmd_file.write(breakpoints + contents)


def main():
    classFile, sleepytime, manual = parse_args()
    configure_gdb_commands_file(classFile)
    BREAKPOINTS[-1] = "NOT_FOUND"
    try:
        lldb = LLDB()
        parser = Parser()
        state = State()
        printer = Printer(24)
        lldb.start()
        while True:
            stop_reason = ''
            start_time = time()
            output = lldb.read()
            registers, stack, local_variables, pc, loop_record, recording, native_trace = parser.parse(
                output)
            if not state.loop_record and loop_record:
                stop_reason = 'Profiler found potential loop header, iterations in loop indicated'
            state.update(registers, pc, loop_record,
                         local_variables, stack, recording, native_trace)
            bp = BREAKPOINTS[parser.get_breakpoint(output)]
            if bp == "BEFORE_RUN":
                print("BEFORE_RUN")
                state.set_methods(parser.parse_code(output))
                lldb.write("continue\n")
                continue
            elif bp == "NATIVE_TRACE":
                state.compiler_state = CompilerState.NATIVE
                stop_reason = "Reached loop header with compiled trace"
            elif bp == "INIT_RECORDING":
                state.compiler_state = CompilerState.RECORDING
                stop_reason = "Hot loop header or side exit reached, recording will start"
                state.recording = []
                state.native_trace = []
            elif bp == "REC_COMPILE_DONE":
                stop_reason = "Compilation of trace finished"
                state.compiler_state = CompilerState.COMPILING
            elif bp == "INTERPRETER":
                if state.compiler_state == CompilerState.NATIVE:
                    state.compiler_state = CompilerState.INTERPRETING
                    stop_reason = "Exited trace, will continue interpret here"
            else:
                break
            if state.compiler_state == CompilerState.RECORDING:
                state.record_record.add(pc)

            printer.print(state)
            if manual or stop_reason:
                print()
                input(stop_reason + " -- Press ENTER to proceed")
            else:
                time_elapsed = time() - start_time
                sleep(max(sleepytime - time_elapsed, 0))
            lldb.write("continue\n")
    finally:
        remove(CMD_FILE_PATH)
        lldb.stop()


main()
