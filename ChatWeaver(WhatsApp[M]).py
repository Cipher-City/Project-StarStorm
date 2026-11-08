import sys
import time
from pathlib import Path
from html import escape
import re
from urllib.parse import quote
from PIL import Image
from hashlib import md5
import tkinter as tk
from tkinter import messagebox

self_path = Path(__file__)

title = "Message from Project-StarStorm"
body = f"""Before we begin, we would like to inform you of exactly what this program does.
{self_path.name} may:
    • Read files in the parent folder 
    • Write files in the parent folder 
    • Process the export files in deterministic, pre-programmed ways
    • Adapt to broken exports with missing files as much as possible 
        
{self_path.name} will NOT:
    • Alter your data
    • Delete your data
    • Leak your data
    • Transmit your data over the network
    • Comrehend the context of your chat conversation in any inteligent, invasive, or intrusive way
    • Evolve, change, or modify the way it processes your data without you programming new intuctions

Note for user: please make sure {self_path.name} is in the same folder as the media files and conversation transcript

Do you consent to this process?"""

base = tk.Tk()

base.withdraw()

user_consent = messagebox.askyesno(title=title,message=body,icon="info",default="no",parent=base)

base.destroy()

if not user_consent:
    print("Operation cancelled. No conversion was started.")
    time.sleep(5)
    raise SystemExit

print("Consent granted. Starting conversion...")
time.sleep(5)

root = Path(__file__).parent
log = root / "Error Log.txt"
transcripts = list(root.glob("WhatsApp Chat with *.txt"))
if transcripts == []:
    with open(log, "a") as report:
        report.write("\nNo transcript was found")
    sys.exit()
if len(transcripts) == 1:
    script = transcripts[0]
if len(transcripts) > 1:
    options = []
    for transcript in transcripts:
        options.append(transcript.name)
    while True:
        chosen = input(f"which one of these items is the intended transcript | {options}:")
        if chosen in options:
            script = root / chosen
            break
        print(f"{chosen} is not a valid option, please try again")
        time.sleep(2)
output = script.with_suffix(".html")


indent = "    "
depth = 2
century = str(time.localtime().tm_year)[:2]

media_types = {
    "image": [
        ".apng",
        ".avif",
        ".bmp",
        ".gif",
        ".ico",
        ".jfif",
        ".jpeg",
        ".jpg",
        ".png",
        ".svg",
        ".webp",
    ],

    "video": [
        ".mp4",
        ".m4v",
        ".ogv",
    ],

    "audio": [
        ".aac",
        ".flac",
        ".m4a",
        ".mp3",
        ".oga",
        ".ogg",
        ".opus",
        ".wav",
    ],

    "document": [
        ".html",
        ".htm",
        ".pdf",
        ".txt",
        ".xhtml",
        ".webm",
        ".py",
        ".json",
    ],
}

url_prefixes = [
    "http://",
    "https://",
    "ftp://",
    "ftps://",
    "file:///",
    "data:",
]

system_attachments = [
    " <This message was edited>",
    "You deleted this message",
    "live location shared",
]

attachment_types = {
    " <This message was edited>": f"""system-attachment""",
    "You deleted this message": f"""system-alert""",
    "live location shared": f"""system-attachment""",
}

with open(script, "r", encoding="utf-8") as file:
    chat = file.read()

patterns = {
    "continuations": "\\n(?!\\d\\d?/\\d\\d?/\\d{2}, \\d{2}:\\d{2} - )",
    "names": "\\n\\d\\d?/\\d\\d?/\\d{2}, \\d{2}:\\d{2} - (.*?): ",
    "links": ".*?(?=\\s|$)"
}

chat = re.sub(patterns["continuations"], lambda match: "\\c", chat)
voices = re.findall(patterns["names"],chat)

participant_message_type = {}

participant_list = []

for voice in voices:
    if voice not in participant_list and isinstance(voice, str):
        participant_list.append(voice)
        participant_message_type[voice] = "received"
