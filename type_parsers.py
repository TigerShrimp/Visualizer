def value_parse(valobj, internal_dict):
  t = valobj.GetChildMemberWithName('type').GetChildMemberWithName('type').GetValue()
  if t == 'Int':
      val = valobj.GetChildMemberWithName('val').GetChildMemberWithName('intValue').GetValue()
  else:
      val = "ff"
  return str(val)


def op_parse (valobj, internal_dict):
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
    method = pc.GetChildMemberWithName('methodIndex').GetValue()
    inst = pc.GetChildMemberWithName('instructionIndex').GetValue()
    val = "({}, {})".format(method, inst)
  elif str(opType) == 'IMMEDIATE':
    value = valobj.GetChildMemberWithName('val')
    val = value_parse(value, internal_dict)
  else:
    val = 'Something'
  return 'Op: ' + str(val)
