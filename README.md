# StatusBot

StatusBot is a Discord bot that will consistently ping a desired website or IP address and send out updates whenever the server is responding abnormally slow or is unresponsive.

## Self-Hosting

### Prerequisites

In order to run StatusBot you'll need a server with the following:

- Python 3.0 or higher
- The following modules: discord, asyncio, pymongo, pingparsing, requests-async
- A MongoDB Community Server
- A Discord bot token
- An IQ of 5 or higher

### Clone

Clone this repository onto your server.

### Config.json

Create a new file in StatusBot's directory called "config.json" (case-sensitive). In this file add the following (pseudo-json is marked with <>):

```
{
    "token":"<bot token>",
    "prefix":"<prefix",
    "mongo_url":"<MongoDB URL>",
    "instance_name":"<name>"
}
```

### Run

Go to the StatusBot directory and use `python main.py`. 