while True:
    user_name = input(f"which one of these names is yours(or enter \"anno\" to remain anonymous) | {participant_list}:")
    if user_name in participant_list:
        participant_message_type[user_name] = "sent"
        break
    if user_name == "anno" and not (user_name in participant_list):
        for iden in participant_list:
            participant_message_type[iden] = "anno"
        break
    print(f"{user_name} is not a participant name or \"anno\", please try again")
    time.sleep(2)
chat_lines = chat.splitlines()

headers = [
    "Messages to yourself are end-to-end encrypted. No one else, not even WhatsApp, can read, listen to, or share them. *Learn more*",
    "Messages to yourself are end-to-end encrypted. No one else, not even WhatsApp, can read, listen to, or share them. Learn more.",
    "Messages and calls are end-to-end encrypted. Only people in this chat can read, listen to, or share them. *Learn more*",
]

header = chat_lines[0]

del chat_lines[0]

header_info = {
    "data": {
        "date": {},
        "time": {},
    },
}

header_split = header.split(" - ",1)
header_stamp = header_split[0].split(", ")
header_date = header_stamp[0].split("/")
header_time = header_stamp[1].split(":")

header_info["data"]["date"]["month"] = f"{"0"*(2 - len(header_date[0]))}{header_date[0]}"
header_info["data"]["date"]["day"] = f"{"0"*(2 - len(header_date[1]))}{header_date[1]}"
header_info["data"]["date"]["year"] = f"{century}{"0"*(2 - len(header_date[2]))}{header_date[2]}"
header_info["data"]["time"]["hour"] = header_time[0]
header_info["data"]["time"]["minute"] = header_time[1]

header_info["contents"] = header_split[1]

try:
    assert header_info["contents"] in headers
except AssertionError:
    with open(output.with_suffix(".md"), "a") as report:
        report.write("\nThis transcript appears to have been altered or corrupted")
    sys.exit()

used_ids = []

