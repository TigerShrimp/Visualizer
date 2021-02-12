import re


class Parser():
    """ Handles extraction of relevant data from the GDB output
    """
    VARIABLES_PATTERN = r"\d+:\s(\w[0-9a-zA-Z]*\s=\s-?\d+)"
    REGISTERS_PATTERN = r"r[0-9a-z]+\s+0x[^\s]*"
    STOPPED_REASON_PATTERN = r"\*stopped,reason=\"([^\"]*)"

    def __init__(self):
        self.variables_regex = re.compile(Parser.VARIABLES_PATTERN)
        self.registers_regex = re.compile(Parser.REGISTERS_PATTERN)
        self.stopped_reason_regex = re.compile(Parser.STOPPED_REASON_PATTERN)

    def parse_variables(self, output):
        """ Parses variables in the form \"n: id = val\"

        Args:
          output: output from GDB after hitting a breakpoint
        Returns:
          [id, val]
        """
        return [v.split(" = ") for v in self.variables_regex.findall(output)]

    def parse_registers(self, output):
        """ Parses registers in the form \"reg  0x...\"

        Args:
          output: output from GDB after hitting a breakpoint
        Returns:
          [reg, 0x...]
        """
        return [list(filter(None, r.split(" "))) for r in self.registers_regex.findall(output)]

    def parse_stop_reason(self, output):
        """ Parses text in the form \"*stopped,reason=\"actual_reason\"\"

        Args:
          output: output from GDB after hitting a breakpoint
        Returns:
          actual_reason
        """
        stopped_reasons = self.stopped_reason_regex.findall(output)
        return stopped_reasons[-1] if stopped_reasons else ""

    def parse(self, output):
        """ Parses output from GDB.
        Currently supports variables, registers and stop reason

        Args:
          output: output from GDB after hitting a breakpoint
        Returns:
            parsed variables, registers and stop reason
        """
        variables = self.parse_variables(output)
        registers = self.parse_registers(output)
        stopped_reason = self.parse_stop_reason(output)
        return variables, registers, stopped_reason
