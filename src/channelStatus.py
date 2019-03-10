#!/usr/bin/python3
import sys, argparse
from lnWrapper.lnWrapper import LnWrapper

parser = argparse.ArgumentParser(description="Lightning channel status")
parser.add_argument( "-r", "--rpcPath", dest="rpcPath", action="store", default="/home/lightning/.lightning/lightning-rpc", type=str, help="path to lightning RPC")
parser.add_argument( "-m", "--more", dest="more", action="store_true", default=False, help="more information about peers")

args = parser.parse_args()
rpcPath = args.rpcPath
more = args.more

ln = LnWrapper(rpcPath)

peers = ln.getPeers()
forwards = ln.getForwards()
totalOutputValue = 0    
totalChChars = 20

for o in ln.getFundOutputs():
    totalOutputValue += o["value"]
print("all amounts in mSat")
print("Outputs total value: %d" % (totalOutputValue*1000))
print
header = "ChanId            ourEnd"
header += " "*(totalChChars+17)
header += "theirEnd     FwdIn(Cnt)    FwdOut(Cnt)"
if not more:
    print(header)

for p in peers["peers"]:
    if more:
        print()
        print("ID: %s" % p["id"])
        connected = p["connected"]
        if connected:
            conStr = "connected - "
            for a in p["netaddr"]:
                conStr += "%s, " % a
            conStr = conStr[:-2]
        else:
            conStr = "not connected"
        print(conStr)
        if len(p["channels"]) > 0:
            print(header)
    for c in p["channels"]:
        space = 10
        channelId = c["short_channel_id"]
        fwdCountIn = 0
        fwdCountOut = 0
        fwdTotalIn = 0
        fwdTotalOut = 0
        for fwd in forwards:
            if fwd["status"] == "settled":
                if channelId == fwd["in_channel"]:
                    fwdCountIn += 1
                    fwdTotalIn += fwd["in_msatoshi"]
                if channelId == fwd["out_channel"]:
                    fwdCountOut += 1
                    fwdTotalOut += fwd["out_msatoshi"]
        total = ln.getChannelTotalAmount(c)
        ourEnd = ln.getChannelOurAmount(c)
        theirEnd = ln.getChannelTheirAmount(c)
        ourEndRel = float(ourEnd)/float(total)
        theirEndRel = float(theirEnd)/float(total)
        channelName = c["short_channel_id"].ljust(12)
        statusString = "%s %11d [" % (channelName, ourEnd)
        ourEndChars = int(totalChChars * ourEndRel)
        theirEndChars = int(totalChChars * theirEndRel)
        space += totalChChars - ourEndChars - theirEndChars
        statusString += "#"*ourEndChars
        statusString += "-"*space
        statusString += "#"*theirEndChars
        statusString += "] %11d %9d(%3d) %9d(%3d)" % (theirEnd, fwdTotalIn, fwdCountIn, fwdTotalOut, fwdCountOut)
        print(statusString)
        if more:
            for stat in c["status"]:
                print("\t" + stat)
