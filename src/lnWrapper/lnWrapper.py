def msat(structure, fieldName):
    fullFieldName = fieldName + "_msat"
    valStr = structure[fullFieldName]
    msatInt = int(valStr)
    return msatInt