import datetime
import time
import requests
import json
import operator
import boto3

API = "https://api.warframe.market/v1/items"
itemsNames = {}
itemsOrdersingame = {}
itemsOrdersingame["sell"] = {}
itemsOrdersingame["buy"] = {}
itemsOrderstopTen = {}
itemsOrderstopTen["sell"] = {}
itemsOrderstopTen["buy"] = {}
itemsOrderscheapest = {}
itemsOrderscheapest["sell"] = {}
itemsOrderscheapest["buy"] = {}
itemsOrdersaverage = {}
itemsOrdersaverage["sell"] = {}
itemsOrdersaverage["buy"] = {}
itemsDucat = {}
ducatPlatledgerUnsorted = {}
ducatPlatledgerSorted = []


def importNamesandDucats():
    imported = requests.get(
        "https://s3.us-east-2.amazonaws.com/www.jsourdough.com/ItemsAndDucats.json"
    ).json()
    global itemsNames
    global itemsDucat
    itemsNames = imported["itemsNames"]
    itemsDucat = imported["itemsDucat"]


def updateItemplat(itemName):
    global itemsOrdersingame
    global itemsOrderstopTen
    global itemsOrderscheapest
    global itemsOrdersaverage
    itemRaw = {}
    itemRaw = requests.get(API + "/" + itemsNames[itemName] + "/orders").json()["payload"]["orders"]
    itemsOrdersingame["sell"][itemName] = {}
    itemsOrdersingame["buy"][itemName] = {}
    for i, tk in enumerate(itemRaw):
        if itemRaw[i]["user"]["status"] == "ingame":
            if itemRaw[i]["order_type"] == "sell":
                itemsOrdersingame["sell"][itemName][itemRaw[i]["user"]["ingame_name"]] = itemRaw[i][
                    "platinum"
                ]
            elif itemRaw[i]["order_type"] == "buy":
                itemsOrdersingame["buy"][itemName][itemRaw[i]["user"]["ingame_name"]] = itemRaw[i][
                    "platinum"
                ]
    #### Sell
    if itemsOrdersingame["sell"][itemName] == {}:
        itemsOrdersingame["sell"][itemName] = {"No sellers": 0}
    itemsOrderstopTen["sell"][itemName] = []
    itemsOrderstopTen["sell"][itemName] = sorted(
        itemsOrdersingame["sell"][itemName].items(), key=operator.itemgetter(1)
    )
    while len(itemsOrderstopTen["sell"][itemName]) >= 11:
        itemsOrderstopTen["sell"][itemName].pop()
    itemsOrderscheapest["sell"][itemName] = itemsOrderstopTen["sell"][itemName][0]
    average = 0
    for i, tk in enumerate(itemsOrderstopTen["sell"][itemName]):
        average += itemsOrderstopTen["sell"][itemName][i][1]
        itemsOrdersaverage["sell"][itemName] = average / len(itemsOrderstopTen["sell"][itemName])
    #### Buy
    if itemsOrdersingame["buy"][itemName] == {}:
        itemsOrdersingame["buy"][itemName] = {"No buyers": 0}
    itemsOrderstopTen["buy"][itemName] = []
    itemsOrderstopTen["buy"][itemName] = sorted(
        itemsOrdersingame["buy"][itemName].items(), key=operator.itemgetter(1)
    )
    itemsOrderstopTen["buy"][itemName].reverse()
    while len(itemsOrderstopTen["buy"][itemName]) >= 11:
        itemsOrderstopTen["buy"][itemName].pop()
    itemsOrderscheapest["buy"][itemName] = itemsOrderstopTen["buy"][itemName][0]
    average = 0
    for i, tk in enumerate(itemsOrderstopTen["buy"][itemName]):
        average += itemsOrderstopTen["buy"][itemName][i][1]
        itemsOrdersaverage["buy"][itemName] = average / len(itemsOrderstopTen["buy"][itemName])
    itemsOrdersingame["sell"].pop(itemName)
    itemsOrdersingame["buy"].pop(itemName)


