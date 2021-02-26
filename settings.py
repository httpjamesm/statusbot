import json,pymongo,discord
try:
    # Load config.json
    with open('config.json', 'r') as config_file:
        # Define its contents as configdata
        configdata = json.load(config_file)
except:
    print("[ERROR] Invalid config.json file! Exiting now.")
    exit()

print("[Start] Config.json loaded")

try:
    # Connect to MongoDB server
    myclient = pymongo.MongoClient(configdata["mongo_url"])
except:
    print("[ERROR] There was an error connecting to MongoDB. Invalid URL in config.json maybe? Exiting now.")
    exit()
# Define the main database and collections as variables
db = myclient["statusbot"]
col = db["data"]

print("[Start] Database and collections defined")