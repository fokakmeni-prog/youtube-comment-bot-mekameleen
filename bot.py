import os
import random
import re
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

CHANNEL_ID = "UCHcGPyxfYfEZsjMcC4zfbgw"

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

SHORT_COMMENTS = [
"""📌 لو المقطع شدّك، تابع القناة من هنا:
الرابط الرسمي:
https://www.youtube.com/channel/UCHcGPyxfYfEZsjMcC4zfbgw

ولا تنس الاشتراك وتفعيل الجرس 👇""",

"""⚡ شورت سريع… لكن المقاطع الكاملة على القناة أعمق وأكثر تفصيلًا.
الرابط الرسمي:
https://www.youtube.com/channel/UCHcGPyxfYfEZsjMcC4zfbgw

اشترك وشاركنا رأيك 👇""",

"""🎯 إذا أعجبك هذا الشورت، فالمحتوى القادم على القناة سيفيدك أكثر.
الرابط الرسمي:
https://www.youtube.com/channel/UCHcGPyxfYfEZsjMcC4zfbgw

ما أول انطباع عندك؟ 👇""",

"""🔥 محتوى مختصر ومباشر… وللمزيد تابع القناة من هنا:
الرابط الرسمي:
https://www.youtube.com/channel/UCHcGPyxfYfEZsjMcC4zfbgw

هل تريد شورتات أكثر بهذا الأسلوب؟ 👇"""
]

SHORT_VIDEO_COMMENTS = [
"""📌 إذا شاهدت هذا المقطع، فلا تفوّت بقية المحتوى على القناة.
الرابط الرسمي:
https://www.youtube.com/channel/UCHcGPyxfYfEZsjMcC4zfbgw

اشترك ليصلك كل جديد 👇""",

"""🎯 هذا النوع من المقاطع يختصر الفكرة بسرعة، لكن المتابعة المستمرة تصنع فرقًا.
الرابط الرسمي:
https://www.youtube.com/channel/UCHcGPyxfYfEZsjMcC4zfbgw

شاركنا رأيك 👇""",

"""⭐ إذا وصلك محتوى هذا المقطع، تابع القناة من هنا:
الرابط الرسمي:
https://www.youtube.com/channel/UCHcGPyxfYfEZsjMcC4zfbgw

هل تتفق مع ما ورد؟ 👇""",

"""🧭 مقطع قصير… لكن فيه رسالة مهمة.
الرابط الرسمي:
https://www.youtube.com/channel/UCHcGPyxfYfEZsjMcC4zfbgw

اكتب لنا رأيك بصراحة 👇"""
]

LONG_VIDEO_COMMENTS = [
"""📌 إذا وصلت إلى هنا، فالمقطع أكيد يستحق المتابعة حتى النهاية.
الرابط الرسمي:
https://www.youtube.com/channel/UCHcGPyxfYfEZsjMcC4zfbgw

اشترك وقل لنا: ما أبرز نقطة لفتت انتباهك؟ 👇""",

"""🎥 المقاطع الكاملة تصنع الفرق، لأنها تشرح ما لا يظهر في المقاطع السريعة.
الرابط الرسمي:
https://www.youtube.com/channel/UCHcGPyxfYfEZsjMcC4zfbgw

ما تقييمك لهذا المقطع من 10؟ 👇""",

"""🧠 إذا شاهدت المقطع كاملًا، فأنت فعلًا مهتم بالمحتوى الجاد.
الرابط الرسمي:
https://www.youtube.com/channel/UCHcGPyxfYfEZsjMcC4zfbgw

ما أكثر جزئية أثرت فيك؟ 👇""",

"""📍 هذا المقطع جزء من صورة أكبر، ومتابعتك المستمرة تصنع فارقًا.
الرابط الرسمي:
https://www.youtube.com/channel/UCHcGPyxfYfEZsjMcC4zfbgw

ما أهم سؤال تركه هذا المقطع عندك؟ 👇"""
]

BOT_SIGNATURE = "الرابط الرسمي:"


def iso_duration_to_seconds(duration):
    pattern = re.compile(
        r'PT'
        r'(?:(\d+)H)?'
        r'(?:(\d+)M)?'
        r'(?:(\d+)S)?'
    )
    match = pattern.match(duration)

    if not match:
        return 0

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


def choose_comment(duration):
    if duration < 90:
        return random.choice(SHORT_COMMENTS)
    elif duration < 240:
        return random.choice(SHORT_VIDEO_COMMENTS)
    else:
        return random.choice(LONG_VIDEO_COMMENTS)


def already_commented(youtube, video_id):
    comments = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=50,
        textFormat="plainText"
    ).execute()

    for item in comments.get("items", []):
        text = item["snippet"]["topLevelComment"]["snippet"].get("textDisplay", "")
        if BOT_SIGNATURE in text:
            return True

    return False


creds = Credentials(
    None,
    refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.environ["YOUTUBE_CLIENT_ID"],
    client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
    scopes=SCOPES,
)

creds.refresh(Request())
youtube = build("youtube", "v3", credentials=creds)

search = youtube.search().list(
    part="snippet",
    channelId=CHANNEL_ID,
    order="date",
    maxResults=10,
    type="video"
).execute()

video_ids = []
for item in search.get("items", []):
    video_id = item.get("id", {}).get("videoId")
    if video_id:
        video_ids.append(video_id)

if not video_ids:
    print("لا يوجد فيديوهات حديثة")
    raise SystemExit(0)

videos = youtube.videos().list(
    part="contentDetails",
    id=",".join(video_ids)
).execute()

video_map = {}

for item in videos.get("items", []):
    video_id = item.get("id")
    content_details = item.get("contentDetails", {})
    duration_text = content_details.get("duration")

    if not video_id or not duration_text:
        continue

    duration = iso_duration_to_seconds(duration_text)
    video_map[video_id] = duration

target_video = None
target_comment = None

for vid in video_ids:
    if vid not in video_map:
        continue

    if already_commented(youtube, vid):
        continue

    duration = video_map[vid]
    target_video = vid
    target_comment = choose_comment(duration)
    break

if not target_video:
    print("لا يوجد فيديو جديد للتعليق عليه")
    raise SystemExit(0)

youtube.commentThreads().insert(
    part="snippet",
    body={
        "snippet": {
            "videoId": target_video,
            "topLevelComment": {
                "snippet": {
                    "textOriginal": target_comment
                }
            }
        }
    }
).execute()

print("تم نشر التعليق بنجاح")
