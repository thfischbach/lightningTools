#!/usr/bin/python3
import sys, argparse
from lnWrapper.lnWrapper import LnWrapper

parser = argparse.ArgumentParser(description="Lightning channel status")
parser.add_argument( "-r", "--rpcFile", dest="rpcFile", action="store", type=str, default="/home/lightning/.lightning/lightning-rpc", help="lightning RPC file")
parser.add_argument( "-o", "--outbound", dest="outbound", action="store", type=str, help="outbound short channel ID")
parser.add_argument( "-i", "--inbound", dest="inbound", action="store", type=str, help="inbound short channel ID")
parser.add_argument( "-a", "--amount", dest="amount", action="store", type=int, help="amount [mSat]")
parser.add_argument( "-R", "--riskfactor", dest="riskfactor", action="store", type=int, default=5, help="risk factor")
parser.add_argument( "-f", "--fuzzpercent", dest="fuzzpercent", action="store", type=float, default=5.0, help="fuzzing percentage [%]")

def checkBalance(ln, outboundChannel, inboundChannel, amount):
    print("Checking out- and inbound channel...")
    ourAmount = ln.getChannelOurAmount(outboundChannel)
    if ourAmount < amount:
        print("we do not have enought msat on the outbound side: have=%d, need=%d" % (ourAmount, amount))
        return False
    ourReserve = ln.getChannelOurReserve(outboundChannel)
    if ourReserve > ourAmount - amount:
        print("we would underrun our reserve on the outbound side: reserve=%d, underrun=%d" % (ourReserve, ourAmount - amount))
        return False
    theirAmount = ln.getChannelTheirAmount(inboundChannel)
    if theirAmount < amount:
        print("they do not have enought msat on the inbound side: have=%d, need=%d" % (theirAmount, amount))
        return False
        ourReserve = ln.getChannelOurReserve(outboundChannel)
    theirReserve = ln.getChannelTheirReserve(inboundChannel)
    if theirReserve > theirAmount - amount:
        print("they would underrun their reserve on the inbound side: reserve=%d, underrun=%d" % (theirReserve, theirAmount - amount))
        return False
    print("Should be working:")
    print("our outbound amount: %d" % ourAmount)
    print("our outbound reserve: %d" % ourReserve)
    print("their inbound amount: %d" % theirAmount)
    print("their inbound reserve: %d" % theirReserve)
    return True

def getMidRoute(inboundNodeId, outboundNodeId, amount, riskfactor, fuzzpercent, myId):
    tries = 10
    for i in range(tries):
        route = ln.getRoute(toPeer=inboundNodeId, amount=amount, riskfactor=riskfactor, fuzzpercent=fuzzpercent, fromPeer=outboundNodeId)
        for r in route:
            if r["id"] == myId:
                continue
        return route
    print("no route found after %d tries" % tries)
    return None

args = parser.parse_args()
rpcFile = args.rpcFile
outboundChannelId = args.outbound
inboundChannelId = args.inbound
amount = args.amount
riskfactor = args.riskfactor
fuzzpercent = args.fuzzpercent
ln = LnWrapper(rpcFile)

myId = ln.getMyId()

outboundChannel = ln.getPeerChannelByChannelId(outboundChannelId)
inboundChannel = ln.getPeerChannelByChannelId(inboundChannelId)
ok = checkBalance(ln, outboundChannel, inboundChannel, amount)

outboundNodeId = ln.getPeerIdByChannelId(outboundChannelId)
inboundNodeId = ln.getPeerIdByChannelId(inboundChannelId)

if not ok:
    sys.exit(1)

print("Creating invoice...")
invoice = ln.invoice(amount)
payment_hash = invoice["payment_hash"]
print("payment hash: %s" % payment_hash)

routeMid = getMidRoute(inboundNodeId, outboundNodeId, amount, riskfactor, fuzzpercent, myId)
if not routeMid:
    sys.exit(1)

routeOut = {"id": outboundNodeId}
routeOut["channel"] = outboundChannelId
routeIn = {"id": myId}
routeIn["channel"] = inboundChannelId

route = [routeOut] + routeMid + [routeIn]
ln.adaptRouteFees(route, amount)
print("Found route:")
for r in route:
    print("  -> via channel %s to node %s, amount=%d" % (r["channel"], r["id"], ln.get_msat(r, "amount")))
print("Fees: %d" % (ln.get_msat(route[0], "amount") - ln.get_msat(route[-1], "amount")))

print("Pay...")
ret = ln.sendPay(route, payment_hash)
print("status=%s" % ret["status"])
print("Wait for payment...")
ret = ln.waitSendPay(payment_hash)
if ret:
    print("status=%s" % ret["status"])
else:
    print("Failed!")
