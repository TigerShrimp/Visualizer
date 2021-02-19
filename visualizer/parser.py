import re


class Parser():
    """ Handles extraction of relevant data from the LLDB output
    """
    REGISTERS_PATTERN = r"r[0-9a-z]+\s+0x[^\s]*"
    STOPPED_PATTERN = r"Process\s\d+\sexited\swith\sstatus\s=\s\d\s"
    LOCAL_VARIABLE_STORE_PATTERN = r"first = (\d+)[^.]*type = ([A-Za-z]+)[^.]*val = \(([^\)]+)"
    STACK_PATTERN = r"type = ([A-Za-z]+)[^.]*val = \(([^\)]+)"

    def __init__(self):
        self.registers_regex = re.compile(Parser.REGISTERS_PATTERN)
        self.stopped_regex = re.compile(Parser.STOPPED_PATTERN)
        self.local_variable_store_regex = re.compile(
            Parser.LOCAL_VARIABLE_STORE_PATTERN)
        self.stack_pattern_regex = re.compile(Parser.STACK_PATTERN)

    def parse_registers(self, output):
        """ Parses registers in the form \"reg  0x...\"

        Args:
          output: output from LLDB after hitting a breakpoint
        Returns:
          [reg, 0x...]
        """
        return [list(filter(None, r.split(" "))) for r in self.registers_regex.findall(output)]

    def parse_stopped(self, output):
        """ Parses text in the form \"Process #### exited with status = #"\"

        Args:
          output: output from LLDB after hitting a breakpoint
        Returns:
          True if stop message is found in output
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
        for chunk in chunks:
            if "General Purpose Registers:" in chunk:
                print("Registers:", chunk)
            elif "state->stack" in chunk:
                print("Stack:", chunk)
            elif "state->locals" in chunk:
                print("Locals:", chunk)
            elif any([var in chunk for var in ["state->method = ", "state->pc = ", "(Mnemonic) mnemonic = "]]):
                print("Variables:", chunk)

        registers = self.parse_registers(output)
        stopped = self.parse_stopped(output)
        return registers, stopped