def platCheck():
    iteration = 0
    for k, tv in itemsNames.items():
        start_time = time.time()
        updateItemplat(k)
        iteration += 1
        if (time.time() - start_time) <= 0.34:
            sleep = 0.34 - (time.time() - start_time)
            if sleep < 0.01:
                sleep = 0.01
            time.sleep(sleep)
        print("[{}/{}]".format(iteration, len(itemsNames.items())))
    itemsOrdersraw = {}


def ducatPlatefficency(itemName):
    try:
        return itemsDucat[itemName] / itemsOrderscheapest["sell"][itemName][1]
    except ZeroDivisionError:
        return 0
    except KeyError:
        return "No ducat value listed on Warframe.Market, please notify Warframe.Market"


def bestDucatplatEfficencycalc():
    global ducatPlatledgerUnsorted
    global ducatPlatledgerSorted
    for k, v in itemsNames.items():
        add = ducatPlatefficency(k)
        if add != "No ducat value listed on Warframe.Market, please notify Warframe.Market":
            ducatPlatledgerUnsorted[k] = add
        ducatPlatledgerSorted = sorted(ducatPlatledgerUnsorted.items(), key=operator.itemgetter(1))
    ducatPlatledgerUnsorted = {}


def bestDucatplatEfficencytxt(count):
    global itemsOrderscheapest
    global itemsDucat
    global ducatPlatledgerSorted
    bestDucatplatEfficencytxtList = []
    for i in range(1, count + 1):
        bestDucatplatEfficencytxtList.append(
            "Item: "
            + str(ducatPlatledgerSorted[-i][0])
            + "\nSeller: '"
            + itemsOrderscheapest["sell"][ducatPlatledgerSorted[-i][0]][0]
            + "' "
            + str(itemsOrderscheapest["sell"][ducatPlatledgerSorted[-i][0]][1])
            + " Plat"
            + "\nDucats: "
            + str(itemsDucat[ducatPlatledgerSorted[-i][0]])
            + "\nCurrent ducat/plat efficency: "
            + str(ducatPlatledgerSorted[-i][1])
            + "\n"
        )
    return str(datetime.datetime.now()) + "\n\n" + "\n".join(bestDucatplatEfficencytxtList)


def lambda_handler(event, context):
    print("Started plat and efficency checks", datetime.datetime.now())
    importNamesandDucats()
    print("Finished name and ducat import", datetime.datetime.now())
    platCheck()
    print("Finished plat check", datetime.datetime.now())
    bestDucatplatEfficencycalc()
    print("Finished efficency check", datetime.datetime.now())
    toClient = {
        "itemsNames": itemsNames,
        "itemsOrderstopTen": itemsOrderstopTen,
        "itemsOrderscheapest": itemsOrderscheapest,
        "itemsOrdersaverage": itemsOrdersaverage,
        "itemsDucat": itemsDucat,
        "ducatPlatledgerSorted": ducatPlatledgerSorted,
    }
    client = boto3.client("s3")
    client.delete_objects(
        Bucket="www.jsourdough.com", Delete={"Objects": [{"Key": "ImportantInfo.json"}]}
    )
    client.put_object(
        Bucket="www.jsourdough.com",
        Key="ImportantInfo.json",
        Body=json.dumps(toClient, indent=4),
        ContentType="text/plain",
    )
    client.delete_objects(
        Bucket="www.jsourdough.com", Delete={"Objects": [{"Key": "bestDucatplatEfficency.txt"}]}
    )
    client.put_object(
        Bucket="www.jsourdough.com",
        Key="bestDucatplatEfficency.txt",
        Body=bestDucatplatEfficencytxt(5),
        ContentType="text/plain",
    )
    print("Pages Updated", datetime.datetime.now())
