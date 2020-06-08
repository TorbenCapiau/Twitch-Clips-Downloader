import requests, os, argparse
from slugify import slugify

def DownloadClip(download_path, clip, filename, i):
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
    print("[SUCCESS] Saved as {}".format(filename))

# Create the parser
my_parser = argparse.ArgumentParser(description='Downloads your Twitch clips')

# Add the arguments
my_parser.add_argument('Username', metavar='username', type=str, help='Twitch channel you want to download clips from')
my_parser.add_argument('Limit', metavar='limit', type=int, help='Limit the amount of clips', default = None)

# Execute the parse_args() method
args = my_parser.parse_args()

Twitch_Username = args.Username
Clips_Limit = args.Limit

try:
    os.mkdir("./top-clips")
    print("[SUCCESS] Directory top-clips Created ") 
except FileExistsError:
    print("[INFO] Directory top-clips already exists")
try:
    os.mkdir("./top-clips/{}".format(Twitch_Username))
    print("[SUCCESS] Directory top-clips/{} Created ".format(Twitch_Username)) 
except FileExistsError:
    print("[INFO] Directory top-clips/{} already exists".format(Twitch_Username))

i = 1
cursor = None
nextPage = True
doneParsing = False
while not doneParsing:
    data = [{"operationName":"ClipsCards__User","variables":{"login":Twitch_Username,"limit":20, "cursor": cursor, "criteria":{"filter":"ALL_TIME"}},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"b73ad2bfaecfd30a9e6c28fada15bd97032c83ec77a0440766a56fe0bd632777"}}}]
    r = requests.post("https://gql.twitch.tv/gql", headers={"Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"}, json=data)
    nextPage = r.json()[0]['data']['user']['clips']['pageInfo']['hasNextPage']
    clips = r.json()[0]['data']['user']['clips']['edges']
    for clip in clips:
        if i <= Clips_Limit:
            DownloadClip("./top-clips/{}".format(Twitch_Username), clip, "{} - {} - {}".format(str(clip['node']['viewCount']), clip['node']['createdAt'].split('T')[0], clip['node']['title']), i)
            i = i + 1
        else:
            doneParsing = True
    if not r.json()[0]['data']['user']['clips']['pageInfo']['hasNextPage']:
        doneParsing = True
    cursor = clips[len(clips) - 1]['cursor']
    if doneParsing:
        print("[SUCCESS] Done. Fetched {} clips".format(int(i - 1)))