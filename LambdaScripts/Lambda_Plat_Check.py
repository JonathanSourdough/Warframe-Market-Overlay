import datetime
import time
import requests
import json
import operator
import boto3

API = "https://api.warframe.market/v1/items"


def importNamesandDucats():
    imported = requests.get(
        "https://s3.us-east-2.amazonaws.com/www.jsourdough.com/ItemsAndDucats.json"
    ).json()
    itemsNames = imported["itemsNames"]
    itemsDucat = imported["itemsDucat"]
    return itemsNames, itemsDucat


def updateItemplat(
    itemName,
    itemsNames,
    itemsDucat,
    itemsOrderstopTen,
    itemsOrderscheapest,
    itemsOrdersaverage,
    playerListings,
):
    itemsOrdersingame = {"sell": {}, "buy": {}}
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
    # player listings
    for k, v in itemsOrdersingame["sell"][itemName].items():
        if not k in playerListings:
            playerListings[k] = {
                "playerName": k,
                "playerPlat": 0,
                "playerDucats": 0,
                "playerEfficency": 0,
                "unorderedItems": [],
                "orderedItems": [],
            }
        for v2 in playerListings[k]["unorderedItems"]:
            if itemName in v2:
                if v2["platinum"] < v:
                    continue
        try:
            playerListings[k]["unorderedItems"].append(
                {"platinum": v, "itemName": itemName, "ducats": itemsDucat[itemName]}
            )
        except KeyError:
            playerListings[k]["unorderedItems"].append(
                {"platinum": v, "itemName": itemName, "ducats": 0}
            )
    return (itemsOrderstopTen, itemsOrderscheapest, itemsOrdersaverage, playerListings)


def platCheck(itemsNames, itemsDucat):
    itemsOrderstopTen = {"sell": {}, "buy": {}}
    itemsOrderscheapest = {"sell": {}, "buy": {}}
    itemsOrdersaverage = {"sell": {}, "buy": {}}
    playerListings = {}
    iteration = 0
    for k, tv in itemsNames.items():
        start_time = time.time()
        stuff = updateItemplat(
            k,
            itemsNames,
            itemsDucat,
            itemsOrderstopTen,
            itemsOrderscheapest,
            itemsOrdersaverage,
            playerListings,
        )
        itemsOrderstopTen.update(stuff[0])
        itemsOrderscheapest.update(stuff[1])
        itemsOrdersaverage.update(stuff[2])
        playerListings.update(stuff[3])
        iteration += 1
        if (time.time() - start_time) <= 0.34:
            sleep = 0.34 - (time.time() - start_time)
            if sleep < 0.01:
                sleep = 0.01
            time.sleep(sleep)
        # print("[{}/{}]".format(iteration, len(itemsNames.items())))
    itemsOrdersraw = {}
    return (
        itemsOrderstopTen,
        itemsOrderscheapest,
        itemsOrdersaverage,
        playerListings,
    )


def ducatPlatefficency(itemName, itemsDucat, itemsOrderscheapest):
    try:
        return itemsDucat[itemName] / itemsOrderscheapest["sell"][itemName][1]
    except ZeroDivisionError:
        return 0
    except KeyError:
        return "No ducat value listed on Warframe.Market, please notify Warframe.Market"


def bestDucatplatEfficencycalc(itemsNames, itemsDucat, itemsOrderscheapest):
    ducatPlatledgerSorted = []
    ducatPlatledgerUnsorted = {}
    for k, v in itemsNames.items():
        add = ducatPlatefficency(k, itemsDucat, itemsOrderscheapest)
        if add != "No ducat value listed on Warframe.Market, please notify Warframe.Market":
            ducatPlatledgerUnsorted[k] = add
    ducatPlatledgerSorted = sorted(ducatPlatledgerUnsorted.items(), key=operator.itemgetter(1))
    ducatPlatledgerUnsorted = {}
    return ducatPlatledgerSorted


def bestDucatplatEfficencytxt(count, itemsDucat, itemsOrderscheapest, ducatPlatledgerSorted):
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
    return (
        str(datetime.datetime.isoformat(datetime.datetime.now()))
        + "\n\n"
        + "\n".join(bestDucatplatEfficencytxtList)
    )


def playerListingsaccumulator(playerListings):
    for k, v in playerListings.items():
        for v2 in v["unorderedItems"]:
            try:
                v2["efficency"] = v2["ducats"] / v2["platinum"]
            except ZeroDivisionError:
                v2["efficency"] = 0
        playerSalessorted = sorted(v["unorderedItems"], key=operator.itemgetter("efficency"))
        playerSalessorted.reverse()
        for v2 in playerSalessorted:
            for v3 in v["unorderedItems"]:
                if v2["itemName"] in v3.values():
                    v["orderedItems"].append(v3)
            if len(v["orderedItems"]) >= 6:
                break
        del playerSalessorted
        del v["unorderedItems"]
        for v2 in v["orderedItems"]:
            v["playerPlat"] = v["playerPlat"] + v2["platinum"]
            v["playerDucats"] = v["playerDucats"] + v2["ducats"]
        try:
            v["playerEfficency"] = v["playerDucats"] / v["playerPlat"]
        except ZeroDivisionError:
            v["playerEfficency"] = 0
    playerDucatefficencysorted = sorted(
        playerListings.values(), key=operator.itemgetter("playerEfficency")
    )
    playerDucatefficencysorted.reverse()
    json = {
        "last Updated": str(datetime.datetime.isoformat(datetime.datetime.now())),
        "playersByefficency": playerDucatefficencysorted,
    }
    return json


def lambda_handler(event, context):
    print("Started plat and efficency checks", datetime.datetime.isoformat(datetime.datetime.now()))
    itemsNames, itemsDucat = importNamesandDucats()
    print("Finished name and ducat import", datetime.datetime.isoformat(datetime.datetime.now()))
    itemsOrderstopTen, itemsOrderscheapest, itemsOrdersaverage, playerListings = platCheck(
        itemsNames, itemsDucat
    )
    print("Finished plat check", datetime.datetime.isoformat(datetime.datetime.now()))
    ducatPlatledgerSorted = bestDucatplatEfficencycalc(itemsNames, itemsDucat, itemsOrderscheapest)
    print("Finished efficency check", datetime.datetime.isoformat(datetime.datetime.now()))
    toClient = {
        "last Updated": str(datetime.datetime.isoformat(datetime.datetime.now())),
        "itemsNames": itemsNames,
        "itemsOrderstopTen": itemsOrderstopTen,
        "itemsOrderscheapest": itemsOrderscheapest,
        "itemsOrdersaverage": itemsOrdersaverage,
        "itemsDucat": itemsDucat,
        "ducatPlatledgerSorted": ducatPlatledgerSorted,
    }
    client = boto3.client("s3")
    client.put_object(
        Bucket="www.jsourdough.com",
        Key="ImportantInfo.json",
        Body=json.dumps(toClient, indent=4),
        ContentType="text/plain",
    )
    client.put_object(
        Bucket="www.jsourdough.com",
        Key="bestDucatplatEfficency.txt",
        Body=bestDucatplatEfficencytxt(20, itemsDucat, itemsOrderscheapest, ducatPlatledgerSorted),
        ContentType="text/plain",
    )
    client.put_object(
        Bucket="www.jsourdough.com",
        Key="playerListings.json",
        Body=json.dumps(playerListingsaccumulator(playerListings), indent=4),
        ContentType="text/plain",
    )
    print("Pages Updated", datetime.datetime.isoformat(datetime.datetime.now()))
