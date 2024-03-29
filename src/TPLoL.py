import asyncio
import json
import os
import platform
import sys
import threading
from functools import wraps
from typing import Awaitable, TypeVar

import html2text
import requests
import TouchPortalAPI
from lcu_driver import Connector
from TouchPortalAPI import TYPES, Tools
import yaml
from utils.HTTP import Http
from utils.CreateRune import create as createRune
from utils.utils import (getAvailableQueue)

# Important
R = TypeVar("R")

def async_to_sync(func: Awaitable[R]) -> R:
    '''Wraps `asyncio.run` on an async function making it sync callable.'''
    if not asyncio.iscoroutinefunction(func):
        raise TypeError(f"{func} is not a coroutine function")
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return asyncio.get_event_loop().run_until_complete(func(*args, **kwargs))
        except RuntimeError:
            return asyncio.new_event_loop().run_until_complete(func(*args, **kwargs))
    return wrapper

def silence_event_loop_closed(func):
    '''Silences the Exception `RuntimeError: Event loop is closed` in a class method.'''
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != 'Event loop is closed':
                raise
    return wrapper

def silence_proactor_pipe_deallocation():
    '''Silences the Exception `RuntimeError: Event loop is closed` in `_ProactorBasePipeTransport.__del__`.'''
    from asyncio.proactor_events import _ProactorBasePipeTransport
    _ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)

if platform.system() == 'Windows':
    silence_proactor_pipe_deallocation()


# Variables
if os.path.isfile('info.yml'):
    with open("info.yml") as ddragoninfo:
        ddragoninfo = yaml.safe_load(ddragoninfo)
else:
    sys.exit(0)
TPClient = TouchPortalAPI.Client('TP.Plugin.LoLPlugin')
connector = Connector()
htmlText = html2text.HTML2Text()
Language = 'en_US'
running = True
riftHeraldRespawnTimer = 360
LeagueVersion = ddragoninfo['Assets_Version']
EnabledQueues = []
SpellDict = {
    "Barrier": 21,
    "Cleanse": 1,
    "Ignite": 14,
    "Exhaust": 3,
    "Flash": 4,
    "Ghost": 6,
    "Heal": 7,
    "Clarity": 13,
    "Smite": 11,
    "Teleport": 12
}
def getTime(Time):
    mins,seconds = divmod(Time,60)
    return "%02d:%02d" % (mins, seconds)

def rankDataProcesser(data):
    pass

def startupUpdatesummoner():
    global EnabledQueues
    Summoner = Http().get('/lol-summoner/v1/current-summoner').json()
    EnabledQueues = getAvailableQueue()
    TPClient.choiceUpdate("KillerBOSS.Plugin.LolPlugin.actions.PutUserinQueue.Modes", [queue['name'] for queue in EnabledQueues])
    if Summoner != None:
        try:
            TPClient.stateUpdateMany([
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.DisplayName",
                    "value": Summoner['displayName']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.DisplayIcon",
                    "value": Tools.convertImage_to_base64(f"DDragon\\{LeagueVersion}\\img\\profileicon\\{Summoner['profileIconId']}.png")
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.CurrentLevel",
                    "value": Summoner['summonerLevel']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.numberofRolls",
                    "value": Summoner['rerollPoints']['numberOfRolls']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.precentCompleteNextLevel",
                    "value": Summoner['percentCompleteForNextLevel']
                }
            ]  
        )
        except TypeError:
            pass

### League Client Event listener
@connector.ready
async def connect(connection):
    global running
    print('LCU API is ready to be used')
    startupUpdatesummoner()
    running = True

# @connector.ws.register('/lol-matchmaking/v1/ready-check', event_types=("UPDATE",))
# async def matchMakingPopUp(connection, event): # Ready Check when match found Popup
#     print(event.data)

@connector.ws.register('/lol-champ-select-legacy/v1/session', event_types=('UPDATE',))
async def champSelect(connection, event): # Champ Select 
    myTeamStateID = [("KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.own.BannedChamp.1.Name","KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.own.BannedChamp.1.Icon"),
                     ("KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.own.BannedChamp.2.Name","KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.own.BannedChamp.2.Icon"),
                     ("KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.own.BannedChamp.3.Name","KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.own.BannedChamp.3.Icon"),
                     ("KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.own.BannedChamp.4.Name","KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.own.BannedChamp.4.Icon"),
                     ("KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.own.BannedChamp.5.Name","KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.own.BannedChamp.5.Icon")
                    ]
    theirTeamStateID = [("KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.Their.BannedChamp.1.Name","KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.Their.BannedChamp.1.Icon"),
                     ("KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.Their.BannedChamp.2.Name","KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.Their.BannedChamp.2.Icon"),
                     ("KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.Their.BannedChamp.5.Name","KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.Their.BannedChamp.5.Icon"),
                     ("KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.Their.BannedChamp.3.Name","KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.Their.BannedChamp.3.Icon"),
                     ("KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.Their.BannedChamp.4.Name","KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.Their.BannedChamp.4.Icon")
                    ]
    
    def getChampjson(champList):
        needToReturn = []
        with open(f"DDragon\\{LeagueVersion}\\data\\{Language}\\championFull.json", encoding="utf-8") as champion:
            champion = json.loads(champion.read())
            for champ in champList:
                for x in champion['data']:
                    if int(champion['data'][x]['key']) == int(champ):
                        needToReturn.append(champion['data'][x])
        return needToReturn

    def updateChampSelect(teamID, SelectData):
        for mTeam in range(len(teamID)):
            try:
                imagepath = SelectData[mTeam]['image']['full']
                champName = SelectData[mTeam]['name']
                TPClient.stateUpdate(teamID[mTeam][1], Tools.convertImage_to_base64(f"DDragon\\{LeagueVersion}\\img\\champion\\{imagepath}"))
                TPClient.stateUpdate(teamID[mTeam][0], champName)
            except IndexError:
                TPClient.stateUpdate(teamID[mTeam][1], Tools.convertImage_to_base64(f"ExtraData\\championSelect\\-1.png"))
                TPClient.stateUpdate(teamID[mTeam][0], "None")

    if isinstance(event.data, dict):
        myTeam = getChampjson(event.data['bans']['myTeamBans'])
        theirTeam = getChampjson(event.data['bans']['theirTeamBans'])
        updateChampSelect(myTeamStateID, myTeam)
        updateChampSelect(theirTeamStateID, theirTeam)

