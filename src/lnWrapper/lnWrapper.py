from lightning import LightningRpc
from lnWrapper.exceptions import LnWrapperException

class LnWrapper:
    
    def __init__(self, rpcFile):
        self.rpcFile = rpcFile
        self.rpc = LightningRpc(rpcFile)
        self.__funds = None
        self.__peers = None
        self.__forwards = None
    
    def getFunds(self, reload=False):
        if not self.__funds or reload:
            self.__funds = self.rpc.listfunds()
        return self.__funds
    
    def getPeers(self, reload=False):
        if not self.__peers or reload:
            self.__peers = self.rpc.listpeers()
        return self.__peers
    
    def getForwards(self, reload=False):
        if not self.__forwards or reload:
            self.__forwards = self.rpc.listforwards()["forwards"]
        return self.__forwards
        
    def getFundOutputs(self):
        return self.getFunds()["outputs"]
    
    def getFundChannels(self):
        return self.getFunds()["channels"]

    def getPeerById(self, id):
        return self.getPeers(id)
    
    def getChannelsByPeerId(self, id):
        peers = getPeerById
    
    def getChannelTotalAmount(self, channel):
        if self.__has_msatField(channel, "amount"):
            return self.msat(channel, "amount")
        elif self.__has_msatField(channel, "total"):
            return self.msat(channel, "total")
        else:
            raise LnWrapperException("argument has no total amount")
    
    def getChannelOurAmount(self, channel):
        if self.__has_msatField(channel, "our_amount"):
            return self.msat(channel, "our_amount")
        elif self.__has_msatField(channel, "to_us"):
            return self.msat(channel, "to_us")
        else:
            raise LnWrapperException("argument has no our amount")
    
    def getChannelTheirAmount(self, channel):
        return self.getChannelTotalAmount(channel) - self.getChannelOurAmount(channel)
    
    def msat(self, structure, fieldName):
        fullFieldName = fieldName + "_msat"
        valStr = structure[fullFieldName]
        msatInt = int(valStr)
        return msatInt

    def __has_msatField(self, structure, fieldName):
        return fieldName + "_msat" in structure
