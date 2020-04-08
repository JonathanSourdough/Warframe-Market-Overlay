import requests
import pytesseract
import difflib
import operator
import json
import os

cwd = os.getcwd()


importantInfo = {}
warframeParts = ["Chassis", "Systems", "Neuroptics"]
primePartsnames = []
# pytesseract.pytesseract.tesseract_cmd = cwd + "/Tesseract-OCR-V5/tesseract.exe"


def generateDictFromMarketItems():
    words = set(" ".join(importantInfo["itemsNames"]).split(" "))
    with open("eng.user-words", "w+") as f:
        f.write("\n".join(words))


def getImportantinfo():
    global importantInfo
    global warframeParts
    global primePartsnames
    importantInfo = requests.get(
        "https://s3.us-east-2.amazonaws.com/www.jsourdough.com/ImportantInfo.json"
    ).json()
    importantInfo["itemsNames"]["Forma Blueprint"] = "Forma"
    importantInfo["itemsNames"]["Failed"] = "Failed"
    importantInfo["itemsDucat"]["Forma Blueprint"] = 0
    importantInfo["itemsDucat"]["Failed"] = 0
    importantInfo["itemsOrdersaverage"]["sell"]["Forma Blueprint"] = 0
    importantInfo["itemsOrdersaverage"]["sell"]["Failed"] = 0
    importantInfo["itemsOrderscheapest"]["sell"]["Forma Blueprint"] = ["None", 0]
    importantInfo["itemsOrderscheapest"]["sell"]["Failed"] = ["None", 0]
    importantInfo["itemsOrdersaverage"]["buy"]["Forma Blueprint"] = 0
    importantInfo["itemsOrdersaverage"]["buy"]["Failed"] = 0
    importantInfo["itemsOrderscheapest"]["buy"]["Forma Blueprint"] = ["None", 0]
    importantInfo["itemsOrderscheapest"]["buy"]["Failed"] = ["None", 0]
    for k, tv in importantInfo["itemsNames"].items():
        if any(x in k for x in warframeParts):
            primePartsnames.append(k + " Blueprint")
        else:
            primePartsnames.append(k)
    generateDictFromMarketItems()
    return (importantInfo, primePartsnames)


def imageTolist(image):
    screenTesseract = []
    screenTesseractraw = pytesseract.image_to_string(
        image, config="--psm 4 --tessdata-dir tessdata --user-words eng.user-words"
    ).split("\n")
    for i, v in enumerate(screenTesseractraw):
        if not (screenTesseractraw[i] == "" or screenTesseractraw[i].isspace()):
            try:
                int(v.replace(",", ""))
            except:
                screenTesseract.append(v)
    return screenTesseract


def mappedWordprocessing(itemName, primePartsnames):
    global warframeParts
    diffValuesunsorted = {}
    diffValuessorted = []
    for k in primePartsnames:
        diffValuesunsorted[k] = int(
            round(difflib.SequenceMatcher(a=itemName, b=k).ratio(), 2) * 100
        )
        diffValuessorted = list(
            reversed(sorted(diffValuesunsorted.items(), key=operator.itemgetter(1)))
        )
    if any(x in diffValuessorted[0][0] for x in warframeParts):
        diffValuessorted[0] = (diffValuessorted[0][0].rsplit(" ", 1)[0], diffValuessorted[0][1])
    return diffValuessorted[0]


def mappedCalc(image, primePartsnames):
    processedPrime = None
    primePart = imageTolist(image)
    bestRead = ("Failed", 0)
    multiLine = ("Failed", 0)
    oneLine = ("Failed", 0)
    if primePart != []:
        multiLine = mappedWordprocessing(" ".join(primePart).title(), primePartsnames)
        oneLine = mappedWordprocessing(primePart[-1].title(), primePartsnames)
        if multiLine[1] >= oneLine[1]:
            bestRead = multiLine
            processedPrime = " ".join(primePart)
        else:
            bestRead = oneLine
            processedPrime = primePart[-1]
    return (bestRead[0], str(bestRead[1]))