output_header = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{escape(output.stem)}</title>

    <style>
        html {{
            scroll-behavior: smooth;
            scrollbar-width: none;
        }}

        body {{
            font-family: Arial, sans-serif;
            background: #0f0f0f;
            padding: 20px;
            margin: 0;
        }}

        .chat {{
            max-width: 65%;
            margin: auto;
            padding: 20px;
        }}

        .message {{
            background: #222;
            color: white;
            max-width: 60%;
            padding: 10px;
            margin: 8px 0;
            border-radius: 8px;
            overflow-wrap: anywhere;
        }}

        .received {{
            margin-right: auto;
        }}

        .sent {{
            margin-left: auto;
        }}

        .anno {{
            margin-right: auto;
            margin-left: auto;
            text-align: center;
        }}

        .system-update {{
            color: #aaa;
            background: #333;
            max-width: 80%;
            margin: 15px auto;
            padding: 8px 12px;
            border-radius: 8px;
            text-align: center;
            font-size: 0.9em;
        }}

        .timestamp {{
            color: #777;
            font-size: 0.85em;
            font-family: 'Courier New', Courier, monospace;
        }}

        .sender {{
            font-weight: bold;
            color: #08f;
        }}

        .system-message {{
            font-size: 1.2em;
            font-weight: bold;
            background: #333;
            color: #fff;
            padding: 15px;
            margin: 15px 0;
            border-radius: 8px;
        }}

        .media-omitted {{
            color: red;
            font-weight: bold;
            font-family: 'Courier New', Courier, monospace;
        }}

        .empty-line {{
            color: #b88600;
            background: yellow;
            font-weight: bold;
            font-family: 'Courier New', Courier, monospace;
        }}

        .url {{
            color: blue;
        }}

        .attached-image {{
            max-width: 100%;
            max-height: 300px;
            color: red;
            font-weight: bold;
            font-family: 'Courier New', Courier, monospace;
            margin: 5px auto;
        }}

        .attached-video {{
            max-width: 100%;
            max-height: 300px;
            margin: 5px auto;
        }}

        .attached-audio {{
            max-width: 100%;
            margin: 5px auto;
        }}
        
        .attached-document {{
            color: orange;
            font-family: Consolas, "Courier New", monospace;
        }}

        .attached-file {{
            color: magenta;
            font-family: Consolas, "Courier New", monospace;
        }}

        .item-name {{
            color: #0f0;
            font-family: Consolas, "Courier New", monospace;
        }}

        .system-attachment {{
            color: #aaa;
            font-family: Consolas, "Courier New", monospace;
            font-size: smaller;
        }}

        .media-item {{
            border: 2px solid white;
            padding: 5px 10px;
            margin-top: 5px;
            margin-bottom: 5px;
            border-radius: 10px;
        }}

        .system-alert {{
            color: red;
            font-family: Consolas, "Courier New", monospace;
            font-size: smaller;
        }}

        .system-note {{
            color: yellow;
            font-family: Consolas, "Courier New", monospace;
            font-size: smaller;
        }}

        .star {{
            background: local;
            border: 2px dotted #fc0;
            color: #fc0;
            font-weight: bolder;
            padding: 10px 10px 10px 10px;
            font-size: larger;
            margin: 5px 5px 5px 5px;
        }}

        .icon {{
            display: inline-block;
            background: local;
            border: 2px dotted #08f;
            font-weight: bolder;
            padding: 10px;
            font-size: larger;
            margin: 5px;
        }}

        .icon:hover {{
            cursor: help;
        }}

        .icon-container {{
            text-align: center;
            display: block;
            width: fit-content;
            margin-left: auto;
        }}

        html::-webkit-scrollbar {{
            display: none;
        }}

        .custom-scrollbar {{
            position: fixed;
            top: 0;
            right: 0;

            width: 16px;
            height: 100vh;

            background: #111;

            z-index: 1000;
        }}

        .scroll-thumb {{
            position: absolute;

            top: 0;
            right: 0;

            width: 100%;

            background: #555;
            border-radius: 8px;

            cursor: grab;
        }}

        .scroll-thumb:active {{
            cursor: grabbing;
        }}

        .scroll-marker {{
            position: absolute;

            width: 6px;
            height: 6px;

            left: 5px;

            border-radius: 50%;

            pointer-events: none;
        }}

        .favourite-marker {{
            background: #fc0;
        }}

        .duplicate-marker {{
            background: #08f;
        }}
    </style>
    <script>
        const icons = ["data:image/svg+xml;utf8,%3Csvg%20width%3D%2250%22%20height%3D%2250%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cpolygon%20points%3D%225%2C5%2045%2C5%2045%2C45%2025%2C35%205%2C45%22%20stroke%3D%22%23fb0%22%20stroke-width%3D%222%22%20fill%3D%22%230000%22%2F%3E%3C%2Fsvg%3E","data:image/svg+xml;utf8,%3Csvg%20width%3D%2250%22%20height%3D%2250%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cpolygon%20points%3D%225%2C5%2045%2C5%2045%2C45%2025%2C35%205%2C45%22%20stroke%3D%22%23fb0%22%20stroke-width%3D%221%22%20fill%3D%22%23fb0%22%2F%3E%3C%2Fsvg%3E"];
        const copy_stamp = "data:image/svg+xml;utf8,%3Csvg%20width%3D%2250%22%20height%3D%2250%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cpath%20d%3D%22M18%2012H10V40H38V32%22%20fill%3D%22none%22%20stroke%3D%22%2308f%22%20stroke-width%3D%223%22%2F%3E%3Cpath%20d%3D%22M22%2010H40V28H22Z%22%20fill%3D%22none%22%20stroke%3D%22%2308f%22%20stroke-width%3D%223%22%2F%3E%3Cpath%20d%3D%22M27%2019L35%2019M35%2019L31%2015M35%2019L31%2023%22%20fill%3D%22none%22%20stroke%3D%22%2308f%22%20stroke-width%3D%222%22%2F%3E%3C%2Fsvg%3E";

        /**
        * @param {{string}} iden
        */
        
        function toggleIcon(iden) {{
            const message = document.getElementById(iden);
            const button = message.querySelector("button");
            const image = button.querySelector("img");

            if (image.src === icons[0]) {{
                image.src = icons[1];
                image.title = "Click to unfavorite this message";
                localStorage.setItem(iden, "1");

                const messagePosition = message.offsetTop;
                const documentHeight = document.documentElement.scrollHeight;
                const viewportHeight = window.innerHeight;
                const scrollableHeight = documentHeight - viewportHeight;
                const pos = ((messagePosition / documentHeight) * (viewportHeight - (viewportHeight / documentHeight * viewportHeight))) + ((viewportHeight / documentHeight * viewportHeight)/2) - 2;
                const marker = document.createElement("div");
                marker.className = "scroll-marker favourite-marker";
                marker.style.top = `${{pos}}px`;
                marker.id = `marker-${{iden}}`;
                document.querySelector(".custom-scrollbar").appendChild(marker);
            }} else {{
                image.src = icons[0];
                image.title = "Click to favorite this message";
                localStorage.setItem(iden, "0");
                const marker = document.body.querySelector(".custom-scrollbar").querySelector(`#marker-${{iden}}`);
                marker.remove();
            }}
        }}

        function highLight(orig) {{
            const origin = document.getElementById(orig);
            const originPosition = origin.offsetTop;
            const documentHeight = document.documentElement.scrollHeight;
            const viewportHeight = window.innerHeight;
            const scrollableHeight = documentHeight - viewportHeight;
            const pos = ((originPosition / documentHeight) * (viewportHeight - (viewportHeight / documentHeight * viewportHeight))) + ((viewportHeight / documentHeight * viewportHeight)/2) - 2;
            const temper = document.createElement("div");
            temper.className = "scroll-marker duplicate-marker";
            temper.style.top = `${{pos}}px`;
            temper.id = "temp-stamp";
            document.querySelector(".custom-scrollbar").appendChild(temper);
        }}

        function unMark(orig) {{
            const temper = document.body.querySelector(".custom-scrollbar").querySelector("#temp-stamp");
            temper.remove();
        }}

        function updateMarkers() {{
            for (const message of document.querySelectorAll(".message")) {{
                const iden = message.id;
                if (localStorage.getItem(iden) === "1") {{
                    const messagePosition = message.offsetTop;
                    const documentHeight = document.documentElement.scrollHeight;
                    const viewportHeight = window.innerHeight;
                    const scrollableHeight = documentHeight - viewportHeight;
                
                    const marker = document.body.querySelector(".custom-scrollbar").querySelector(`#marker-${{iden}}`);
                    const pos = ((messagePosition / documentHeight) * (viewportHeight - (viewportHeight / documentHeight * viewportHeight))) + ((viewportHeight / documentHeight * viewportHeight)/2) - 2;
                    marker.style.top = `${{pos}}px`
                }}
            }}
        }}
    </script>
