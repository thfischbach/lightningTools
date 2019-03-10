from lightning import LightningRpc
from lnWrapper.exceptions import LnWrapperException

class LnWrapper:
    
    def __init__(self, rpcFile):
        self.rpcFile = rpcFile
        self.rpc = LightningRpc(rpcFile)
        self.__funds = None
        self.__peers = None
        self.__peersFiltered = None
        self.__forwards = None
    
    def getFunds(self, reload=False):
        if not self.__funds or reload:
            self.__funds = self.rpc.listfunds()
        return self.__funds
    
    def getPeers(self, peerId=None, reload=False):
        if peerId:
            if self.__peersFiltered and self.__peersFiltered["id"] == peerId:
                return self.__peersFiltered
            else:
                self.__peersFiltered = self.rpc.listpeers(peerId)["peers"]
                return self.__peersFiltered
        elif not self.__peers or reload:
            self.__peers = self.rpc.listpeers()["peers"]
        return self.__peers
    
    def getForwards(self, reload=False):
        if not self.__forwards or reload:
            self.__forwards = self.rpc.listforwards()["forwards"]
        return self.__forwards
    
    def msat(self, structure, fieldName):
        fullFieldName = fieldName + "_msat"
        valStr = structure[fullFieldName]
        msatInt = int(valStr)
        return msatInt

    def __has_msatField(self, structure, fieldName):
        return fieldName + "_msat" in structure
    
    
    def getFundOutputs(self):
        return self.getFunds()["outputs"]
    
    def getFundChannels(self):
        return self.getFunds()["channels"]
    
    def getFundChannelById(self, channelId):
        channels = self.getFundChannels()
        for c in channels:
            if c["short_channel_id"] == channelId:
                return c
        return None

    def getPeerById(self, id):
        return self.getPeers(id)
    
    def getPeerChannelsByPeerId(self, peerId):
        peer = self.getPeerById(peerId)
        return peer["channels"]
    
    def getPeerChannelByChannelId(self, channelId):
        peers = self.getPeers()
        for p in peers:
            for c in p["channels"]:
                if c["short_channel_id"] == channelId:
                    return c
        return None
    
    def getChannelTotalAmount(self, channel):
        if self.__has_msatField(channel, "amount"):
            return self.msat(channel, "amount")
        elif self.__has_msatField(channel, "total"):
            return self.msat(channel, "total")
        else:
            raise LnWrapper_msatFoundException("amount or total")
    
    def getChannelOurAmount(self, channel):
        if self.__has_msatField(channel, "our_amount"):
            return self.msat(channel, "our_amount")
        elif self.__has_msatField(channel, "to_us"):
            return self.msat(channel, "to_us")
        else:
            raise LnWrapper_msatFoundException("our_amount or to_us")
    
    def getChannelTheirAmount(self, channel):
        return self.getChannelTotalAmount(channel) - self.getChannelOurAmount(channel)
    
    def getChannelOurReserve(self, channel):
        if self.__has_msatField(channel, "our_reserve"):
            return self.msat(channel, "our_reserve")
        else:
            raise LnWrapper_msatFoundException("our_reserve")
    
    def getChannelTheirReserve(self, channel):
        if self.__has_msatField(channel, "their_reserve"):
            return self.msat(channel, "their_reserve")
        else:
            raise LnWrapper_msatFoundException("their_reserve")
