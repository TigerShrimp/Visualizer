from constants import CompilerState

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
        self.pc = None
        self.variable_store = []
        self.loop_record = []
        self.stack = []
        self.recording = []
        self.native_trace = []
        self.record_record = set()
        self.compiler_state = CompilerState.INTERPRETING

    def set_methods(self, methods):
        self.methods = methods

    def update_registers(self, to_update):
        if to_update:
            for (k, v) in to_update:
                if k in self.registers:
                    self.registers[k] = v

    def update_pc(self, to_update):
        if to_update:
            self.pc = to_update

    def update_loop_record(self, to_update):
        if to_update:
            self.loop_record = to_update.copy()

    def update_variable_store(self, to_update):
        if to_update:
            self.variable_store = to_update.copy()

    def update_stack(self, to_update):
        if to_update != None:
            self.stack = list(reversed(to_update.copy()))
        
    def update_recording(self, to_update):
        if to_update:
            self.recording = to_update.copy()

    def update_trace(self, to_update):
        if to_update:
            self.native_trace = to_update.copy()

    def update(self, regs, pc, record, variables, stack, recording, trace):
        self.update_registers(regs)
        self.update_pc(pc)
        self.update_loop_record(record)
        self.update_variable_store(variables)
        self.update_stack(stack)
        self.update_recording(recording)
        self.update_trace(trace)

    def get_reg(self, index):
        return (self.register_names[index], self.registers[self.register_names[index]]) if self.register_names[index] else None
