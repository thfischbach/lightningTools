from lightning import LightningRpc
from lightning.lightning import RpcError
from lnWrapper.exceptions import LnWrapperException
from time import time

class LnWrapper:
    
    def __init__(self, rpcFile):
        self.rpcFile = rpcFile
        self.rpc = LightningRpc(rpcFile)
        self.__funds = None
        self.__peers = None
        self.__peersFiltered = None
        self.__channels = None
        self.__channelsFiltered = None
        self.__forwards = None
        self.__info = None
    
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
    
    def getChannels(self, channelId=None, reload=False):
        if channelId:
            if self.__channelsFiltered and self.__channelsFiltered[0]["short_channel_id"] == channelId and self.__channelsFiltered[1]["short_channel_id"] == channelId:
                return self.__channelsFiltered
            else:
                self.__channelsFiltered = self.rpc.listchannels(channelId)["channels"]
                return self.__channelsFiltered
        elif not self.__channels or reload:
            self.__channels = self.rpc.listchannels()["channels"]
        return self.__channels
    
    def getInfo(self, reload=False):
        if not self.__info or reload:
            self.__info = self.rpc.getinfo()
        return self.__info
    
    def getMyId(self):
        return self.getInfo()["id"]
    
    def getRoute(self, toPeer, amount, riskfactor=None, fuzzpercent=None, fromPeer=None):
        route = self.rpc.getroute(toPeer, amount, riskfactor=riskfactor, fuzzpercent=fuzzpercent, cltv=9, fromid=fromPeer)
        return route["route"]
    
    def invoice(self, amount, label=None, description=None):
        if not label:
            label = str(time())
        if not description:
            description = label
        return self.rpc.invoice(amount, label, description)
    
    def sendPay(self, route, payment_hash):
        return self.rpc.sendpay(route, payment_hash)
    
    def waitSendPay(self, payment_hash):
        return self.__rpcCall(self.rpc.waitsendpay, payment_hash)
    
    def get_msat(self, structure, fieldName):
        fullFieldName = fieldName + "_msat"
        valStr = structure[fullFieldName]
        if type(valStr) == str:
            msatInt = int(valStr[:-4])
        else:
            msatInt = int(valStr)
        return msatInt
    
    def set_msat(self, structure, fieldName, value):
        fullFieldName = fieldName + "_msat"
        structure[fullFieldName] = str(value) + "msat"

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
    
    def getChannelByChannelId(self, channelId):
        return self.getChannels(channelId)
    
    def getPeerIdByChannelId(self, channelId):
        c = self.getFundChannelById(channelId)
        return c["peer_id"]
    
    def getChannelTotalAmount(self, channel):
        if self.__has_msatField(channel, "amount"):
            return self.get_msat(channel, "amount")
        elif self.__has_msatField(channel, "total"):
            return self.get_msat(channel, "total")
        else:
            raise LnWrapper_msatNotFoundException("amount or total")
    
    def getChannelOurAmount(self, channel):
        if self.__has_msatField(channel, "our_amount"):
            return self.get_msat(channel, "our_amount")
        elif self.__has_msatField(channel, "to_us"):
            return self.get_msat(channel, "to_us")
        else:
            raise LnWrapper_msatNotFoundException("our_amount or to_us")
    
    def getChannelTheirAmount(self, channel):
        return self.getChannelTotalAmount(channel) - self.getChannelOurAmount(channel)
    
    def getChannelOurReserve(self, channel):
        if self.__has_msatField(channel, "our_reserve"):
            return self.get_msat(channel, "our_reserve")
        else:
            raise LnWrapper_msatNotFoundException("our_reserve")
    
    def getChannelTheirReserve(self, channel):
        if self.__has_msatField(channel, "their_reserve"):
            return self.get_msat(channel, "their_reserve")
        else:
            raise LnWrapper_msatNotFoundException("their_reserve")
    
    def adaptRouteFees(self, route, amount):
        delay=9
        for r in reversed(route):
            self.set_msat(r, "amount", amount)
            r["msatoshi"] = amount
            r["delay"] = delay
            channel = self.getChannels(r["channel"])
            for side in channel:
                if side["destination"] == r["id"]:
                    fee = side["base_fee_millisatoshi"]
                    fee += amount * side["fee_per_millionth"] / 1000000
                    amount += int(fee)
                    delay += side["delay"]
    
    def __rpcCall(self, rpcFunc, *args):
        try:
            return rpcFunc(*args)
        except RpcError as e:
            print("RpcError: %s" % str(e))
            return None
