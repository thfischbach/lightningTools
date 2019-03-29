class LnWrapperException(Exception):
    def __init__(self, msg):
        errorText = "%s" % msg
        super(LnWrapperException, self).__init__(errorText)
        
class LnWrapper_msatNotFoundException(LnWrapperException):
    def __init__(self, fieldName):
        msg = "msat field not found: %s" % fieldName
        super(LnWrapper_msatFoundException, self).__init__(msg)