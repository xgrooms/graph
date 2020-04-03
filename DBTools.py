import pyorient
import json

def reset_db(client, name):

   # Remove Old Database
   if client.db_exists(name):
    client.db_drop(name)

   # Create New Database
   client.db_create(name,
      pyorient.DB_TYPE_GRAPH,
      pyorient.STORAGE_TYPE_PLOCAL)

def getrid(client,id):
    nodeId = client.query("SELECT FROM V WHERE id = '" + str(id) + "'")
    return str(nodeId[0]._rid)

def printJSONDB(filepath):

    with open(filepath) as f:
        data = json.load(f)

    for key in data:
        name = data.get(key).get("name")
        wikiUrl = data.get(key).get("wikiUrl")
        wikiImage = data.get(key).get("wikiImage")
        degreeLists = data.get(key).get("degreeLists")

#         print("json key:\t\t" + key)
#         print("name:\t\t\t" + name)

#         #Most people are on Wikipedia, but not everyone
#         if wikiUrl is not None:
#             print("wikiUrl:\t\t" + wikiUrl)
#         if wikiImage is not None:
#             print("wikiImage:\t\t" + wikiImage)

#         print("degreeLists:\t", end=" ")
#         print(degreeLists)
#         print("")

def loadDB(filepath):

    #database name
    dbname = "agen"
    #database login is root by default
    login = "root"
    #database password, set by docker param
    password = "rootpwd"

    #create client to connect to local orientdb docker container
    client = pyorient.OrientDB('172.31.147.140', 2424)
    session_id = client.connect(login, password)

    #remove old database and create new one
    reset_db(client,dbname)

    #open the database we are interested in
    client.db_open(dbname, login, password)
    client.command("CREATE CLASS Person Extends V")
    client.command("CREATE PROPERTY Person.id Integer")
    client.command("CREATE PROPERTY Person.name String")
    #client.command("CREATE PROPERTY Person.students Integer")
    #client.command("CREATE PROPERTY Person.advisors Integer")
    client.command("CREATE PROPERTY Person.wikiUrl String")
    client.command("CREATE PROPERTY Person.wikiImg String")
    client.command("CREATE PROPERTY Person.DegLists String")
    

    #open and parse local json file
    with open(filepath) as f:
        data = json.load(f)

    #loop through each key in the json database and create a new vertex, V with the id in the database
    for key in data:
        name = data.get(key).get("name") #NEED THIS 
        #student = data.get(key)["students"]
        #advisor = data.get(key)["advisors"]

        if data.get(key).get("wikiUrl") is None:
            wikiUrl = ''
        else:
            wikiUrl = data.get(key).get("wikiUrl")

        if data.get(key).get("wikiImage") is None:
            wikiImg = ''
        else:
            wikiImg = data.get(key).get("wikiImage")
        
        if data.get(key).get("degreeLists") is None:
            degLists = ''
        else:
            degLists = data.get(key).get("degreeLists")

        #name = re.sub("'", "", data.get(key).get("name"))

        #print("CREATE VERTEX Person SET id = '" + key + "', name = '" + name + "', wikiUrl = '" + wikiUrl + "'")
        #print("CREATE VERTEX Person SET id = '" + key + "', name = '" + name + "', wikiUrl = '" + wikiUrl + "', wikiImg = '" + wikiImg + "', Degree Lists = '" + degLists + "'")
        client.command("CREATE VERTEX Person SET id = '" + key + "', name = '" + name + "', wikiUrl = '" + wikiUrl + "'")

    #loop through each key creating edges from advisor to advise
    for key in data:
        advisorNodeId = str(getrid(client,key))
        print("AdvisorNodeId = '" + advisorNodeId + "'")
        for student in data.get(key)["students"]:
            studentNodeId = str(getrid(client,student))
            #print("CREATE EDGE FROM " + advisorNodeId + " TO " + studentNodeId + "'")
            #client.command("CREATE EDGE FROM " + advisorNodeId + " TO " + studentNodeId + "'")

    client.close()

def shortestPath(personIdA, personIdB):

    #personId[A/B] is the V id, which matches the id in the JSON file
    #personNodeId[A/B] is the internal OrientDB node ids (rid), which are used for functions like shortestPath

    dbname = "agen"
    login = "root"
    password = "rootpwd"

    client = pyorient.OrientDB("172.31.147.140", 2424)
    session_id = client.connect(login, password)

    client.db_open(dbname, login, password)

    #get the RID of the two people
    personNodeIdA = getrid(client,personIdA)
    personNodeIdB = getrid(client,personIdB)

    #determine the shortest path
    pathlist = client.command("SELECT shortestPath(" + personNodeIdA + ", " + personNodeIdB +")")
    #print(pathlist[0].__getattr__('shortestPath'))

    #get distance
    distance = len(pathlist[0].__getattr__('shortestPath'))

    for node in pathlist[0].__getattr__('shortestPath'):
        print(node)

    #pyorient.otypes.OrientRecord
    client.close()
    return distance
