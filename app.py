import requests, argparse, base64, os, unicodedata
from slugify import slugify

download_path = "./downloads"

def GetCuratorId(username, auth):
    data = [{"operationName":"ClipsManagerTable_User","variables":{"login":username,"limit":20,"criteria":{"sort":"CREATED_AT_DESC","period":"ALL_TIME","curatorID":"0"},"cursor":None},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"b300f79444fdcf2a1a76c101f466c8c9d7bee49b643a4d7878310a4e03944232"}}}]
    r = requests.post("https://gql.twitch.tv/gql", headers={"Authorization": "OAuth {}".format(auth), "Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"}, json=data)
    return r.json()[0]['data']['user']['id']

def DownloadClip(clip, filename):
    filename = "{}.mp4".format(slugify(filename))
    if "AT-cm" not in clip['node']['thumbnailURL']:
        video_id = clip['node']['thumbnailURL'].split('/')[3].split('-')[0]
        offset = clip['node']['thumbnailURL'].split('/')[3].split('-')[2]
        clip_url = "https://{}/{}-offset-{}.mp4".format(clip['node']['thumbnailURL'].split('/')[2], str(video_id), str(offset))
    else:
        clip_url = "https://{}/AT-{}.mp4".format(clip['node']['thumbnailURL'].split('/')[2], clip['node']['thumbnailURL'].split('/')[3].split('-')[1])
    r = requests.get(clip_url)
    with open("{}/{}".format(download_path, filename), 'wb') as f:
        f.write(r.content)
    print("[SUCCESS] Saved as {}".format(filename))

# Create the parser
my_parser = argparse.ArgumentParser(description='Downloads your Twitch clips')

# Add the arguments
my_parser.add_argument('Username', metavar='username', type=str, help='Your twitch username')
my_parser.add_argument('Auth', metavar='auth', type=str, help='Twitch.tv oAuth Authorization header value')

# Execute the parse_args() method
args = my_parser.parse_args()

Twitch_Username = args.Username
Twitch_Auth = args.Auth

# Create downloads directory
try:
    os.mkdir(download_path)
    print("Directory " , download_path ,  " Created ") 
except FileExistsError:
    print("Directory " , download_path ,  " already exists")

doneParsing = False
curatorId = GetCuratorId(Twitch_Username, Twitch_Auth)
limit_increase = 20
currentCount = 0
cursor = None

print("[SUCCESS] Authenticated, curator ID: {}".format(curatorId))
data = [{"operationName":"ClipsManagerTable_User","variables":{"login":Twitch_Username,"limit":limit_increase,"criteria":{"sort":"CREATED_AT_DESC","period":"ALL_TIME","curatorID":curatorId},"cursor":cursor},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"b300f79444fdcf2a1a76c101f466c8c9d7bee49b643a4d7878310a4e03944232"}}}]

while not doneParsing:
    r = requests.post("https://gql.twitch.tv/gql", headers={"Authorization": "OAuth {}".format(Twitch_Auth), "Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"}, json=data)
    currentCount = currentCount + limit_increase
    cursor = base64.b64encode(str(currentCount).encode('ascii')).decode("utf-8", "ignore")
    clips = r.json()[0]['data']['user']['clips']['edges']
    data = [{"operationName":"ClipsManagerTable_User","variables":{"login":Twitch_Username,"limit":limit_increase,"criteria":{"sort":"CREATED_AT_DESC","period":"ALL_TIME","curatorID":curatorId},"cursor":str(cursor)},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"b300f79444fdcf2a1a76c101f466c8c9d7bee49b643a4d7878310a4e03944232"}}}]
    for clip in clips:
        print("[INFO] Found clip: {} on {} ({})".format(clip['node']['title'], clip['node']['broadcaster']['displayName'], clip['node']['url']))
        DownloadClip(clip, "{} - {} - {}".format(clip['node']['createdAt'].split('T')[0], clip['node']['broadcaster']['displayName'], clip['node']['title']))
    if len(clips) < limit_increase:
        doneParsing = True
        print("[SUCCESS] Done. Fetched {} clips".format(currentCount))