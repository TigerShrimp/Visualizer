import os


class Printer():
    """ Handles printing of data

      Args:
        height:
          Number of rows in each column
        strlen:
          Fixed length of every info string
    """

    COLUMN_SPACING = "   "

    def __init__(self, height=8, strlen=24):
        self.height = height
        self.strlen = strlen

    def format_value(self, id_val):
        """ Formats id value pairs

        Args:
          id_val:
            iterable in the form (id, value)
        Returns:
          string in the form \"id = value\"
        """
        if not id_val:
            return "".join([" "]*self.strlen)
        s = ""
        s += id_val[0]
        if s == "r8" or s == "r9":
            s += " "
        s += " = "
        s += str(id_val[1])
        for _ in range(self.strlen - len(s)):
            s += " "
        return s

    def print(self, registers, stack, local_variables, interpreter_variables):
        """ Clears the previous output and prints the given values in columns

        Args:
          variables:
            string pairs parsed by Parser::parse_variables
          registers:
            string pairs parsed by Parser::parse_registers
        """
        os.system('clear')
        rem = len(interpreter_variables) % self.height
        if rem != 0:
            interpreter_variables.extend([None]*(self.height-rem))
        rem = len(local_variables) % self.height
        if rem != 0:
            local_variables.extend([None]*(self.height-rem))
        rem = len(stack) % self.height
        if rem != 0:
            stack.extend([None]*(self.height-rem))

        interpreter_variable_columns = len(
            interpreter_variables) // self.height
        local_variable_columns = len(local_variables) // self.height
        stack_columns = len(stack) // self.height
        for i in range(self.height):
            regstr1 = self.format_value(registers[i])
            regstr2 = self.format_value(registers[i+self.height])
            interpreter_varstr = ""
            for j in range(interpreter_variable_columns):
                interpreter_varstr += self.format_value(
                    interpreter_variables[i + (j*self.height)]) + Printer.COLUMN_SPACING

            local_varstr = ""
            for j in range(local_variable_columns):
                local_varstr += self.format_value(
                    local_variables[i + (j*self.height)]) + Printer.COLUMN_SPACING

            stack_str = ""
            for j in range(stack_columns):
                stack_val = str(stack[i + (j*self.height)]
                                )if stack[i + (j*self.height)] else ""
                stack_str += stack_val + Printer.COLUMN_SPACING

            print("{}{}{}{}{}{}{}".format(regstr1, Printer.COLUMN_SPACING, regstr2,
                                          Printer.COLUMN_SPACING, interpreter_varstr, local_varstr, stack_str))
