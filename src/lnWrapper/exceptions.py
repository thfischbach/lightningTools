class LnWrapperException(Exception):
    def __init__(self, msg):
        errorText = "LnWrapper: %s" % msg
        super(LnWrapperException, self).__init__(errorText)