@connector.ws.register('/lol-chat/v1/friend-counts', event_types=('UPDATE',))
async def friendCount(connection, event): # To-Do Show user all their Friend online offline etc...
    for friend in list(event.data.keys()):
        TPClient.stateUpdate(f"KillerBOSS.TP.Plugins.LoLPlugin.states.LCU.FriendCount.{friend}", str(event.data[friend]))

@connector.ws.register('/lol-summoner/v1/current-summoner', event_types=('UPDATE',))
async def currentSummoner(connection, event):
    TPClient.stateUpdateMany([
        {
            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.DisplayName",
            "value": event.data['displayName']
        },
        {
            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.DisplayIcon",
            "value": Tools.convertImage_to_base64(f"DDragon\\{LeagueVersion}\\img\\profileicon\\{event.data['profileIconId']}.png")
        },
        {
            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.CurrentLevel",
            "value": event.data['summonerLevel']
        },
        {
            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.numberofRolls",
            "value": event.data['rerollPoints']['numberOfRolls']
        },
        {
            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.precentCompleteNextLevel",
            "value": event.data['percentCompleteForNextLevel']
        }
    ])

@connector.ws.register('/lol-matchmaking/v1/search', event_types=('UPDATE',))
async def matchMakingState(connection, event):
    print(event.data)
    TPClient.stateUpdateMany([
        {
            "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.estmatedQueueTime',
            "value": getTime(int(round(event.data['estimatedQueueTime'], 0)))
        },
        {
            "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.TimeinQueue',
            "value": getTime(int(round(event.data['timeInQueue'], 0)))
        },
        {
            "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.UserResponses',
            "value": event.data['readyCheck']['playerResponse']
        },
        {
            "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.matchmaking.States',
            "value": event.data['searchState']
        }
    ])


@connector.ws.register('/lol-ranked/v1/current-ranked-stats', event_types=('UPDATE',))
async def getUserRankinfo(connection, event):
    print(event.data)
# @connector.close
# async def disconnect(connection):
#     await connector.stop()

