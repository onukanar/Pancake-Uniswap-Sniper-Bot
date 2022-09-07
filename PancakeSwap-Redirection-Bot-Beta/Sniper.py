import requests
from txns import TXN
import argparse, json
from time import sleep
from halo import Halo
from style import style

/"
ascii = """    
"""

parser = argparse.ArgumentParser(description='Set your Token and Amount example: "sniper.py -t 0x34faa80fec0233e045ed4737cc152a71e490e2e3 -a 0.2 -s 15"')
parser.add_argument('-t', '--token', help='str, Token for snipe e.g. "-t 0x34faa80fec0233e045ed4737cc152a71e490e2e3"')
parser.add_argument('-a', '--amount',default=0, help='float, Amount in Bnb to snipe e.g. "-a 0.1"')
parser.add_argument('-tx', '--txamount', default=1, nargs="?", const=1, type=int, help='int, how mutch tx you want to send? It Split your BNB Amount in e.g. "-tx 5"')
parser.add_argument('-hp', '--honeypot', action="store_true", help='Check if your token to buy is a Honeypot, e.g. "-hp" or "--honeypot"')
parser.add_argument('-nb', '--nobuy', action="store_true", help='No Buy, Skipp buy, if you want to use only TakeProfit/StopLoss/TrailingStopLoss')
parser.add_argument('-tp', '--takeprofit', default=0, nargs="?", const=True, type=int, help='int, Percentage TakeProfit from your input BNB amount "-tp 50" ')
parser.add_argument('-sl', '--stoploss', default=0, nargs="?", const=True, type=int, help='int, Percentage Stop loss from your input BNB amount "-sl 50" ')
parser.add_argument('-tsl', '--trailingstoploss', default=0, nargs="?", const=True, type=int, help='int, Percentage Trailing-Stop-loss from your first Quote "-tsl 50" ')
parser.add_argument('-wb', '--awaitBlocks', default=0, nargs="?", const=True, type=int, help='int, Await Blocks before sending BUY Transaction "-ab 50" ')
parser.add_argument('-cmt', '--checkMaxTax',  action="store_true", help='get Token Tax and check if its higher.')
parser.add_argument('-cc', '--checkcontract',  action="store_true", help='Check is Contract Verified and Look for some Functions.')
parser.add_argument('-so', '--sellonly',  action="store_true", help='Sell all your Tokens from given address')
parser.add_argument('-bo', '--buyonly',  action="store_true", help='Buy Tokens with from your given amount')
parser.add_argument('-cl', '--checkliquidity',  action="store_true", help='with this arg you use liquidityCheck')
parser.add_argument('-dsec', '--DisabledSwapEnabledCheck',  action="store_true", help='this argument disabled the SwapEnabled Check!')
args = parser.parse_args()


