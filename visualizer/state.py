class State:
    def __init__(self):
        self.registers = {
            "rax": "0x0",
            "rbx": "0x0",
            "rcx": "0x0",
            "rdx": "0x0",
            "rdi": "0x0",
            "rsi": "0x0",
            "rbp": "0x0",
            "rsp": "0x0",
            "r8": "0x0",
            "r9": "0x0",
            "r10": "0x0",
            "r11": "0x0",
            "r12": "0x0",
            "r13": "0x0",
            "r14": "0x0",
            "r15": "0x0"
        }
        self.register_names = ["rax", "rcx", "rdx", "rbx", "rdi", "rsi",
                               "rbp", "rsp", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]
        self.interpreter_state = []
        self.variable_store = []
        self.stack = []

    def update_registers(self, to_update):
        if to_update:
            for (k, v) in to_update:
                if k in self.registers:
                    self.registers[k] = v

    def update_interpreter_state(self, to_update):
        if to_update:
            self.interpreter_state = to_update.copy()

    def update_variable_store(self, to_update):
        if to_update:
            self.variable_store = to_update.copy()

    def update_stack(self, to_update):
        if to_update != None:
            self.stack = list(reversed(to_update.copy()))

    def update(self, regs, interpreter, variables, stack):
        self.update_registers(regs)
        self.update_interpreter_state(interpreter)
        self.update_variable_store(variables)
        self.update_stack(stack)

    def get_reg(self, index):
        return (self.register_names[index], self.registers[self.register_names[index]])