### Ingame Event handler
def InGame():
    Timer = threading.Timer(0.3, InGame)
    isWorking = False
    if running:
        Timer.start()
        try:
            mainData = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify='riotgames.pem')
            if mainData.status_code == 200:
                mainData = mainData.json()
                try:
                    if mainData['events']['Events'][0]['EventID'] == 0:
                        isWorking = True
                except KeyError:
                    isWorking = False
            else:
                isWorking = False
        except Exception as e:
            isWorking = False

        if isWorking:
            def getRune(Id):
                with open(f'DDragon\\{LeagueVersion}\\data\\{Language}\\runesReforged.json', encoding="utf-8") as Data:
                    Data = json.loads(Data.read())
                    for x in Data:
                        if x['id'] == Id:
                            return x

            def getRuneTree(Rune):
                with open(f'DDragon\\{LeagueVersion}\\data\\{Language}\\runesReforged.json', encoding="utf-8") as Data:
                    Data = json.loads(Data.read())
                    for eachRunes in Data:
                        for slots in range(len(eachRunes['slots'])):
                            for x in eachRunes['slots'][slots]['runes']:
                                if x['id'] == Rune:
                                    return x

            def itemUpdate(slot, itemdata):
                TPClient.stateUpdateMany([
                        {
                            "id": f"KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Item.slot.{slot+1}.Name",
                            "value": itemdata['name']
                        },
                        {
                            "id": f"KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Item.slot.{slot+1}.Desc",
                            "value": htmlText.handle(itemdata['description']).replace("\n", "")
                        },
                        {
                            "id": f"KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Item.slot.{slot+1}.Icon",
                            "value": Tools.convertImage_to_base64(f"DDragon\\{LeagueVersion}\\img\\item\\{itemdata['image']['full']}")
                        },
                        {
                            "id": f"KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Item.slot.{slot+1}.Price",
                            "value": itemdata['gold']['total']
                        },
                        {
                            "id": f"KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Item.slot.{slot+1}.SellPrice",
                            "value": itemdata['gold']['sell']
                        }
                    ])
            
            def setItemSlotNone(slots):
                for slot in slots:
                    TPClient.stateUpdateMany([
                        {
                            "id": f"KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Item.slot.{slot}.Name",
                            "value": 'None'
                        },
                        {
                            "id": f"KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Item.slot.{slot}.Desc",
                            "value": "None"
                        },
                        {
                            "id": f"KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Item.slot.{slot}.Icon",
                            "value": Tools.convertImage_to_base64(f"{os.getcwd()}//ExtraData//InGame//ItemNone.png")
                        },
                        {
                            "id": f"KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Item.slot.{slot}.Price",
                            "value": "0"
                        },
                        {
                            "id": f"KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Item.slot.{slot}.SellPrice",
                            "value": "0"
                        }
                    ])

            TPClient.stateUpdateMany([ # Get User Runes
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.primaryRuneTree.Name',
                    "value": getRune(mainData['activePlayer']['fullRunes']['primaryRuneTree']['id'])['name']
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.primaryRuneTree.Icon',
                    "value": Tools.convertImage_to_base64(os.path.join('DDragon//img//',getRune(mainData['activePlayer']['fullRunes']['primaryRuneTree']['id'])['icon']))
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.secondaryRuneTree.Name',
                    "value": getRune(mainData['activePlayer']['fullRunes']['secondaryRuneTree']['id'])['name']
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.secondaryRuneTree.Icon',
                    "value": Tools.convertImage_to_base64(os.path.join('DDragon//img//',getRune(mainData['activePlayer']['fullRunes']['secondaryRuneTree']['id'])['icon']))
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.KeyStone.Name',
                    "value": getRuneTree(mainData['activePlayer']['fullRunes']['keystone']['id'])['name']
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.KeyStone.Icon',
                    "value": Tools.convertImage_to_base64(os.path.join("DDragon//img//",getRuneTree(mainData['activePlayer']['fullRunes']['keystone']['id'])['icon']))
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.KeyStone.shortDesc',
                    "value": getRuneTree(mainData['activePlayer']['fullRunes']['keystone']['id'])['shortDesc']
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.PrimaryTree.set1.Name',
                    "value": getRuneTree(mainData['activePlayer']['fullRunes']['generalRunes'][1]['id'])['name']
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.PrimaryTree.set1.Icon',
                    "value": Tools.convertImage_to_base64(os.path.join("DDragon//img//",getRuneTree(mainData['activePlayer']['fullRunes']['generalRunes'][1]['id'])['icon']))
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.PrimaryTree.set1.shortDesc',
                    "value": getRuneTree(mainData['activePlayer']['fullRunes']['generalRunes'][1]['id'])['shortDesc']
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.PrimaryTree.set2.Name',
                    "value": getRuneTree(mainData['activePlayer']['fullRunes']['generalRunes'][2]['id'])['name']
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.PrimaryTree.set2.Icon',
                    "value": Tools.convertImage_to_base64(os.path.join("DDragon//img//",getRuneTree(mainData['activePlayer']['fullRunes']['generalRunes'][2]['id'])['icon']))
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.PrimaryTree.set2.shortDesc',
                    "value": getRuneTree(mainData['activePlayer']['fullRunes']['generalRunes'][2]['id'])['shortDesc']
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.PrimaryTree.set3.Name',
                    "value": getRuneTree(mainData['activePlayer']['fullRunes']['generalRunes'][3]['id'])['name']
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.PrimaryTree.set3.Icon',
                    "value": Tools.convertImage_to_base64(os.path.join("DDragon//img//",getRuneTree(mainData['activePlayer']['fullRunes']['generalRunes'][3]['id'])['icon']))
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.PrimaryTree.set3.shortDesc',
                    "value": getRuneTree(mainData['activePlayer']['fullRunes']['generalRunes'][3]['id'])['shortDesc']
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.SecondaryTree.set1.Name',
                    "value": getRuneTree(mainData['activePlayer']['fullRunes']['generalRunes'][4]['id'])['name']
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.SecondaryTree.set1.Icon',
                    "value": Tools.convertImage_to_base64(os.path.join("DDragon//img//",getRuneTree(mainData['activePlayer']['fullRunes']['generalRunes'][4]['id'])['icon']))
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.SecondaryTree.set1.shortDesc',
                    "value": getRuneTree(mainData['activePlayer']['fullRunes']['generalRunes'][4]['id'])['shortDesc']
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.SecondaryTree.set2.Name',
                    "value": getRuneTree(mainData['activePlayer']['fullRunes']['generalRunes'][5]['id'])['name']
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.SecondaryTree.set2.Icon',
                    "value": Tools.convertImage_to_base64(os.path.join("DDragon//img//",getRuneTree(mainData['activePlayer']['fullRunes']['generalRunes'][5]['id'])['icon']))
                },
                {
                    "id": 'KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Runes.SecondaryTree.set2.shortDesc',
                    "value": getRuneTree(mainData['activePlayer']['fullRunes']['generalRunes'][5]['id'])['shortDesc']
                }])

            myChampion = ""
            myUserData = {}
            for x in mainData['allPlayers']:
                if mainData['activePlayer']['summonerName'] == x['summonerName']:
                    myChampion = x['rawChampionName'].split("_")[-1]
                    myUserData = x 
            def getSpellDetail(Ability):
                return 0 if mainData['activePlayer']['abilities'][Ability]['abilityLevel'] == 1 else mainData['activePlayer']['abilities'][Ability]['abilityLevel']-1
            if myChampion != "":
                with open(f'DDragon\\{LeagueVersion}\\data\\{Language}\\champion\\{myChampion}.json', encoding="utf-8") as Data:
                    Data = json.loads(Data.read())
                    if "skinName" in list(myUserData.keys()):
                        for skin in Data['data'][myChampion]['skins']:
                            if myUserData['skinName'] == skin['name']:
                                TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.Champion.IconWSkin", Tools.convertImage_to_base64(f"DDragon\\img\\champion\\tiles\\{myChampion}_{skin['num']}.jpg", type="Local"))
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.Champion.Icon", Tools.convertImage_to_base64(f"DDragon\\img\\champion\\tiles\\{myChampion}_0.jpg", type="Local"))
                    
                    for spell in Data['data'][myChampion]['spells']: # Champion Abilities
                        if spell['id'] == mainData['activePlayer']['abilities']['Q']['id']:
                            #print(spell['cooldown'][getSpellDetail("Q")])
                            TPClient.stateUpdateMany(
                                [
                                    #                        Champion Q Ability info
                                    { # mainData['activePlayer']['abilities']['Q']['abilityLevel']
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.Q.Name",
                                        "value": spell['name']
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.Q.Level",
                                        "value": str(mainData['activePlayer']['abilities']['Q']['abilityLevel'])
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.Q.Icon",
                                        "value": Tools.convertImage_to_base64(f"DDragon\\{LeagueVersion}\\img\\spell\\{spell['image']['full']}")
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.Q.Cost",
                                        "value": str(spell['cost'][mainData['activePlayer']['abilities']['Q']['abilityLevel']-1])
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.Q.Cooldown",
                                        "value": str(spell['cooldown'][mainData['activePlayer']['abilities']['Q']['abilityLevel']-1])
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.Q.Desc",
                                        "value": spell['description']
                                    },
                                ]
                            )
                        elif spell['id'] == mainData['activePlayer']['abilities']['W']['id']:
                            TPClient.stateUpdateMany(
                                [
                                    #                        Champion W Ability info
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.W.Name",
                                        "value": spell['name']
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.W.Level",
                                        "value": str(mainData['activePlayer']['abilities']['W']['abilityLevel'])
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.W.Icon",
                                        "value": Tools.convertImage_to_base64(f"DDragon\\{LeagueVersion}\\img\\spell\\{spell['image']['full']}")
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.W.Cost",
                                        "value": str(spell['cost'][mainData['activePlayer']['abilities']['W']['abilityLevel']-1])
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.W.Cooldown",
                                        "value": str(spell['cooldown'][mainData['activePlayer']['abilities']['W']['abilityLevel']-1])
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.W.Desc",
                                        "value": spell['description']
                                    },
                                ]
                            )
                        elif spell['id'] == mainData['activePlayer']['abilities']['E']['id']:
                            TPClient.stateUpdateMany(
                                [
                                    #                        Champion E Ability info
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.E.Name",
                                        "value": spell['name']
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.E.Level",
                                        "value": str(mainData['activePlayer']['abilities']['E']['abilityLevel'])
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.E.Icon",
                                        "value": Tools.convertImage_to_base64(f"DDragon\\{LeagueVersion}\\img\\spell\\{spell['image']['full']}")
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.E.Cost",
                                        "value": str(spell['cost'][mainData['activePlayer']['abilities']['E']['abilityLevel']-1])
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.E.Cooldown",
                                        "value": str(spell['cooldown'][mainData['activePlayer']['abilities']['E']['abilityLevel']-1])
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.E.Desc",
                                        "value": spell['description']
                                    },
                                ]
                            )
                        elif spell['id'] == mainData['activePlayer']['abilities']['R']['id']:
                            TPClient.stateUpdateMany(
                                [
                                    #                        Champion R Ability info
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.R.Name",
                                        "value": spell['name']
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.R.Level",
                                        "value": str(mainData['activePlayer']['abilities']['R']['abilityLevel'])
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.R.Icon",
                                        "value": Tools.convertImage_to_base64(f"DDragon\\{LeagueVersion}\\img\\spell\\{spell['image']['full']}")
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.R.Cost",
                                        "value": str(spell['cost'][mainData['activePlayer']['abilities']['R']['abilityLevel']-1])
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.R.Cooldown",
                                        "value": str(spell['cooldown'][mainData['activePlayer']['abilities']['R']['abilityLevel']-1])
                                    },
                                    {
                                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.R.Desc",
                                        "value": spell['description']
                                    },
                                ]
                            )
                    TPClient.stateUpdateMany([ # Passive
                        {
                            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.Passive.Name",
                            "value": Data['data'][myChampion]['passive']['name']
                        },
                        {
                            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.Passive.Desc",
                            "value": Data['data'][myChampion]['passive']['description']
                        },
                        {
                            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampAbilities.Passive.Image",
                            "value": Tools.convertImage_to_base64(f"DDragon\\{LeagueVersion}\\img\\passive\\{Data['data'][myChampion]['passive']['image']['full']}")
                        }
                    ])
                with open(f"DDragon\\{LeagueVersion}\\data\\{Language}\\summoner.json", encoding="utf-8") as summonerSpell:
                    summonerSpell = json.loads(summonerSpell.read())
                    for x in mainData['allPlayers']:
                        if mainData['activePlayer']['summonerName'] == x['summonerName']:
                            Spell1 = str(x["summonerSpells"]['summonerSpellOne']['rawDisplayName']).replace("GeneratedTip_SummonerSpell_", "").replace("_DisplayName", "")
                            Spell2 = str(x["summonerSpells"]['summonerSpellTwo']['rawDisplayName']).replace("GeneratedTip_SummonerSpell_", "").replace("_DisplayName", "")
                            for spell in summonerSpell['data']:
                                if summonerSpell['data'][spell]['id'] == Spell1:
                                    TPClient.stateUpdateMany([
                                        {
                                            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.Spell1.Name",
                                            "value": summonerSpell['data'][spell]['name']
                                        },
                                        {
                                            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.Spell1.description",
                                            "value": summonerSpell['data'][spell]['description']
                                        },
                                        {
                                            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.Spell1.Icon",
                                            "value": Tools.convertImage_to_base64(f"DDragon\\{LeagueVersion}\\img\\spell\\{summonerSpell['data'][spell]['image']['full']}")
                                        }
                                    ])
                                if summonerSpell['data'][spell]['id'] == Spell2:
                                    TPClient.stateUpdateMany([
                                        {
                                            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.Spell2.Name",
                                            "value": summonerSpell['data'][spell]['name']
                                        },
                                        {
                                            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.Spell2.description",
                                            "value": summonerSpell['data'][spell]['description']
                                        },
                                        {
                                            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.Spell2.Icon",
                                            "value": Tools.convertImage_to_base64(f"DDragon\\{LeagueVersion}\\img\\spell\\{summonerSpell['data'][spell]['image']['full']}")
                                        }
                                    ])
            TPClient.stateUpdateMany([ # User Champ Stats
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.AbilityPower",
                    "value": mainData['activePlayer']['championStats']['abilityPower']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.Armor",
                    "value": mainData['activePlayer']['championStats']['armor']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.ArmorPenetrationPercent",
                    "value": mainData['activePlayer']['championStats']['armorPenetrationPercent']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.attackDamage",
                    "value": round(mainData['activePlayer']['championStats']['attackDamage'], 2)
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.attackRange",
                    "value": round(mainData['activePlayer']['championStats']['attackRange'], 2)
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.attackSpeed",
                    "value": round(mainData['activePlayer']['championStats']['attackSpeed'], 2)
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.bonusArmorPenetrationPercent",
                    "value": mainData['activePlayer']['championStats']['bonusArmorPenetrationPercent']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.bonusMagicPenetrationPercent",
                    "value": mainData['activePlayer']['championStats']['bonusMagicPenetrationPercent']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.critChance",
                    "value": mainData['activePlayer']['championStats']['critChance']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.critDamage",
                    "value": mainData['activePlayer']['championStats']['critDamage']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.currentHealth",
                    "value": mainData['activePlayer']['championStats']['currentHealth']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.healthRegenRate",
                    "value": mainData['activePlayer']['championStats']['healthRegenRate']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.lifeSteal",
                    "value": mainData['activePlayer']['championStats']['lifeSteal']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.magicLethality",
                    "value": mainData['activePlayer']['championStats']['magicLethality']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.magicPenetrationPercent",
                    "value": mainData['activePlayer']['championStats']['magicPenetrationPercent']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.magicResist",
                    "value": round(mainData['activePlayer']['championStats']['magicResist'],2)
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.maxHealth",
                    "value": mainData['activePlayer']['championStats']['maxHealth']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.moveSpeed",
                    "value": mainData['activePlayer']['championStats']['moveSpeed']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.physicalLethality",
                    "value": mainData['activePlayer']['championStats']['physicalLethality']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.resourceMax",
                    "value": mainData['activePlayer']['championStats']['resourceMax']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.resourceRegenRate",
                    "value": round(mainData['activePlayer']['championStats']['resourceRegenRate'],2)
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.resourceType",
                    "value": mainData['activePlayer']['championStats']['resourceType']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.resourceValue",
                    "value": mainData['activePlayer']['championStats']['resourceValue']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.spellVamp",
                    "value": mainData['activePlayer']['championStats']['spellVamp']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ChampStats.tenacity",
                    "value": mainData['activePlayer']['championStats']['tenacity']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.currentChampLevel",
                    "value": mainData['activePlayer']['level']
                }])

            # Scoreboard
            scoreboard = dict(
                assists = 0,
                deaths = 0,
                kills = 0,
                wardScore = 0,
                creepScore = 0,
            )
            teams = {
                'ORDER': {'scores': dict(scoreboard), 'members': []},
                'CHAOS': {'scores': dict(scoreboard), 'members': []},
            }

            for x in mainData['allPlayers']:
                team = teams[x['team']]
                sb = team['scores']
                
                for key in sb.keys():
                    sb[key] += x['scores'][key]
                team['members'].append(x['summonerName'])
                if mainData['activePlayer']['summonerName'] == x['summonerName']: # my Scoreboard Update
                    TPClient.stateUpdateMany([
                        {
                            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ScoreBoard.Myown.Kill",
                            "value": str(x['scores']['kills'])
                        },
                        {
                            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ScoreBoard.Myown.deaths",
                            "value": str(x['scores']['deaths'])
                        },
                        {
                            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ScoreBoard.Myown.assists",
                            "value": str(x['scores']['assists'])
                        },
                        {
                            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ScoreBoard.Myown.wardScore",
                            "value": str(round(int(x['scores']['wardScore'])))
                        },
                        {
                            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ScoreBoard.Myown.CS",
                            "value": str(round(int(x['scores']['creepScore'])))
                        },
                        {
                            "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ScoreBoard.Myown.KDA",
                            "value": str(round((x['scores']['kills']+x['scores']['assists'])/x['scores']['deaths'], 2)) if x['scores']['deaths'] != 0 else 0
                        }
                    ])
            blueTeam = teams['ORDER']['members']
            redTeam = teams['CHAOS']['members']
            states = []
            for team in teams.keys():
                teamState = "TotalBlueTeam" if team == "ORDER" else "TotalRedTeam"
                sb = teams[team]['scores']
                # if all the state names (like "Kill" and "CS") matched the score key names (like "kills" and "creepScore") then 
                # this could also be a loop over the scoreboard keys like we did above
                states.extend([
                    {
                        "id": f"KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ScoreBoard.{teamState}.Kill",
                        "value": str(sb['kills']),
                    },
                    {
                        "id": f"KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ScoreBoard.{teamState}.deaths",
                        "value": str(sb['deaths'])
                    },
                    {
                        "id": f"KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ScoreBoard.{teamState}.assists",
                        "value": str(sb['assists'])
                    },
                    {
                        "id": f"KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ScoreBoard.{teamState}.wardScore",
                        "value": str(int(sb['wardScore']))
                    },
                    {
                        "id": f"KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ScoreBoard.{teamState}.CS",
                        "value": str(sb['creepScore'])
                    },
                    {
                        "id": f"KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.ScoreBoard.{teamState}.KDA",
                        "value": str(round((sb['kills']+sb['assists'])/sb['deaths'], 2)) if sb['deaths'] != 0 else 0
                    }
                ])

            TPClient.stateUpdateMany([
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.CurrentGold",
                    "value": mainData['activePlayer']['currentGold']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.currentChampLevel",
                    "value": mainData['activePlayer']['level']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.RespawnTimer",
                    "value": mainData['activePlayer']['level']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.CurrentHealthInPercent",
                    "value": round((mainData['activePlayer']['championStats']['currentHealth']/mainData['activePlayer']['championStats']['maxHealth'])*100, 0)
                }
            ])

            TPClient.stateUpdateMany(states)       
            with open(f"DDragon\\{LeagueVersion}\\data\\{Language}\\item.json") as items: # Update Item slots
                items = json.loads(items.read())['data']
                UsedSlots = []
                notUsedSlots = []
                for x in mainData['allPlayers']:
                    if mainData['activePlayer']['summonerName'] == x['summonerName']:
                        if len(x['items']) > 0:
                            for i in x['items']:
                                UsedSlots.append(int(i['slot'])+1)
                                for item in items:
                                    if item == str(i['itemID']):
                                        itemUpdate(i['slot'], items[item])
                            for slotnum in [1,2,3,4,5,6,7]:
                                if slotnum not in UsedSlots:
                                    notUsedSlots.append(slotnum)

                            setItemSlotNone(notUsedSlots)
                        else:
                            setItemSlotNone([1,2,3,4,5,6,7])
                setItemSlotNone(notUsedSlots)


            isEventWork = False
            try:
                currentEvents = mainData['events']['Events'][-1]
                isEventWork = True
            except IndexError:
                isEventWork = False
            canElderDragonSpawn = False
            if len(mainData['events']['Events']) > 0 and isEventWork:
                TPClient.stateUpdateMany([
                    {
                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Events.EventName",
                        "value": currentEvents['EventName']
                    },
                    {
                        "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Events.LastEventTime",
                        "value": getTime(currentEvents['EventTime'])
                    },
                ])
                if currentEvents['EventName'] == "DragonKill":
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Events.DragonType", currentEvents['DragonType'])
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Events.isDragonStolen", currentEvents['Stolen'])
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Events.LastDragon.Killer", currentEvents['KillerName'])
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Events.LastDragon.KilledTime", getTime(currentEvents['EventTime']))
                if currentEvents['EventName'] == 'HeraldKill':
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Events.isHeraldStolen", currentEvents['Stolen'])
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Events.LastHerald.Killer", currentEvents['KillerName'])
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Events.LastHerald.KilledTime", getTime(currentEvents['EventTime']))
                if currentEvents['EventName'] == 'BaronKill':
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Events.isBaronStolen", currentEvents['Stolen'])
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Events.LastBaron.Killer", currentEvents['KillerName'])
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Events.LastBaron.KilledTime", getTime(currentEvents['EventTime']))
                if currentEvents['EventName'] == "Ace":
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Events.Acer", currentEvents['Acer'])
                    if currentEvents['AcingTeam'] == 'ORDER':
                        TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Events.Ace", "Blue")
                    else:
                        TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Events.Ace", "Red")
                if currentEvents['EventName'] == 'TurretKilled' or currentEvents['EventName'] == "InhibKilled":
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Events.TurretKilled.Name", currentEvents['KillerName'])
                    if currentEvents['EventName'] == "TurretKilled":
                        TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Events.TurretKilled", currentEvents['TurretKilled'])
                    else:
                        TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Events.TurretKilled", currentEvents['InhibKilled'])
                TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.Events.LastEventTime", getTime(currentEvents['EventTime']))
                BluedragonCount = 0
                ReddragonCount = 0
                for dragonEvent in mainData['events']['Events']:
                    if dragonEvent['EventName'] == "DragonKill":
                        if dragonEvent['KillerName'] in blueTeam:
                            BluedragonCount += 1
                        elif dragonEvent['KillerName'] in redTeam:
                            ReddragonCount += 1
                if BluedragonCount >= 4 or ReddragonCount >= 4:
                    canElderDragonSpawn = True
                else:
                    canElderDragonSpawn = False

            TPClient.stateUpdateMany([ # Get Game detail
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.GameData.gameMode",
                    "value": mainData['gameData']['gameMode']
                },
                {
                    "id": "KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.GameData.gameTime",
                    "value": getTime(mainData['gameData']['gameTime'])
                },
            ])
            with open(os.path.join(os.getcwd(), f"DDragon\\{LeagueVersion}\\data\\{Language}\\map.json"), encoding="utf-8") as mapData:
                mapData = json.loads(mapData.read())['data']
                TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.GameData.MapName", mapData[str(mainData['gameData']['mapNumber'])]['MapName'])
                TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.Ingame.GameData.MapImage", Tools.convertImage_to_base64(os.path.join(os.getcwd(), f"DDragon\\{LeagueVersion}\\img\\map\\"+mapData[str(mainData['gameData']['mapNumber'])]['image']['full'])))
            
            def getobjectiveStatus(firstSpawn, respawn, unobtainableTime, objectiveEventName, TPStatus, countDownStates):
                currentGameTime = mainData['gameData']['gameTime']
                gameEvent = mainData['events']['Events']
                latestObjectiveKill = 0
                objectiveRespawnTimer = 0
                objectiveTimeremain = "00:00"
                if firstSpawn >= currentGameTime:
                    for event in gameEvent:
                        if event['EventName'] == objectiveEventName:
                            latestObjectiveKill = event['EventTime'] # Set value to the latest Objective kill time
                            objectiveRespawnTimer = currentGameTime+respawn # get respawn time from current Time
                    if not unobtainableTime >= currentGameTime:
                        if latestObjectiveKill != 0 and objectiveTimeremain == "00:00":
                            TPClient.stateUpdate(f"KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.{TPStatus}", "Alive")
                    else:
                        TPClient.stateUpdate(f"KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.{TPStatus}", "Unobtainable")
                else:
                    TPClient.stateUpdate(f"KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.{TPStatus}", "FirstSpawn")
                    objectiveTimeremain = round(firstSpawn-currentGameTime)
                TPClient.stateUpdate(f"KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.{countDownStates}", getTime(objectiveTimeremain))
                
            # getObjectiveStatus() i am losted needed help with that on how these thing gonna work
            # because blow 3 Objective countDown n stuff are kinda repeated 3 times

            latestRiftKill = 0
            riftHeraldTimeremain = "00:00"
            killriftHeraldCounter = 0
            #          Rift Herald RespawnTimer/Status
            global riftHeraldRespawnTimer
            if mainData['gameData']['gameTime'] > 480:
                for riftHeraldEvent in mainData['events']['Events']:
                    if riftHeraldEvent['EventName'] == "HeraldKill":
                        latestRiftKill = riftHeraldEvent['EventTime']
                        riftHeraldRespawnTimer = latestRiftKill+360
                        killriftHeraldCounter += 1
                if latestRiftKill != 0 and mainData['gameData']['gameTime'] < 1185 and not killriftHeraldCounter >= 2:
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.RiftHeraldStatus", "Respawning")
                elif mainData['gameData']['gameTime'] >= 1185 or killriftHeraldCounter >= 2:
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.RiftHeraldStatus", "Unobtainable")
                
                if latestRiftKill != 0 and mainData['gameData']['gameTime'] < 1185 and round(riftHeraldRespawnTimer-mainData['gameData']['gameTime']) > 0 and not killriftHeraldCounter >= 2:
                    riftHeraldTimeremain = getTime(round(riftHeraldRespawnTimer-mainData['gameData']['gameTime']))
                else:
                    riftHeraldTimeremain = "00:00"
            else:
                riftHeraldTimeremain = getTime(round(480-mainData['gameData']['gameTime']))
            if riftHeraldTimeremain == "00:00" and mainData['gameData']['gameTime'] < 1185:
                TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.RiftHeraldStatus", "Alive")
            elif latestRiftKill == 0:
                TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.RiftHeraldStatus", "FirstSpawn")

            TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.RiftHeraldSpawnTimer", riftHeraldTimeremain)
        
            #           Dragon RespawnTimer/Status
            latestDragonkill = 0
            DragonRespawnTimer = 0
            DragonSpawnTimerRemain = "00:00"
            if mainData['gameData']['gameTime'] > 300:
                for EDrakes in mainData['events']['Events']:
                    if EDrakes['EventName'] == "DragonKill":
                        latestDragonkill = EDrakes['EventTime']
                        DragonRespawnTimer = (360 if canElderDragonSpawn else 300) + latestDragonkill

                if latestDragonkill != 0 and round(DragonRespawnTimer-mainData['gameData']['gameTime']) > 0:
                    DragonSpawnTimerRemain = getTime(round(DragonRespawnTimer-mainData['gameData']['gameTime']))
                else:
                    DragonSpawnTimerRemain = "00:00"


                if mainData['gameData']['gameTime'] >= 300 and latestDragonkill != 0 and DragonSpawnTimerRemain != "00:00":
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.EDrakeStatus", "Respawning")
                elif DragonSpawnTimerRemain == "00:00":
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.EDrakeStatus", "Alive")
            else:
                #print("Check")
                DragonSpawnTimerRemain = getTime(round(300-mainData['gameData']['gameTime']))
                if latestDragonkill == 0:
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.EDrakeStatus", "FirstSpawn")
            TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.EDrakeSpawnTimer", DragonSpawnTimerRemain)
            if canElderDragonSpawn:
                TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.EDrakeSpawnType", "Elder Dragon")
                ElderbuffTimeRemain = (150+latestDragonkill)-mainData['gameData']['gameTime']
                if ElderbuffTimeRemain > 0:
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.ElderDragonBuffTimer", getTime(ElderbuffTimeRemain))
            else:
                TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.EDrakeSpawnType", "Elemental Dragon")

            #           Baron RespawnTimer/Status
            latestBaronkill = 0
            BaronRespawnTimer = 0
            BaronSpawnTimerRemain = "00:00"
            if mainData['gameData']['gameTime'] >= 1200:
                for Baron in mainData['events']['Events']:
                    if Baron['EventName'] == "BaronKill":
                        latestBaronkill = Baron['EventTime']
                        BaronRespawnTimer = 360+latestBaronkill
                if mainData['gameData']['gameTime'] >= 1200 and latestBaronkill != 0:
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.BaronStatus", "Respawning")
                elif latestBaronkill == 0:
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.BaronStatus", "FirstSpawn")
                
                if latestBaronkill != 0 and mainData['gameData']['gameTime'] > 1200 and round(BaronRespawnTimer-mainData['gameData']['gameTime']) > 0:
                    BaronSpawnTimerRemain = getTime(round(BaronRespawnTimer-mainData['gameData']['gameTime']))
                else:
                    BaronSpawnTimerRemain = "00:00"
            else:
                BaronSpawnTimerRemain = getTime(round(1200-mainData['gameData']['gameTime']))
                TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.BaronStatus", "FirstSpawn")

            TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.BaronSpawnTimer", BaronSpawnTimerRemain)
            if BaronSpawnTimerRemain == "00:00":
                TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.BaronStatus", "Alive")
            
            if latestBaronkill != 0:
                buffTimeRemain = (180+latestBaronkill)-mainData['gameData']['gameTime']
                if buffTimeRemain > 0:
                    TPClient.stateUpdate("KillerBOSS.TP.Plugins.LoLPlugin.states.InGame.objective.BaronBuffTimer", getTime(buffTimeRemain))

