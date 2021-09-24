# TouchPortal League of Legend Plugin
- [TouchPortal League of Legend Plugin](#touchportal-league-of-legend-plugin)
  - [Installation](#installation)
  - [Asset Update](#asset-update)
  - [Settings](#settings)
  - [Features](#features)
    - [Actions](#actions)
    - [States](#states)
  - [Suggestion & Bugs](#suggestion--bugs)
- [Contribute](#contribute)

## Installation
NOTE This Plugin is only made for Windows 10. It is possible for Mac OS user to use this Plugin but I will need some help with it.

1. The latest release can be downloaded [Here](https://github.com/KillerBOSS2019/TPLoLPlugin/releases)
2. You will need TouchPortal 2.1 for [Plugin support](https://www.touch-portal.com/blog/post/2020-03-09/New_in_release_version_2_1.php)
3. Now you will need to Import Plug-in should be on your Top Right Corner one of the Setting looking button
4. It should now popup a menu says if you would like to trust this plug-in click `Trust Always`. If this does not popup You may need to fully restart TouchPortal application.
5. The Plugin won't work just yet, That is because it require some missing data that is needed for Plugin to work.
6. Press `Win+R` and Copy&Paste `%appdata%\TouchPortal\plugins\TPLoLPlugin` 
7. You should see `ExtraData`, `Downloader-Main.exe`, `entry.tp`, `logo.ico`, `logo.png`, `riotgames.pem`, and main part `TPLoL.exe` If you're missing any of these Files/Folder It might be your Antivirus Software removed due to false virus. This depends on Antivirus Software but if you're using Windows Buildin software then windows should give you a notification and you can click on it and allow this file
8. After making sure all the files are there. Now we can start setting the Plug-in up
9. In that folder you should see a `Downloader-Main.exe` This little app will download the game assets like Champion Icons, map, champion data, and lots other stuff. So run this executable This will depends on your Internet speed for me it took less then 5 minutes. Remember never close it unless it's done otherwise you will get broken file.
10. After you run the `Downloader-Main.exe` It should create `DDragon` folder and `info.yml`. If it did not create ether of those file you will need to run the `Downloader-Main.exe` again.
11. Finally Your done setting it up congratulations! Now you will need to restart TP again after the setup. After that enjoy your game!

## Asset Update
INFO When League of Legend gets new update like adding new champ or buff and nerfs. the Plugin will not sync with the game anymore Therefore you need to update the assets.
To Update the assets follow these steps
1. You need to completly shutdown the Plugin and in Task Manager make sure TPLoL.exe isnt in the list if it is kill it
2. Press `Win+R` and enter `%appdata%\TouchPortal\plugins\TPLoLPlugin`.
3. You should see a `Downloader-Main.exe` executable in that folder.
4. Then run that file. This will delete old assets and replace with new one. It should say `Done` in console once it's done then your able to X out the window. 

## Settings
- `Language` This allows you to change the language of the data that gives to you in the states like Champion names there are Chinese name for it too. It has over 26 different languages.
- `Assets Version` This shows what is the current assets is made for (It's NOT CURRENT GAME VERSION)
- `Need Asset Update` This shows if there are any updates to the assets (Not Plugin Update It's Data Update) It will say `True` if is needs a update. And if you wish to update it follow #Asset Update

## Features

### Actions
- `Put User in Queue` This action put themself in a queue eg. Put you in a ranked match It does not start it.
- `Select 2 Roles` This will allow you to select the lane you wanted to play like `TOP` and `Bottom`.
- `Start a Match` This will just start the queue once your in a queue. If your not in a queue it wont start it
- `Cancel Queue` This will stop the matchmaking if are in searching state
- `Select Spell` This will allow you to select basic spells like `Flash` and `Ignite`
- `Create Rune` This will allow you create a rune page and set current.
  to use the action you will need to enter the rune name that you wanted to create. Then you wanted a Rune String.
  A rune string looks like `R3123S102111` basically `R3123` This parts means `Resolve`, 3rd Keystone, 1st Item, 2nd Item, and 3rd Item. And `S102` means Sorcery, 1st Item, empty on 2nd row, and 2nd Item slot in last row. `111` is the last part it means first Item, first Item, first Item.

### States
There is over 200 states Not going to list them all but i will list the groups
- `Summoner Info` Shows things about your Profile like `Display Name` and `Current Level`.
- `Match Making` This shows general things about match making like `Estimated Queue Time` and `Match Making States`.
- `Champion Select` This group shows banned Champion in Champ select. More coming soon!
- `In Game Runes` This group will show your current rune like `Primary Rune Tree` and `Secondary Rune Tree`.
- `In Game Events` This groups shows the events like `Latest event Name`, `Is Last Dragon Stolen?`, `Turret/Inhib Killer Name` etc...
- `In Game Spells` This shows your Spells like the `Spell One Name` and `Spell Two Name`.
- `In Game Game Data` This group shows general stuff like `Current Game mode` and `Current Game Time`.
- `In Game Scoreboard` This shows both Team Red and Blue team total KDA stats and Your own including CS, KDA, Kill, Assists, Wardscore and more.
- `In Game Champion Stats` Shows `current Health`, `life Steal`, `magic Resist` and much more.
- `In Game Champion Abilities` Shows champion abilities like Passive, Q, W, E, R all of them each one with Name, Level, Icon, Cost and Cooldown. 
- `In Game Items` This gives data like current game slot one Item name, Icon and more.
- `In Game Extra Data` this shows some data that is missing from other groups like current Gold, champion level, champion Name and more.
- `In Game Objective` This is a status for `Rift Herald`, `Drakes` and `Baron` for each one It has Status like First Spawn, Alive and Unobtainable. It also have a spawn Timer for each one. Also It has Baron Buff Timer and Elder Dragon Buff Timer as well!
Extra notes: This `In Game Objective` is Only made for normal matches like Ranked SR, Draft mode, etc... the Timer and status will not work for modes like `ONE FOR ALL`, `URF`, etc...
- `Friend Count` This shows your friends like how many friends are on mobile, Online, Offline etc...

## Suggestion & Bugs
If you have a Suggestion or found something isnt suppose to happend then Please Report or share your awsome idea [Here](https://github.com/KillerBOSS2019/TPLoLPlugin/issues/new/choose)

# Contribute
Feel free to suggest a pull request for new features, improvements, or documentation.
If you are not sure how to proceed with something, please start an Issue at the GitHub repository.