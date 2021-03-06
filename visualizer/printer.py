import os
from constants import Color


class Printer():
    ''' Handles printing of data

      Args:
        height:
          Number of rows in each column
        strlen:
          Fixed length of every info string
    '''

    COLUMN_SPACING = '    '

    def __init__(self, height=8, strlen=24):
        self.height = height
        self.strlen = strlen

    def expand(self, string, columns=1):
        ''' Expands the given string with padding spaces to match strlen

        Args:
          string: String to be expanded
        Returns:
          padded string
        '''
        return string + ''.join([' ']*(self.strlen*columns-len(string))) + ''.join([Printer.COLUMN_SPACING]*columns)

    def format_value(self, id_val):
        ''' Formats id value pairs

        Args:
          id_val:
            iterable in the form (id, value)
        Returns:
          string in the form \'id = value\'
        '''
        if not id_val:
            return self.expand('')
        s = ''
        s += id_val[0]
        if s == 'r8' or s == 'r9':
            s += ' '
        s += ' = '
        s += str(id_val[1])
        return self.expand(s)

    def columns(self, lst):
        ''' Expands the argument list with None values to fill columns

        Args:
          lst: List to expand
        Returns:
          The number of columns that the items in the list takes up
        '''
        rem = len(lst) % self.height
        if rem != 0:
            lst.extend([None]*(self.height-rem))
        return len(lst) // self.height

    def construct_header(self, state):
        register_header = self.expand('Registers', 2)

        interpreter_state_header = ''
        if len(state.interpreter_state) > 0:
            interpreter_state_header = self.expand(
                'Interpreter State', self.columns(state.interpreter_state))

        loop_record_header = ''
        if len(state.loop_record) > 0:
            loop_record_header = self.expand(
                'Loop Record (method, pc)', self.columns(state.loop_record))

        variable_store_header = ''
        if len(state.variable_store) > 0:
            variable_store_header = self.expand(
                'Local Variable Store', self.columns(state.variable_store))

        stack_header = 'Stack (Top {})'.format(self.height)

        return Color.BOLD + register_header + interpreter_state_header + loop_record_header + variable_store_header + stack_header + Color.END + '\n'

    def print(self, state):
        ''' Clears the previous output and prints the given values in columns

        Args:
          state - see class in state.py
        '''
        os.system('clear')
        print(self.construct_header(state))

        for i in range(self.height):
            regstr1 = self.format_value(state.get_reg(i))
            regstr2 = self.format_value(state.get_reg(i+self.height))
            interpreter_varstr = ''
            for j in range(self.columns(state.interpreter_state)):
                interpreter_varstr += self.format_value(
                    state.interpreter_state[i + (j*self.height)])

            loop_record_varstr = ''
            for j in range(self.columns(state.loop_record)):
                loop_record_varstr += self.format_value(
                    state.loop_record[i+(j*self.height)])

            local_varstr = ''
            for j in range(self.columns(state.variable_store)):
                local_varstr += self.format_value(
                    state.variable_store[i + (j*self.height)])

            if i >= len(state.stack):
                stack_str = '-'
            else:
                stack_str = state.stack[i]

            print('{}{}{}{}{}{}'.format(regstr1, regstr2,
                                        interpreter_varstr, loop_record_varstr, local_varstr, stack_str))
