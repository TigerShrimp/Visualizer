import os
from constants import Color, CompilerState
from random import getrandbits


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

    def code_at(self, methods, pc, state):
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
            if curr_pc in state.loop_record:
                row = Color.RED + \
                    row[:-(len(state.loop_record[curr_pc]))-len(Printer.COLUMN_SPACING)] + \
                    state.loop_record[curr_pc] + \
                    Printer.COLUMN_SPACING + Color.END
            elif curr_pc in state.record_record:
                row = Color.MAGENTA + row + Color.END

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

    def construct_first_header(self, state):
        register_header = self.expand(
            'Registers', self.columns(state.register_names))

        interpreter_state_header = self.expand('Code')

        variable_store_header = ''
        if len(state.variable_store) > 0:
            variable_store_header = self.expand(
                'Local Variable Store', self.columns(state.variable_store))

        stack_header = 'Stack (Top {})'.format(min(self.height,8) )

        return Color.BOLD + register_header + interpreter_state_header + variable_store_header + stack_header + Color.END + '\n'

    def construct_second_header(self, state):
        record_header = self.expand(
            'Recording', self.columns(state.recording))

        compiled_state_header = self.expand(
            'Compiled Trace') if state.compiler_state == CompilerState.COMPILING else ''

        return Color.BOLD + record_header + compiled_state_header + Color.END + '\n'

    def construct_headest(self, state):
        return Color.BLUE + Color.BOLD + state.compiler_state + Color.END + '\n'
        # return Color.BLUE + Color.BOLD + "".join([x.lower() if getrandbits(1) else x for x in state.compiler_state]) + Color.END + "\n"

    def get_line_nr(self, index):
        return (" {}" if index+1 < 10 else "{}").format(index+1)

    def print(self, state):
        ''' Clears the previous output and prints the given values in columns

        Args:
          state - see class in state.py
        '''
        os.system('clear')
        print(self.construct_headest(state))
        print(self.construct_first_header(state))
        code = self.code_at(state.methods, state.pc, state)
        # First set of columns
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

            if i < len(state.stack) and i < 8:
                stack_str = state.stack[i]
            elif i < 8:
                stack_str = '-'
            else:
                stack_str = ''

            print('{}{}{}{}'.format(regstr, code_varstr, local_varstr, stack_str))

        # Second set of columns
        if state.compiler_state in [CompilerState.RECORDING, CompilerState.COMPILING]:
            snd_height = min(self.height, max(len(state.recording), len(state.native_trace) if state.compiler_state == CompilerState.COMPILING else 0))
            print()
            print(self.construct_second_header(state))
            for i in range(snd_height):
                record_str = ''
                for j in range(self.columns(state.recording)):
                    record_str += self.expand(
                        "{}: {}".format(self.get_line_nr(i+snd_height*j),state.recording[i+snd_height*j]) if state.recording[i+snd_height*j] else '')

                native_str = ''
                if(state.compiler_state == CompilerState.COMPILING):
                    for j in range(self.columns(state.native_trace)):
                        native_str += self.expand(
                            "{}: {}".format(self.get_line_nr(i+snd_height*j), state.native_trace[i+snd_height*j]) if state.native_trace[i+snd_height*j] else '')

                print('{}{}'.format(record_str, native_str))