class SniperBot():
    
    def __init__(self):
        self.parseArgs()
        self.settings = self.loadSettings()
        self.SayWelcome()
    
    def loadSettings(self):
        with open("Settings.json","r") as settings:
            settings = json.load(settings)
        return settings

    def SayWelcome(self):
        print(style().YELLOW + ascii+ style().RESET)
        print(style().GREEN +"""Attention, You pay a 0.77% Tax on your swap amount!"""+ style().RESET)
        print(style().GREEN +"Start Sniper Tool with following arguments:"+ style().RESET)
        print(style().BLUE + "---------------------------------"+ style().RESET)
        print(style().YELLOW + "Amount for Buy:",style().GREEN + str(self.amount) + " BNB"+ style().RESET)
        print(style().YELLOW + "Token to Interact :",style().GREEN + str(self.token) + style().RESET)
        print(style().YELLOW + "Transaction to send:",style().GREEN + str(self.tx)+ style().RESET)
        print(style().YELLOW + "Amount per transaction :",style().GREEN + str("{0:.8f}".format(self.amountForSnipe))+ style().RESET)
        print(style().YELLOW + "Await Blocks before buy :",style().GREEN + str(self.wb)+ style().RESET)
        if self.tsl != 0:
            print(style().YELLOW + "Trailing Stop loss Percent :",style().GREEN + str(self.tsl)+ style().RESET)
        if self.tp != 0:
            print(style().YELLOW + "Take Profit Percent :",style().GREEN + str(self.tp)+ style().RESET)
        if self.sl != 0:
            print(style().YELLOW + "Stop loss Percent :",style().GREEN + str(self.sl)+ style().RESET)
        print(style().BLUE + "---------------------------------"+ style().RESET)
        
    import screen
    def parseArgs(self):
        self.token = args.token
        if self.token == None:
            print(style.RED+"Please Check your Token argument e.g. -t 0x34faa80fec0233e045ed4737cc152a71e490e2e3")
            print("exit!")
            raise SystemExit

        self.amount = args.amount
        if args.nobuy != True:  
            if not args.sellonly: 
                if self.amount == 0:
                    print(style.RED+"Please Check your Amount argument e.g. -a 0.01")
                    print("exit!")
                    raise SystemExit

        self.tx = args.txamount
        self.amountForSnipe = float(self.amount) / float(self.tx)
        self.hp = args.honeypot
        self.wb = args.awaitBlocks
        self.tp = args.takeprofit
        self.sl = args.stoploss 
        self.tsl = args.trailingstoploss
        self.cl = args.checkliquidity
        self.stoploss = 0
        self.takeProfitOutput = 0


    def calcProfit(self):
        if self.amountForSnipe == 0.0:
            self.amountForSnipe = self.TXN.getOutputfromTokentoBNB()[0] / (10**18)
        a = ((self.amountForSnipe * self.tx) * self.tp) / 100
        b = a + (self.amountForSnipe * self.tx)
        return b 
    

    def calcloss(self):
        if self.amountForSnipe == 0.0:
            self.amountForSnipe = self.TXN.getOutputfromTokentoBNB()[0] / (10**18)
        a = ((self.amountForSnipe * self.tx) * self.sl) / 100
        b = (self.amountForSnipe * self.tx) - a
        return b 


    def calcNewTrailingStop(self, currentPrice):
        a = (currentPrice  * self.tsl) / 100
        b = currentPrice - a
        return b

    def awaitBuy(self):
        spinner = Halo(text='await Buy', spinner='dots')
        spinner.start()
        for i in range(self.tx):
            spinner.start()
            self.TXN = TXN(self.token, self.amountForSnipe)
            tx = self.TXN.buy_token()
            spinner.stop()
            print(tx[1])
            if tx[0] != True:
                raise SystemExit

    def awaitSell(self):
        spinner = Halo(text='await Sell', spinner='dots')
        spinner.start()
        self.TXN = TXN(self.token, self.amountForSnipe)
        tx = self.TXN.sell_tokens()
        spinner.stop()
        print(tx[1])
        if tx[0] != True:
            raise SystemExit 

    def awaitApprove(self):
        spinner = Halo(text='await Approve', spinner='dots')
        spinner.start()
        self.TXN = TXN(self.token, self.amountForSnipe)
        tx = self.TXN.approve()
        spinner.stop()
        print(tx[1])
        if tx[0] != True:
            raise SystemExit 

    def awaitBlocks(self):
        spinner = Halo(text='await Blocks', spinner='dots')
        spinner.start()
        waitForBlock = self.TXN.getBlockHigh() + self.wb
        while True:
            sleep(0.13)
            if self.TXN.getBlockHigh() > waitForBlock:
                spinner.stop()
                break
        print(style().GREEN+"[DONE] Wait Blocks finish!")
        

    def CheckVerifyCode(self):
        while True:
            req = requests.get(f"https://api.bscscan.com/api?module=contract&action=getsourcecode&address={self.token}&apikey=YourApiKeyToken")
            if req.status_code == 200:
                getsourcecode = req.text.lower()
                jsonSource = json.loads(getsourcecode)
                if not "MAX RATE LIMIT REACHED".lower() in str(jsonSource["result"]).lower():
                    if not "NOT VERIFIED".lower() in str(jsonSource["result"]).lower():
                        print("[CheckContract] IS Verfied")
                        for BlackWord in self.settings["cc_BlacklistWords"]:
                            if BlackWord.lower() in getsourcecode:
                                print(style().RED+f"[CheckContract] BlackWord {BlackWord} FOUND, Exit!")
                                raise SystemExit
                        print(style().GREEN+"[CheckContract] No known abnormalities found.")
                        break
                    else:
                        print(style().RED+"[CheckContract] Code Not Verfied, Can't check, Exit!")
                        raise SystemExit
                else:
                    print("Max Request Rate Reached, Sleep 5sec.")
                    sleep(5)
                    continue
            else:
                print("BSCScan.org Request Faild, Exiting.")
                raise SystemExit


    def awaitLiquidity(self):
        spinner = Halo(text='await Liquidity', spinner='dots')
        spinner.start()
        while True:
            sleep(0.07)
            try:
                self.TXN.getOutputfromBNBtoToken()[0]
                spinner.stop()
                break
            except Exception as e:
                if "UPDATE" in str(e):
                    print(e)
                    raise SystemExit
                continue
        print(style().GREEN+"[DONE] Liquidity is Added!"+ style().RESET)

    def fetchLiquidity(self):
        liq = self.TXN.getLiquidityBNB()[1]
        print(style().GREEN+"[LIQUIDTY] Current Token Liquidity:",round(liq,3),"BNB"+ style().RESET)
        if float(liq) < float(self.settings["MinLiquidityBNB"]):
            print(style.RED+"[LIQUIDTY] <- TO SMALL, EXIT!")
            raise SystemExit
        return True

    def awaitEnabledBuy(self):
        spinner = Halo(text='await Dev Enables Swapping', spinner='dots')
        spinner.start()
        while True:
            sleep(0.07)
            try:
                if self.TXN.checkifTokenBuyDisabled() == True:
                    spinner.stop()
                    break
            except Exception as e:
                if "UPDATE" in str(e):
                    print(e)
                    raise SystemExit
                continue
        print(style().GREEN+"[DONE] Swapping is Enabeld!"+ style().RESET)
    

    def awaitMangePosition(self):
        highestLastPrice = 0
        if self.tp != 0:
            self.takeProfitOutput = self.calcProfit()
        if self.sl != 0:
            self.stoploss = self.calcloss()
        TokenBalance = round(self.TXN.get_token_balance(),5)
        time = 300
        while time:
            try:
                sleep(0.9)
                LastPrice = float(self.TXN.getOutputfromTokentoBNB()[0] / (10**18))
                if self.tsl != 0:
                    if LastPrice > highestLastPrice:
                        highestLastPrice = LastPrice
                        TrailingStopLoss = self.calcNewTrailingStop(LastPrice)
                    if LastPrice < TrailingStopLoss:
                        print(style().GREEN+"[TRAILING STOP LOSS] Triggert!"+ style().RESET)
                        self.awaitSell()
                        break

                if self.takeProfitOutput != 0:
                    if LastPrice >= self.takeProfitOutput:
                        print()
                        print(style().GREEN+"[TAKE PROFIT] Triggert!"+ style().RESET)
                        self.awaitSell()
                        break

                if self.stoploss != 0:
                    if LastPrice <= self.stoploss:
                        print()
                        print(style().GREEN+"[STOP LOSS] Triggert!"+ style().RESET)
                        self.awaitSell()
                        break
                    
                msg = str("Token Balance: " + str("{0:.5f}".format(TokenBalance)) + "| CurrentOutput: "+str("{0:.7f}".format(LastPrice))+"BNB")
                if self.stoploss != 0:
                    msg = msg + "| Stop loss below: " + str("{0:.7f}".format(self.stoploss)) + "BNB"
                if self.takeProfitOutput != 0:
                    msg = msg + "| Take Profit Over: " + str("{0:.7f}".format(self.takeProfitOutput)) + "BNB"
                if self.tsl != 0:  
                    msg = msg + "| Trailing Stop loss below: " + str("{0:.7f}".format(TrailingStopLoss)) + "BNB"
                print(msg, end="\r")
                
            except Exception as e:
                print(e)
                sleep(5)

        print(style().GREEN+"[DONE] Position Manager Finished!"+ style().RESET)


    def StartUP(self):
        self.TXN = TXN(self.token, self.amountForSnipe)

        if args.sellonly:
            print("Start SellOnly, Selling Now all tokens!")
            inp = input("please confirm y/n\n")
            if inp.lower() == "y": 
                print("Wait for Liquidity?")
                liqq = input("please confirm y/n\n")
                if liqq.lower() == "y":
                    self.awaitEnabledBuy()
                print(self.TXN.sell_tokens()[1])
                raise SystemExit
            else:
                raise SystemExit

        if args.buyonly:
            print(f"Start BuyOnly, buy now with {self.amountForSnipe}BNB tokens!")
            print(self.TXN.buy_token()[1])
            raise SystemExit

        if args.nobuy != True:
            self.awaitLiquidity()
            if args.DisabledSwapEnabledCheck != True:
                self.awaitEnabledBuy()

        if args.checkcontract:
            self.CheckVerifyCode()

        honeyTax = self.TXN.checkToken()
        if self.hp == True:
            print(style().YELLOW +"Checking Token..." + style().RESET)
            if honeyTax[2] == True:
                print(style.RED + "Token is Honeypot, exiting")
                raise SystemExit
            elif honeyTax[2] == False:
                print(style().GREEN +"[DONE] Token is NOT a Honeypot!" + style().RESET)

        if args.checkMaxTax == True:
            if honeyTax[1] > self.settings["MaxSellTax"]:
                print(style().RED+"Token SellTax exceeds Settings.json, exiting!")
                raise SystemExit
            if honeyTax[0] > self.settings["MaxBuyTax"]:
                print(style().RED+"Token BuyTax exceeds Settings.json, exiting!")
                raise SystemExit

        if self.wb != 0: 
            self.awaitBlocks()

        if self.cl == True:
            if self.fetchLiquidity() != False:
                pass
            
        if args.nobuy != True:
            self.awaitBuy()

        sleep(7) # Give the RPC/WS some time to Index your address nonce, make it higher if " ValueError: {'code': -32000, 'message': 'nonce too low'} "
        self.awaitApprove()

        if self.tsl != 0 or self.tp != 0 or self.sl != 0:
            self.awaitMangePosition()

    print(style().GREEN + "[DONE] TradingTigers Sniper Bot finish!" + style().RESET)

SniperBot().StartUP()
