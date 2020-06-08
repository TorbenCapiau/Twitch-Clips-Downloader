import requests, argparse, os, unicodedata
from slugify import slugify
from time import sleep

download_path = "./downloads"
filesList = []

def MarkDone(slug):
    with open("done.txt", "a+") as myfile:
        myfile.write("{}\n".format(slug))

def AlreadyDownloaded(slug):
    with open('done.txt') as myfile:
        if slug in myfile.read():
            return True
    return False

def GetCuratorId(username, auth):
    data = [{"operationName":"ClipsManagerTable_User","variables":{"login":username,"limit":20,"criteria":{"sort":"CREATED_AT_DESC","period":"ALL_TIME","curatorID":"0"},"cursor":None},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"b300f79444fdcf2a1a76c101f466c8c9d7bee49b643a4d7878310a4e03944232"}}}]
    r = requests.post("https://gql.twitch.tv/gql", headers={"Authorization": "OAuth {}".format(auth), "Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"}, json=data)
    return r.json()[0]['data']['user']['id']

def DownloadClip(clip, filename, i):
    if not AlreadyDownloaded(clip['node']['slug']):
        filename = "{}-{}.mp4".format(str(i), slugify(filename))
        if "AT-cm" not in clip['node']['thumbnailURL']:
            if "offset" in clip['node']['thumbnailURL'] or "index" in clip['node']['thumbnailURL']:
                video_id = clip['node']['thumbnailURL'].split('/')[3].split('-')[0]
                offset = clip['node']['thumbnailURL'].split('/')[3].split('-')[2]
                if len(clip['node']['thumbnailURL'].split('/')[3].split('-')) > 5:
                    if "vod" in clip['node']['thumbnailURL'].split('/')[3]:
                        clip_url = "https://{}/vod-{}-offset-{}.mp4".format(clip['node']['thumbnailURL'].split('/')[2], clip['node']['thumbnailURL'].split('/')[3].split('-')[1], clip['node']['thumbnailURL'].split('/')[3].split('-')[3])
                    else:
                        clip_url = "https://{}/{}-offset-{}-{}.mp4".format(clip['node']['thumbnailURL'].split('/')[2], str(video_id), clip['node']['thumbnailURL'].split('/')[3].split('-')[2], clip['node']['thumbnailURL'].split('/')[3].split('-')[3])
                else:
                    clip_url = "https://{}/{}-offset-{}.mp4".format(clip['node']['thumbnailURL'].split('/')[2], str(video_id), str(offset))
            else:
                clip_url = "https://{}/{}.mp4".format(clip['node']['thumbnailURL'].split('/')[2], clip['node']['thumbnailURL'].split('/')[3].split('-')[0])
        else:
            if "AT-cm" in clip['node']['thumbnailURL']:
                clip_url = "https://{}/AT-{}.mp4".format(clip['node']['thumbnailURL'].split('/')[2], clip['node']['thumbnailURL'].split('/')[3].split('-')[1])
        if "-index-" in clip['node']['thumbnailURL']:
            clip_url = clip_url.replace("-offset-", "-index-")
        r = requests.get(clip_url)
        with open("{}/{}".format(download_path, filename), 'wb') as f:
            f.write(r.content)
        MarkDone(clip['node']['slug'])
        print("[SUCCESS] Saved as {}".format(filename))
    else:
        print("[SKIPPED] Already downloaded this file ({})".format(filename))

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
    print("[SUCCESS] Directory " , download_path ,  " Created ") 
except FileExistsError:
    print("[INFO] Directory " , download_path ,  " already exists")

doneParsing = False
curatorId = GetCuratorId(Twitch_Username, Twitch_Auth)
limit_increase = 20
currentCount = 0
cursor = None
i = 0

print("[SUCCESS] Authenticated, curator ID: {}".format(curatorId))
data = [{"operationName":"ClipsManagerTable_User","variables":{"login":Twitch_Username,"limit":limit_increase,"criteria":{"sort":"CREATED_AT_DESC","period":"ALL_TIME","curatorID":curatorId},"cursor":cursor},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"b300f79444fdcf2a1a76c101f466c8c9d7bee49b643a4d7878310a4e03944232"}}}]
MarkDone("")
while not doneParsing:
    r = requests.post("https://gql.twitch.tv/gql", headers={"Authorization": "OAuth {}".format(Twitch_Auth), "Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"}, json=data)
    if "errors" not in r.json()[0]:
        currentCount = currentCount + limit_increase
        clips = r.json()[0]['data']['user']['clips']['edges']
        cursor = clips[len(clips) - 1]['cursor']
        data = [{"operationName":"ClipsManagerTable_User","variables":{"login":Twitch_Username,"limit":limit_increase,"criteria":{"sort":"CREATED_AT_DESC","period":"ALL_TIME","curatorID":curatorId},"cursor":str(cursor)},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"b300f79444fdcf2a1a76c101f466c8c9d7bee49b643a4d7878310a4e03944232"}}}]
        for clip in clips:
            i = i + 1
            channelName = "channel"
            try:
                channelName = clip['node']['broadcaster']['displayName']
            except:
                pass
            print("[INFO] Found clip: {} on {} ({})".format(clip['node']['title'], channelName, clip['node']['url']))
            DownloadClip(clip, "{} - {} - {}".format(clip['node']['createdAt'].split('T')[0], channelName, clip['node']['title']), i)
        if not r.json()[0]['data']['user']['clips']['pageInfo']['hasNextPage']:
            doneParsing = True
            print("[SUCCESS] Done. Fetched {} clips".format(currentCount))
    else:
        if r.json()[0]['errors'][0]['message'] == "service timeout":
            print("[TIMEOUT] Received rate-limit, waiting 5 seconds...")
            sleep(5)