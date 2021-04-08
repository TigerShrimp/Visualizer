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
        assert(height % 2 == 0)
        self.height = height
        self.strlen = strlen

    def code_at(self, methods, pc, loop_record):
        (method_index, instruction_index) = pc
        (name, conversion, code) = methods[method_index]
        inst_row = conversion[instruction_index]
        output = [self.expand("{}:".format(name))]
        if len(code) < self.height-1:
            start = 0
            stop = len(code)
        else:
            start = 0 if inst_row - \
                (self.height-1) // 2 < 0 else inst_row - (self.height-1) // 2
            stop = start + self.height-1
            if stop > len(code):
                start -= stop-len(code)
                stop = len(code)
        for (i, (inst, c)) in enumerate(code[start:stop]):
            prefix = "-> " if i+start == inst_row else "   "
            row = prefix + c
            row = self.expand(row)
            curr_pc = (method_index, inst)
            if curr_pc in loop_record:
                row = Color.RED + \
                    row[:-(len(loop_record[curr_pc]))-len(Printer.COLUMN_SPACING)] + \
                    loop_record[curr_pc] + Printer.COLUMN_SPACING + Color.END

            output.append(row)
            # Expand to always have self.height rows.
        output += [self.expand("")]*(self.height - len(output))

        return output

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
        register_header = self.expand(
            'Registers', self.columns(state.register_names))

        interpreter_state_header = self.expand('Code')

        # loop_record_header = ''
        # if len(state.loop_record) > 0:
        #     loop_record_header = self.expand(
        #         'Loop Record (method, pc)', self.columns(state.loop_record))

        variable_store_header = ''
        if len(state.variable_store) > 0:
            variable_store_header = self.expand(
                'Local Variable Store', self.columns(state.variable_store))

        stack_header = 'Stack (Top {})'.format(self.height)

        return Color.BOLD + register_header + interpreter_state_header + variable_store_header + stack_header + Color.END + '\n'

    def print(self, state):
        ''' Clears the previous output and prints the given values in columns

        Args:
          state - see class in state.py
        '''
        os.system('clear')
        print(self.construct_header(state))
        code = self.code_at(state.methods, state.pc, state.loop_record)
        for i in range(self.height):
            regstr = ''
            for j in range(self.columns(state.register_names)):
                regstr += self.format_value(state.get_reg(i+(j*self.height)))

            # interpreter_varstr = ''
            # for j in range(self.columns(state.interpreter_state)):
            #     interpreter_varstr += self.format_value(
            #         state.interpreter_state[i + (j*self.height)])

            code_varstr = code[i]

            # loop_record_varstr = ''
            # for j in range(self.columns(state.loop_record)):
            #     loop_record_varstr += self.format_value(
            #         state.loop_record[i+(j*self.height)])

            local_varstr = ''
            for j in range(self.columns(state.variable_store)):
                local_varstr += self.format_value(
                    state.variable_store[i + (j*self.height)])

            if i >= len(state.stack):
                stack_str = '-'
            else:
                stack_str = state.stack[i]

            print('{}{}{}{}'.format(regstr, code_varstr, local_varstr, stack_str))