</head>

<body>

<div class="custom-scrollbar" id="scroll-wheel">

    <div
        class="scroll-thumb"
        id="scroll-thumb"
    ></div>

</div>

<div class="chat">
"""



system_message = f"""
    <!-- Start of chat -->
    <div class="system-message">
        {header_info["data"]["date"]["day"]}/{header_info["data"]["date"]["month"]}/{header_info["data"]["date"]["year"]}, {header_info["data"]["time"]["hour"]}:{header_info["data"]["time"]["minute"]} -
        {".\n        ".join(header_info["contents"].replace(" *Learn more*","").replace(" Learn more.","").split(". "))}
        <a class="url" target="_blank" href="https://faq.whatsapp.com/">Learn more.</a>
    </div>"""

with open(output,"w", encoding="utf-8-sig") as interface:
    interface.write(output_header)
    interface.write(system_message)
    for message in chat_lines:
        message_info = {
            "date": {},
            "time": {},
            "sender": ""
        }
        for name in participant_list:
            if f" - {name}: " in message:
                message_info["sender"] = str(name)
                message_split = message.split(f" - {name}: ",1)
                message_stamp = message_split[0].split(", ")
                message_date = message_stamp[0].split("/")
                message_time = message_stamp[1].split(":")
                message_info["date"]["month"] = f"{"0"*(2 - len(message_date[0]))}{message_date[0]}"
                message_info["date"]["day"] = f"{"0"*(2 - len(message_date[1]))}{message_date[1]}"
                message_info["date"]["year"] = f"{century}{"0"*(2 - len(message_date[2]))}{message_date[2]}"
                message_info["time"]["hour"] = message_time[0]
                message_info["time"]["minute"] = message_time[1]
                break
        else:
            message_split = message.split(f" - ",1)
            message_stamp = message_split[0].split(", ")
            message_date = message_stamp[0].split("/")
            message_time = message_stamp[1].split(":")
            message_info["date"]["month"] = f"{"0"*(2 - len(message_date[0]))}{message_date[0]}"
            message_info["date"]["day"] = f"{"0"*(2 - len(message_date[1]))}{message_date[1]}"
            message_info["date"]["year"] = f"{century}{"0"*(2 - len(message_date[2]))}{message_date[2]}"
            message_info["time"]["hour"] = message_time[0]
            message_info["time"]["minute"] = message_time[1]
            update = message_split[1]
            block = f"""
    <div class="system-update">
        <span class="timestamp">{message_info["date"]["day"]}/{message_info["date"]["month"]}/{message_info["date"]["year"]}, {message_info["time"]["hour"]}:{message_info["time"]["minute"]}</span>
        <br>
        <a>{escape(update)}</a>
    </div>"""
            interface.write(block)
            continue
        content = message_split[1].split("\\c")
        message_id = md5(f"{message_info["sender"]}:\n{"\n".join(content)}".encode("utf-8")).hexdigest()
        if message_id in used_ids:
            unique = False
        if message_id not in used_ids:
            used_ids.append(message_id)
            unique = True
        chat_box_info = f"""
    <div class="message {participant_message_type[message_info["sender"]]}" id="{message_id * int(unique)}">
        <span class="timestamp">{message_info["date"]["day"]}/{message_info["date"]["month"]}/{message_info["date"]["year"]}, {message_info["time"]["hour"]}:{message_info["time"]["minute"]}</span>
        <span class="sender">{message_info["sender"]}:</span>"""
        interface.write(chat_box_info)
        if message_split[1] == "":
            interface.write(f"""\n{indent*depth}<br>""")
            interface.write(f"""\n{indent*depth}<span class="empty-line">empty message</span>""")
            interface.write("""\n    </div>""")
            continue
        sys_attach = False
        attachments = []
        for line in content:
            for attachment in system_attachments:
                if bool(line.find(attachment)+1):
                    line = line.replace(attachment,"")
                    attachments.append(attachment)
                    sys_attach = True
            interface.write(f"""\n{indent*depth}<br>""")
            solo = bool(re.search("\\s\\(file attached\\)$",line)) or bool(re.search("^<Media omitted>$",line))
            if solo:
                if bool(re.search("^<Media omitted>$",line)):
                    interface.write(f"""\n{indent*depth}<div class="media-item"><span class="media-omitted">Media omitted</span></div>""")
                    continue
                if bool(re.search("\\s\\(file attached\\)$",line)):
                    item_name = line[:line.find("(file attached)")-1]
                    item = root / f"{item_name}"
                    if item.suffix.lower() in media_types["image"]:
                        interface.write(f"""\n{indent*depth}<div class="media-item">""")
                        if item.exists():
                            with Image.open(item) as image:
                                dim = f"({image.width}x{image.height})"
                            info = f"""Name: {escape(item.name)}\nDimensions: {dim}\nFile Size: {item.stat().st_size}-bytes"""
                            interface.write(f"""<span class="item-name">{escape(item.name)}</span><br>""")
                        if not item.exists(): info = ""
                        interface.write(f"""<a href="file:///{quote(str(item).replace("\\","/"),safe="/:")}" target="_blank" title="{info}"><img class="attached-image" src="{quote(str(item),safe="\\:")}" alt="{escape(item.name)} was not found"></a>""")
                        interface.write("""</div>""")
                        continue
                    if item.suffix.lower() in media_types["video"]:
                        interface.write(f"""\n{indent*depth}<div class="media-item">""")
                        if item.exists():
                            interface.write(f"""<span class="item-name">{escape(item.name)}</span><br>""")
                        interface.write(f"""<video class="attached-video" controls src="{quote(str(item),safe="\\:")}"></video>""")
                        if not item.exists():
                            interface.write(f"""<br><span class="media-omitted">{escape(item.name)} not found</span>""")
                        interface.write("""</div>""")
                        continue
                    if item.suffix.lower() in media_types["audio"]:
                        interface.write(f"""\n{indent*depth}<div class="media-item">""")
                        if item.exists():
                            interface.write(f"""<span class="item-name">{escape(item.name)}</span><br>""")
                        interface.write(f"""<audio class="attached-audio" controls src="{quote(str(item),safe="\\:")}"></audio>""")
                        if not item.exists():
                            interface.write(f"""<br><span class="media-omitted">{escape(item.name)} not found</span>""")
                        interface.write("""</div>""")
                        continue
                    if item.suffix.lower() in media_types["document"]:
                        if item.exists():
                            interface.write(f"""\n{indent*depth}<a class="attached-document" href="file:///{quote(str(item).replace("\\","/"),safe="/:")}" target="_blank" title="{item.name} is a Document Item">{escape(item.name)}/</a>""")
                        else:
                            interface.write(f"""\n{indent*depth}<span class="media-omitted">{escape(item.name)} not found</span>""")
                        continue
                    if item.exists(): interface.write(f"""\n{indent*depth}<a class="attached-file" title="{item.name} does exist but it is not advised to open it in your browser so it has no hyper-link address">{escape(item.name)}</a>""")
                    else: interface.write(f"""\n{indent*depth}<span class="media-omitted">{escape(item.name)} not found</span>""")
                    continue
            url_found = False
            for prefix in url_prefixes:
                url_found = url_found or bool(re.search(f"{prefix}{patterns["links"]}",line))
            if url_found:
                urls = []
                for prefix in url_prefixes:
                    matches = re.findall(f"{prefix}{patterns["links"]}",line)
                    for link in matches:
                        urls.append(link)
                if len(urls) == 1:
                    for prefix in url_prefixes:
                        display_text = re.sub(f"{prefix}{patterns["links"]}","",line)
                        url = re.search(f"{prefix}{patterns["links"]}",line)
                        if url != None:
                            url = url.group()
                            break
                    if display_text.strip() == "":
                        interface.write(f"""\n{indent*depth}<a class="url" href="{escape(url)}" target="_blank">{escape(url)}</a>""")
                    else:
                        interface.write(f"""\n{indent*depth}<a class="url" href="{escape(url)}" target="_blank">{escape(display_text)}</a>""")
                else:
                    display_text = line
                    for prefix in url_prefixes:
                        display_text = re.sub(f"{prefix}{patterns["links"]}",lambda match: f"\\l{match.group()}\\l",display_text)
                    interface.write(f"""\n{indent*depth}""")
                    components = display_text.split("\\l")
                    for component in components:
                        for prefix in url_prefixes:
                            if component[:len(prefix)] == prefix:
                                interface.write(f"""<a class="url" href="{escape(component)}" target="_blank">{escape(component)}</a>""")
                                break
                        else:
                            interface.write(f"""<span>{escape(component)}</span>""")
                continue
            if line != "":
                interface.write(f"""\n{indent*depth}{escape(line)}""")
                continue
            interface.write(f"""<!-- empty-line -->""")
        if sys_attach:
            for attachment in attachments:
                interface.write(f"""\n{indent*depth}<br>""")
                interface.write(f"""\n{indent*depth}<span class="{attachment_types[attachment]}">{escape(attachment.strip())}</span>""")
        interface.write(f"""\n{indent*depth}<br>""")
        if unique: interface.write(f"""
{indent*depth}<div class="icon-container">
{indent*depth}    <button class="star" onclick="toggleIcon('{message_id}')">
{indent*depth}        <script>
{indent*depth}            {{
{indent*depth}                const image = document.createElement("img");
{indent*depth}                image.width = 50;
{indent*depth}                image.height = 50;
{indent*depth}                const storedSource = localStorage.getItem("{message_id}");
{indent*depth}                if (storedSource === null || !(storedSource === "0" || storedSource === "1")) {{
{indent*depth}                    image.src = icons[0];
{indent*depth}                    image.title = "Click to favorite this message";
{indent*depth}                }} else {{
{indent*depth}                    image.src = icons[Number(storedSource)];
{indent*depth}                    if (storedSource === "0") {{
{indent*depth}                        image.title = "Click to favorite this message";
{indent*depth}                    }}
{indent*depth}                    if (storedSource === "1") {{
{indent*depth}                        image.title = "Click to unfavorite this message";
{indent*depth}                    }}
{indent*depth}                }}
{indent*depth}                document.currentScript.parentElement.appendChild(image);
{indent*depth}            }}
{indent*depth}        </script>
{indent*depth}    </button>
{indent*depth}</div>""")
        if not unique: interface.write(f"""
{indent*depth}<div class="icon-container">
{indent*depth}    <a class="icon" href="#{message_id}" onmouseenter="highLight('{message_id}')" onmouseleave="unMark('{message_id}')">
{indent*depth}        <script>
{indent*depth}            {{
{indent*depth}                const image = document.createElement("img");
{indent*depth}                image.width = 50;
{indent*depth}                image.height = 50;
{indent*depth}                image.src = copy_stamp;
{indent*depth}                image.title = "This message appears to be a duplicate/copy of an earlier one\\nClick to navigate to the original message";
{indent*depth}                document.currentScript.parentElement.appendChild(image);
{indent*depth}            }}
{indent*depth}        </script>
{indent*depth}    </a>
{indent*depth}</div>""")
        interface.write("""\n    </div>""")#Message-closer
    interface.write("""
