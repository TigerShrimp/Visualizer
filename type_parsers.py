import re


def pc_parse(valobj, internal_dict):
    method = valobj.GetChildMemberWithName('methodIndex').GetValue()
    inst = valobj.GetChildMemberWithName('instructionIndex').GetValue()
    return "({}, {})".format(method, inst)


def value_parse(valobj, internal_dict):
    t = valobj.GetChildMemberWithName(
        'type').GetChildMemberWithName('type').GetValue()
    if t == 'Int':
        val = valobj.GetChildMemberWithName(
            'val').GetChildMemberWithName('intValue').GetValue()
    elif t == 'Double':
        val = valobj.GetChildMemberWithName(
            'val').GetChildMemberWithName('doubleValue').GetValue()
    elif t == 'Long':
        val = valobj.GetChildMemberWithName(
            'val').GetChildMemberWithName('longValue').GetValue()
    elif t == 'Float':
        val = valobj.GetChildMemberWithName(
            'val').GetChildMemberWithName('floatValue').GetValue()
    else: 
        val = "Add parse for type {}".format(t) 
    return str(val)


def op_parse(valobj, internal_dict):
    opType = valobj.GetChildMemberWithName('opType').GetValue()
    if str(opType) == 'REGISTER':
        val = valobj.GetChildMemberWithName('reg').GetValue()
    elif str(opType) == 'MEMORY':
        mem = valobj.GetChildMemberWithName('mem')
        reg = mem.GetChildMemberWithName('reg').GetValue()
        offset = mem.GetChildMemberWithName('offset').GetValue()
        if offset != '0':
            val = '[{} + {}]'.format(reg, offset)
        else:
            val = '[{}]'.format(reg)
    elif str(opType) == 'LABEL':
        pc = valobj.GetChildMemberWithName('pc')
        inst = pc.GetChildMemberWithName('instructionIndex').GetValue()
        val = "label_{}".format(inst)
    elif str(opType) == 'IMMEDIATE':
        value = valobj.GetChildMemberWithName('val')
        val = value_parse(value, internal_dict)
    else:
        val = 'Something'
    return str(val)


def inst_parse(valobj, internal_dict):
    inst = valobj.GetChildMemberWithName('inst').GetValue()
    if inst == 'LABEL':
        op = op_parse(valobj.GetChildMemberWithName('op1'), internal_dict)
        val = "{}:".format(op)
    elif inst in ['LEAVE', 'RET']:
        val = str(inst)
    elif inst in [
            'PUSH', 'POP', 'INC', 'JMP', 'JE', 'JGE']:
        op = op_parse(valobj.GetChildMemberWithName('op1'), internal_dict)
        val = '{} {}'.format(inst, op)
    else:
        op1 = op_parse(valobj.GetChildMemberWithName('op1'), internal_dict)
        op2 = op_parse(valobj.GetChildMemberWithName('op2'), internal_dict)
        val = '{} {}, {}'.format(inst, op1, op2)
    return val


def byte_code_parse(valobj, internal_dict):
    param_regex = r'\[\d+\] = (-?[\d.]+)'
    mnemonic = valobj.GetChildMemberWithName('mnemonic').GetValue()
    params = str(valobj.GetChildMemberWithName('params'))
    matches = re.findall(param_regex, params)
    params_str = ''
    for match in matches:
        params_str += ' {}'.format(match)
    return '{}{}'.format(mnemonic, params_str)


def record_entry_parse(valobj, internal_dict):
    return byte_code_parse(valobj.GetChildMemberWithName('inst'), internal_dict)
