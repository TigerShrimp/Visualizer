import re


class Parser():
    """ Handles extraction of relevant data from the LLDB output
    """
    REGISTERS_PATTERN = r"(r..?) = 0x0+([0-9a-f]+)"
    STOPPED_PATTERN = r"Process\s\d+\sexited\swith\sstatus\s=\s\d\s"
    LOCAL_VARIABLE_STORE_PATTERN = r"first = (\d+)[^.]*type = ([A-Za-z]+)[^.]*val = \(([^\)]+)"
    STACK_PATTERN = r"type = ([A-Za-z]+)[^.]*val = \(([^\)]+)"
    INTERPRETER_VARS_PATTERN = r"\([^)]+\) ([a-zA-Z0-9->]+) = ([^\n]+)"

    def __init__(self):
        self.registers_regex = re.compile(Parser.REGISTERS_PATTERN)
        self.stopped_regex = re.compile(Parser.STOPPED_PATTERN)
        self.local_variable_store_regex = re.compile(
            Parser.LOCAL_VARIABLE_STORE_PATTERN)
        self.stack_regex = re.compile(Parser.STACK_PATTERN)
        self.interpreter_var_regex = re.compile(
            Parser.INTERPRETER_VARS_PATTERN)

    def parse_registers(self, output):
        """ Parses registers in the form \"reg = 0x...\"

        Args:
          output: output from LLDB after hitting a breakpoint
        Returns:
          [reg, 0x...]
        """
        return [(r[0], "0x{}".format(r[1])) for r in self.registers_regex.findall(output)]

    def parse_value_given_type(self, value_type, values):
        order = {"Int": 0, "Long": 1, "Float": 2, "Double": 3}
        return values.split(',')[order[value_type]].split(' = ')[1]

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
        variables = []
        for match in self.local_variable_store_regex.findall(output):
            ident = match[0]
            value = self.parse_value_given_type(match[1], match[2])
            variables.append((ident, value))
        return variables

    def parse_stack_values(self, output):
        """ Parses the values from the interpreter stack.
        The regex to extract the stack values is very similar to the regex for 
        the local variable store with the exception that it lacks the identifier.

        Args:
          Output from LLDB after hitting a breakpoint
        Returns:
          List of the stack values
        """
        stack = []
        for match in self.stack_regex.findall(output):
            stack.append(self.parse_value_given_type(match[0], match[1]))
        return stack

    def parse_interpreter_variable(self, output):
        """
        regex.findAll returns a list of matches but we onyl have one which is
        why we extract the first argument. 

        Args: 
          Output from LLDB after hitting a breakpoint
        Returns: 
          Tuple of name and value of an interpreter variable. 
        """
        return self.interpreter_var_regex.findall(output)[0]

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
        interpreter_variables = []
        for chunk in chunks:
            if "General Purpose Registers:" in chunk:
                registers = self.parse_registers(chunk)
            elif "state->stack" in chunk:
                stack = self.parse_stack_values(chunk)
            elif "state->locals" in chunk:
                local_variables = self.parse_local_variables(chunk)
            elif any([var in chunk for var in ["state->method = ", "state->pc = ", "(Mnemonic) mnemonic = "]]):
                interpreter_variables.append(
                    self.parse_interpreter_variable(chunk))

        stopped = self.parse_stopped(output)
        return registers, stack, local_variables, interpreter_variables, stopped
