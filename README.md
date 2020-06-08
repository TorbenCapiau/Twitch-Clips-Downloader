# Twitch clips downloader

Downloads all clips made by you of various streamers to a local directory
![Tool](result.png)

## Why?
Many streamers have received copyright complaints over their Twitch clips and are forced to remove all their clips

## Prerequisites
- Python 3
- pip

## How to use
1. Sign in on [Twitch](https://twitch.tv) using Chrome/Firefox
2. Go to inspect element -> Application tab
3. Go to cookies and copy the auth-token value
![Cookies](cookies.png "Find auth-token cookie value")
4. Run the tool by supplying your username and the auth-token value as seen below

## Installation & usage
```bash
pip install -r requirements.txt
python app.py --username <Twitch username> --auth <auth-token value>
```