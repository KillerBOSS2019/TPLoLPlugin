from .HTTP import Http


def getAvailableQueue():
    http = Http()
    if http.lockfile != None:
        queues = http.get("/lol-game-queues/v1/queues").json()
        newQueueList = []
        print(queues)
        for queue in queues:
            if "Tutorial" not in queue['name'].split() and queue['queueAvailability'] == "Available" and queue['description'] != "Tutorial":
                if queue['type'] != "BOT":
                    newQueueList.append({"id": queue['id'], "name": queue['detailedDescription'] if queue['detailedDescription'] else queue['shortName']})
                elif queue['type'] == "BOT":
                    newQueueList.append({"id": queue['id'], "name": "CO-OP VS. AI "+queue['shortName']})
        return newQueueList
    else:
        return []