# TP Start and End
@TPClient.on(TYPES.onConnect)
def TPStart(data):
    print(data)
    TPClient.settingUpdate("Assets Version", LeagueVersion)
    try:
        if requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0] != LeagueVersion:
            TPClient.settingUpdate("Need Asset Update?", "True")
        else:
            TPClient.settingUpdate("Need Asset Update?", "False")
    except:
        pass
    InGame()
    while True:
        if Http().lockfile != None:
            connector.start()
            break

@TPClient.on(TYPES.onAction)
def TPAction(data):
    http = Http()
    if http.lockfile != None:
        if data['actionId'] == "KillerBOSS.Plugin.LoLPlugin.actions.matchMaking.SelectSpell1&2":
            if data['data'][0]['value'] != data['data'][1]['value']:
                http.patch("/lol-champ-select/v1/session/my-selection",
                json={"spell1Id": SpellDict[data['data'][0]['value']], "spell2Id": SpellDict[data['data'][1]['value']]})

        if data['actionId'] == "KillerBOSS.Plugin.LoLPlugin.actions.SelectRole":
            if data['data'][0]['value'] != data['data'][1]['value']:
                http.put("/lol-lobby/v2/lobby/members/localMember/position-preferences", 
                json={
                    "firstPreference": data['data'][0]['value'],
                    "secondPreference": data['data'][1]['value']
                })
        if data['actionId'] == "KillerBOSS.Plugin.LoLPlugin.actions.PutUserinQueue":
            for queue in EnabledQueues:
                if queue['name'] == data['data'][0]['value']:
                    http.post("/lol-lobby/v2/lobby", json={"queueId" : queue['id']})

        if data['actionId'] == "KillerBOSS.Plugin.LoLPlugin.actions.startgame":
            http.post("/lol-lobby/v2/lobby/matchmaking/search")
            
        if data['actionId'] == "LoLPlugin.actions.CancelQueue":
            http.delete("/lol-matchmaking/v1/search")

        if data['actionId'] == "LoLPlugin.actions.QueueResponses":
            http.post(f"/lol-matchmaking/v1/ready-check/{data['data'][0]['value'].lower()}")
        if data['actionId'] == "KillerBOSS.Plugin.LoLPlugin.actions.MakeRunes":
            createRune(data['data'][1]['value'], data['data'][0]['value'])
@TPClient.on(TYPES.onListChange)
def TPListChange(data):
    print(data)

@async_to_sync
async def stopLoLConnection():
    print("LoL client shutting Down")
    await connector.stop()


@TPClient.on('closePlugin')
def Shutdown(data):
    global running
    running = False
    stopLoLConnection()
    TPClient.disconnect()
    os._exit(0)


print('Starting')
TPClient.connect()