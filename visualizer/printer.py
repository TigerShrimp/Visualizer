import os


class Printer():
    """ Handles printing of data

      Args:
        height:
          Number of rows in each column
        strlen:
          Fixed length of every info string
    """

    def __init__(self, height=8, strlen=21):
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
        s += " = "
        s += str(id_val[1])
        for _ in range(self.strlen - len(s)):
            s += " "
        return s

    def print(self, variables, registers):
        """ Clears the previous output and prints the given values in columns

        Args:
          variables: 
            string pairs parsed by Parser::parse_variables
          registers: 
            string pairs parsed by Parser::parse_registers
        """
        if variables and registers:
            os.system('clear')
            rem = len(variables) % self.height
            if rem != 0:
                variables.extend([None]*(self.height-rem))

            variable_columns = len(variables) // self.height
            for i in range(self.height):
                regstr1 = self.format_value(registers[i])
                regstr2 = self.format_value(registers[i+self.height])
                varstr = ""
                for j in range(variable_columns):
                    varstr += self.format_value(variables[i + (j*self.height)])
                print("{}   {}   {}".format(regstr1, regstr2, varstr))