</div>

<script>

    const thumb = document.getElementById("scroll-thumb");


    function updateScrollbar() {

        /* How tall the entire document is */
        const documentHeight =
            document.documentElement.scrollHeight;

        /* How much of it is currently visible */
        const viewportHeight =
            window.innerHeight;

        /* How far we can scroll */
        const scrollableHeight =
            documentHeight - viewportHeight;

        /* Size of the custom thumb */
        const thumbHeight =
            viewportHeight / documentHeight * viewportHeight;

        thumb.style.height =
            `${thumbHeight}px`;


        /* Current scroll position */
        const scrollPosition =
            window.scrollY;


        /* How far the thumb can travel */
        const trackHeight =
            viewportHeight - thumbHeight;


        /* Position of the thumb */
        let thumbPosition = 0;

        if (scrollableHeight > 0) {
            thumbPosition =
                scrollPosition / scrollableHeight
                * trackHeight;
        }

        thumb.style.top =
            `${thumbPosition}px`;
    }


    /* Update whenever the page scrolls */
    window.addEventListener(
        "scroll",
        updateScrollbar
    );


    /* Update when the window changes size */
    window.addEventListener("resize", () => {
        updateScrollbar();
        updateMarkers();
    });

    window.addEventListener("load", () => {

        /* Initial calculation */
        updateScrollbar();

        for (const message of document.querySelectorAll(".message")) {
            const iden = message.id;

            if (localStorage.getItem(iden) === "1") {
                const messagePosition = message.offsetTop;
                const documentHeight = document.documentElement.scrollHeight;
                const viewportHeight = window.innerHeight;
                const scrollableHeight = documentHeight - viewportHeight;
                
                const pos = ((messagePosition / documentHeight) * (viewportHeight - (viewportHeight / documentHeight * viewportHeight))) + ((viewportHeight / documentHeight * viewportHeight)/2) - 2;
                const marker = document.createElement("div");
                marker.className = "scroll-marker favourite-marker";
                marker.style.top = `${pos}px`;
                marker.id = `marker-${iden}`;
                document.querySelector(".custom-scrollbar").appendChild(marker);
            }
        }
    });
</script>

</body>
</html>""")#Closing sequence