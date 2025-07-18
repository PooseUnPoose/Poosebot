# Installation
```bash
git clone git@github.com:PooseUnPoose/Poosebot.git
cd Poosebot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
touch .env
```
Then insert the following into the .env file:
```txt
TOKEN = ""
CHANNEL_ID = ""
TIMETABLE_LINK = ""
```
Fill in the relevant information with the corresponding variables as such

```txt
TOKEN = "YOURDISCORDCLIENTTOKEN"
CHANNEL_ID = "TheIdForTheChannelToPostIn"
TIMETABLE_LINK = "https://TheLinkToTheUFVTimeTable.com"
```
