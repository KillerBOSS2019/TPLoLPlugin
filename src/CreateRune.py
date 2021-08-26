import json
import yaml
import os
import sys
from HTTP import Http

if os.path.isfile('info.yml'):
    with open("info.yml") as ddragoninfo:
        ddragoninfo = yaml.safe_load(ddragoninfo)
else:
    sys.exit(0)

LeagueVersion = ddragoninfo['Assets_Version']
Language = 'en_US'

def createRune(runeData:str, name):
    def findId(id):
        with open(f"DDragon\\{LeagueVersion}\\data\\{Language}\\runesReforged.json", encoding="utf-8") as CreateRune:
            CreateRune = json.loads(CreateRune.read())
        for rune in range(len(CreateRune)):
            if CreateRune[rune]['id'] == int(id):
                return (CreateRune[rune]['id'], rune)
        return None
    def keyStone(indexTree, indexKeyStone):
        with open(f"DDragon\\{LeagueVersion}\\data\\{Language}\\runesReforged.json", encoding="utf-8") as data:
            data = json.loads(data.read())
            return data[indexTree]['slots'][0]['runes'][indexKeyStone-1]['id']
    def findStuff(indexTree, item, step):
        with open(f"DDragon\\{LeagueVersion}\\data\\{Language}\\runesReforged.json", encoding="utf-8") as data:
            data = json.loads(data.read())
            return data[indexTree]['slots'][step]['runes'][item-1]['id']
    runeTrees = {
        "D": "8100", # Domination
        "I": "8300", # Inspiration
        "P": "8000", # Precision
        "R": "8400", # Resolve
        "S": "8200" # Sorcery
    }
    runeTree1 = runeData[0:5].upper()
    runeTree2 = runeData[5:9].upper()
    statusRune = runeData[9:12]
    if len(runeTree1) == 5 and len(runeTree2) == 4 and len(statusRune) == 3:
        mainTree = findId(runeTrees[runeTree1[0:1]])
        runeTree = findId(runeTrees[runeTree2[0:1]])
    emptyRow = int(runeTree2[1:4].index("0"))+1
    #secondRune = [i for i in range(1,4) if emptyRow != i]
    secondRune = []
    indexMatch = {
        1: int(runeTree2[1:2]),
        2: int(runeTree2[2:3]),
        3: int(runeTree2[3:4])
    }
    for i in range(1,4):
        if emptyRow != i:
            secondRune.append(findStuff(runeTree[1], indexMatch[i], i))

    statusDict = {
        1: [5008, 5005, 5007],
        2: [5008, 5002, 5003],
        3: [5001, 5002, 5003]
    }
    return {
        "current": True,
        "id": 0,
        "isActive": True,
        "isDeletable": True,
        "isEditable": True,
        "isValid": True,
        "lastModified": 0,
        "name": name,
        "order": 0,
        "primaryStyleId": mainTree[0],
        "selectedPerkIds": [
            keyStone(mainTree[1], int(runeTree1[1:2])),
            findStuff(mainTree[1], int(runeTree1[2:3]), 1),
            findStuff(mainTree[1], int(runeTree1[3:4]), 2),
            findStuff(mainTree[1], int(runeTree1[4:5]), 3),
            secondRune[0],
            secondRune[1],
            statusDict[1][int(statusRune[0:1])-1],
            statusDict[2][int(statusRune[1:2])-1],
            statusDict[3][int(statusRune[2:3])-1]
        ],
        "subStyleId": runeTree[0]
        }

def create(runeData, runeName, setCurrent=True):
    http = Http()

    def getTotalPage():
        allPages = http.get("/lol-perks/v1/pages").json()

        editablePage = []
        for page in allPages:
            if page['isDeletable'] and page['isEditable']:
                editablePage.append(page)
        return editablePage
    userCanHave = http.get("/lol-perks/v1/inventory").json()['ownedPageCount']
    totalPage = getTotalPage()
    listVaildTree = ["D", "I", "P", "R", "S"]
    if not userCanHave > len(totalPage):
        http.delete(f"/lol-perks/v1/pages/{totalPage[0]['id']}")

    if len(runeData) == 12 and runeData[0:1].upper() in listVaildTree and runeData[5:6].upper() in listVaildTree:
        try:
            if isinstance(int(runeData[1:5]), int) and isinstance(int(runeData[6:12]), int):
                def checkKeyStone(keystone, keyStoneIndex):
                    if keystone == "D":
                        return 4 >= keyStoneIndex >= 1
                    elif keystone == "I":
                        return 3 >= keyStoneIndex >= 1
                    elif keystone == "P":
                        return 4 >= keyStoneIndex >= 1
                    elif keystone == "R":
                        return 3 >= keyStoneIndex >= 1
                    elif keystone == "S":
                        return 3 >= keyStoneIndex >= 1
                def checkVaildIndex(data):
                    isAllpassed = []
                    for x in data:
                        isAllpassed.append(4 >= int(x) >= 1)
                    if len(isAllpassed) == 6 and isAllpassed.count(False) == 1:
                        return True

                    return all(isAllpassed)
                if checkKeyStone(runeData[0:1].upper(), int(runeData[1:2])):
                    if checkVaildIndex(runeData[2:5]) and checkVaildIndex(runeData[6:12]) and "0" in runeData:
                        generatedRune = createRune(runeData, runeName)
                        createdRuneId = http.post("/lol-perks/v1/pages", json=generatedRune).json()['id']
                        if setCurrent:
                            http.put(f"/lol-perks/v1/pages/{createdRuneId}")
        except Exception as e:
            print(e)

# create("S2211D301111", "Galio Build", )

# create("P1331R330212", "Akshan")

# create("S2233D034113", "Lux Midlaner")