import re


class Parser():
    """ Handles extraction of relevant data from the LLDB output
    """
    REGISTERS_PATTERN = r"(r..?) = 0x0+([0-9a-f]+)"
    STOPPED_PATTERN = r"Process\s\d+\sexited\swith\sstatus\s=\s\d\s"
    # LOCAL_VARIABLE_STORE_PATTERN = r"first = (\d+)[^.]*type = ([A-Za-z]+)[^.]*val = \(([^\)]+)"
    # PROFILE_RECORD_PATTERN = r"method = (\d+)\n.*pc = (\d+)\n.*second = (\d+)"
    # STACK_PATTERN = r"type = ([A-Za-z]+)[^.]*val = \(([^\)]+)"
    # INTERPRETER_VARS_PATTERN = r"\([^)]+\) ([a-zA-Z0-9->]+) = ([a-zA-Z_0-9]+)"

    """
    [0] = (first = 1, second = 2/ICONST)
    matches are 1 and 2/ICONST
    """
    MAP_PATTERN = r"\[\d+\] = \(first = (\d+), second = ([^)]*)"
    """
    [0] = ((24, 1), first = 5)
    matches are 24, 1 and 5
    """
    PAIR_MAP_PATTERN = r"\(([\d]+), ([\d]+)\)\D*(\d+)*"
    """
    [0] = something
    match is something
    """
    LIST_PATTERN = r"\[\d+\] = ([^\n]*)"

    """
    [0] = {
    first = "<init> (5)"
    second = size=3 {
      [0] = (first = 0, second = ALOAD_0)
    }
    match is:
    first = "<init> (5)"
    second = size=3 {
      [0] = (first = 0, second = ALOAD_0)
    """
    CODE_PATTERN = r"\[\d+] = \{(.*?)}\n"

    """
    first = "main (23)"
    match is main, 23
    """
    METHOD_ID_PATTERN = r"first = \"(.+?) \((\d+)\)"
    """
    Long console text, after reaching a breakpoint.
    match is line number of breakpoint.
    """
    BREAKPOINT_PATTERN = r"TigerShrimp`RunTime::run\(this.*? at RunTime\.cpp:(\d+)"

    def __init__(self):
        self.registers_regex = re.compile(Parser.REGISTERS_PATTERN)
        self.stopped_regex = re.compile(Parser.STOPPED_PATTERN)
        self.map_regex = re.compile(Parser.MAP_PATTERN)
        self.pair_map_regex = re.compile(Parser.PAIR_MAP_PATTERN)
        self.list_regex = re.compile(Parser.LIST_PATTERN)
        self.code_regex = re.compile(
            Parser.CODE_PATTERN,  re.MULTILINE | re.DOTALL)
        self.method_id_regex = re.compile(Parser.METHOD_ID_PATTERN)
        self.breakpoint_regex = re.compile(Parser.BREAKPOINT_PATTERN)

    def parse_code(self, output):
        matches = self.code_regex.findall(output)
        methods = {}
        for match in matches:
            method_id_match = self.method_id_regex.findall(match)[0]
            method_match = self.map_regex.findall(match)
            pc_conversion = {pc: index for (
                index, (pc, _)) in enumerate(method_match)}

            methods[method_id_match[1]] = (
                method_id_match[0], pc_conversion, method_match)
        return methods

    def parse_registers(self, output):
        """ Parses registers in the form \"reg = 0x...\"

        Args:
          output: output from LLDB after hitting a breakpoint
        Returns:
          [reg, 0x...]
        """
        return [(r[0], "0x{}".format(r[1])) for r in self.registers_regex.findall(output)]

    def get_breakpoint(self, output):
        """
        Retreive the line number of the latest breakpoint stopped at.
        Args:
          output: output from LLDB after hitting a breakpoint
        Returns:
          line number of breakpoint or -1 if something went wrong
        """
        match = self.breakpoint_regex.findall(output)
        return int(match[-1]) if match else -1

    def parse_local_variables(self, output):
        """ Parses the local variables map.
        The regex produces one match for each variable in the variable store
        where each match contains three groups:
          1 - the id of the variable
          2 - the type of the variable
          3 - list of values for the different types where only the one 
              corresponding to the type of the variable matters.

        Args:
          output: output from LLDB after hitting a breakpoint
        Returns:
           variables in the variable store, identifier and value
        """
        return [("[{}]".format(match[0]), match[1]) for match in self.map_regex.findall(output)]

    def parse_stack_values(self, output):
        """ Parses the values from the interpreter stack.
        The regex to extract the stack values is very similar to the regex for 
        the local variable store with the exception that it lacks the identifier.

        Args:
          Output from LLDB after hitting a breakpoint
        Returns:
          List of the stack values
        """
        return [match for match in self.list_regex.findall(output)]

    def parse_interpreter_variable(self, output):
        """
        regex.findAll returns a list of matches but we only have one which is
        why we extract the first argument. 

        Args: 
          Output from LLDB after hitting a breakpoint
        Returns: 
          Tuple of name and value of an interpreter variable. 
        """
        return self.pair_map_regex.findall(output)[0]

    def parse_profile_record(self, output):
        return {(match[0], match[1]): match[2] for match in self.pair_map_regex.findall(output)}

    def parse_stopped(self, output):
        """ Parses text in the form \"Process #### exited with status = #"\"

        Args:
          output: output from LLDB after hitting a breakpoint
        Returns:
          None if stop message is not found in output else something
        """
        return self.stopped_regex.search(output)

    def parse(self, output):
        """ Parses output from LLDB.
        Currently supports variables, registers and stop reason

        Args:
          output: output from LLDB after hitting a breakpoint
        Returns:
            parsed variables, registers and stop reason
        """
        chunks = output.split("\n\n")
        registers = None
        stack = None
        local_variables = None
        pc = None
        loop_record = []
        recording = []
        native_trace = []
        for chunk in chunks:
            if "General Purpose Registers:" in chunk:
                registers = self.parse_registers(chunk)
            elif "state->stack" in chunk:
                stack = self.parse_stack_values(chunk)
            elif "state->locals" in chunk:
                local_variables = self.parse_local_variables(chunk)
            elif "profiler.loopRecord" in chunk:
                loop_record = self.parse_profile_record(chunk)
            elif "traceRecorder.recordedTrace" in chunk:
                recording = [match for match in self.list_regex.findall(chunk)]
            elif "compiler.nativeTrace" in chunk:
                native_trace = [
                    match for match in self.list_regex.findall(chunk)]
            elif "(ProgramCounter) pc = " in chunk:
                (m, pc, _) = self.parse_interpreter_variable(chunk)
                pc = (m, pc)
        return registers, stack, local_variables, pc, loop_record, recording, native_trace
