import time
from pathlib import Path
from html import escape
import re
from urllib.parse import quote
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import HTTPError
from urllib.error import URLError
from hashlib import sha256
import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime
import errno

agent_info = {"User-Agent":"ChatWeaver/1.0 (Project-StarStorm)"}

def import_mode_dialog(parent: tk.Tk):
    dialog = tk.Toplevel(parent)
    dialog.title("Please Choose Import Mode")
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()

    result = None

    def select_mode(mode):
        nonlocal result
        result = mode
        dialog.destroy()

    tk.Label(
        dialog,
        text="How would you like to import attachments?",
        padx=20,
        pady=15
    ).pack()

    full_button = tk.Button(
        dialog,
        text="Full Import Mode",
        width=25,
        command=lambda: select_mode("full")
    )
    full_button.pack(pady=5)

    space_button = tk.Button(
        dialog,
        text="Space-Saving Mode",
        width=25,
        command=lambda: select_mode("space-saving")
    )
    space_button.pack(pady=5)

    cancel_button = tk.Button(
        dialog,
        text="Cancel",
        width=25,
        command=dialog.destroy
    )
    cancel_button.pack(pady=(5, 15))

    cancel_button.focus_set()

    dialog.bind("<Return>", lambda event: cancel_button.invoke())
    dialog.bind("<Escape>", lambda event: cancel_button.invoke())

    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

    parent.wait_window(dialog)

    return result

url_prefixes = [
    "http://",
    "https://",
    "ftp://",
    "ftps://",
    "file:///",
    "data:",
]

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
}

self_path = Path(__file__)

title = "Message from Project-StarStorm"
body = f"""Before we begin, we would like to inform you of exactly what this program does.
{self_path.name} may:
    • Read files in the parent folder
    • Write files in the parent folder
    • Process the export files in deterministic, pre-programmed ways
    • Adapt to broken exports with missing files as much as possible

{self_path.name} will NOT:
    •Alter your data
    •Delete your data
    •Leak your data
    •Transmit your data over the network
    •Comrehend the context of your chat conversation in any inteligent, invasive, or intrusive way
    •Evolve, change, or modify the way it processes your data without you programming new intuctions

Note for user: please make sure {self_path.name} is directly under the "Messages" folder

Do you consent to this process?"""

base = tk.Tk()

base.withdraw()

user_consent = messagebox.askyesno(title=title,message=body,icon="info",default="no",parent=base)

if not user_consent:
    print("Operation cancelled. No conversion was started.")
    time.sleep(5)
    raise SystemExit

print("Consent granted. Starting conversion...")
time.sleep(5)

root = Path(__file__).parent

log_path = root / "Error Log.txt"
map_path = root / "Chat-Map.html"

media_path = root / "Chat-Media.html"

index_path = root / "index.json"

proceed = None
type_exep = []

if not index_path.exists():
    map_code = f"""<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Chat-Map</title>
        <style>
            html {{
                scroll-behavior: smooth;
            }}
            body {{
                font-family: 'Courier New', Courier, monospace;
                background: #0f0f0f;
                padding: 20px;
            }}

            .header {{
                max-width: 80%;
                margin: auto;
                color: #d00;
                padding: 5px;
                background: #333;
                font-size: larger;
                border-radius: 10px;
                border: 2px solid #f00;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Discord Transcript Map</h2>
            <p>This export apears to be broken or incomplete,</p>
            <p>The file: index.json apears to be missing</p>
        </div>
    </body>
</html>"""
    proceed = messagebox.askyesno(title="The was a problem",message="this export apears to be broken, degraded or incomplete\nindex.json apears to be missing",detail="Do you want to proceed?",icon="warning",default="no",parent=base)
    if not proceed:
        try:
            with open(map_path, "w", encoding="utf-8-sig") as map_file:
                map_file.write(map_code)
        except OSError as fail:
            if fail.errno == errno.ENOSPC:
                map_path.unlink(True)
            else:
                raise
        print("Operation cancelled.\nExiting...")
        time.sleep(5)
        raise SystemExit

if proceed == None:
    with open(index_path, "r", encoding="utf-8") as index_file:
        index = dict(json.load(index_file))
    ids = list(index.keys())
if proceed:
    folders = list(root.glob("c*"))
    ids = []
    index = {}
    for path in folders:
        if path.is_dir():
            ids.append(path.name[1:])
            if (path / "channel.json").exists():
                chan = dict(json.load(open((path / "channel.json"), "r", encoding="utf-8")))
                if chan["type"] == "DM": index[path.name[1:]] = f"Direct Message between {" & ".join(chan["recipients"])}"
                elif chan["type"] == "GUILD_TEXT": index[path.name[1:]] = f"{chan["name"]} in {chan["guild"]["name"]}"
                elif chan["type"] == "PUBLIC_THREAD": index[path.name[1:]] = f"{chan["name"]} in {chan["guild"]["name"]}"
                elif chan["type"] == "GROUP_DM": index[path.name[1:]] = str(chan["name"])
                else: type_exep += [path.name[1:]]

local_mode = messagebox.askyesno(title="Do you want to activate local mode?",message=f"Activating local mode may cause {self_path.name} to make network-requests for the contents each media attachment and dowload the the ones it could access into local storage",icon="question",default="no",parent=base)
if local_mode:
    import_mode = import_mode_dialog(base)
    if import_mode is None:
        local_mode = False

map_opener = f"""<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Chat-Map</title>
        <style>
            html {{
                scroll-behavior: smooth;
            }}
            body {{
                font-family: 'Courier New', Courier, monospace;
                background: #0f0f0f;
                padding: 20px;
            }}

            .header {{
                max-width: 80%;
                margin: auto;
                color: #0d0;
                padding: 5px;
                background: #333;
                font-size: larger;
                border-radius: 10px;
                border: 2px solid #0f0;
            }}

            .list {{
                max-width: 65%;
                margin: auto;
                padding: 5px;
            }}

            .entry {{
                background: #333;
                padding: 10px;
                font-size: larger;
                border-radius: 10px;
                margin: 5px auto;
                /*border: 2px solid #0f0;*/
            }}

            .entry:hover::before {{
                content: "> ";
            }}

            .entry:hover::after {{
                content: attr(data-hover);
            }}

            .stable {{
                color: #0d0;
            }}

            .broken {{
                color: #d00;
            }}

            .ghost {{
                color: #dd0;
            }}

            .entry a {{
                color: inherit;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Discord Transcript Map</h2>
            <p>This document serves as an index of the exported Discord conversations processed by this program.</p>
            <p>Each entry represents a conversation and provides a hyperlink to its corresponding HTML transcript. Select an entry to open the associated conversation.</p>
            <p>All transcripts and this index are generated locally from the exported data. This document serves as a navigational index and does not contain the full contents of the conversations themselves.</p>
        </div>
        <div class="list">"""
map_closer = """
        </div>
    </body>
</html>"""
map_code = """"""
map_code += map_opener

media_opener = f"""<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
It will be read and overwritten.
DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Discord Chat Media Links</TITLE>
<H1>Discord Chat Media Links</H1>
<DL><p>
    <DT><H3>Discord Chat Media</H3>
    <DL><p>"""
media_closer = """
    </DL><p>
</DL><p>"""
media_code = """"""
media_code += media_opener

delay = 0.1
retry_limit = 10
server_stackup = 0
stackup_limit = 5
wait_max = 10.0

for chat_id in ids:
    folder = root / f"c{chat_id}"
    channel_path = folder / "channel.json"
    message_path = folder / "messages.json"
    media_folder = folder / "media"
    restricted = False
    if not (index_path.exists()) and (not channel_path.exists() or (chat_id in type_exep)):
        chat_path = folder / f"c{chat_id}.html"
        true_path = folder / f"c{chat_id}.html"
    if (index_path.exists()) or (channel_path.exists() and (chat_id not in type_exep)):
        chat_path = folder / f"{str(index[chat_id]).replace('\\', '_').replace('/', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')}.html"
        true_path = folder / f"{index[chat_id]}.html"
    is_broken = not (folder.exists() and channel_path.exists() and message_path.exists()) or (chat_id in type_exep)
    if is_broken:
        if not folder.exists():
            map_code += f"""
            <div class="broken entry" data-hover=" - Folder is missing">c{chat_id}</div>"""; continue
        if folder.exists():
            if channel_path.exists() and not message_path.exists(): map_code += f"""
            <div class="broken entry" data-hover=" - 'c{chat_id}\\messages.json' is missing">c{chat_id}</div>"""; continue
            if not channel_path.exists() and message_path.exists(): map_code += f"""
            <div class="broken entry" data-hover=" - 'c{chat_id}\\channel.json' is missing">c{chat_id}</div>"""
            if not channel_path.exists() and not message_path.exists(): map_code += f"""
            <div class="broken entry" data-hover=" - 'c{chat_id}\\channel.json' and 'c{chat_id}\\messages.json' are missing">c{chat_id}</div>"""; continue
            if chat_id in type_exep: map_code += f"""
            <div class="ghost entry" data-hover=" - Type-unrecognised"><a href="file:///{quote(str(chat_path).replace("\\","/"),safe="/:")}" target="_blank">c{chat_id}</a></div>"""
    if local_mode and not media_folder.exists(): media_folder.mkdir()
    if channel_path.exists():
        with open(channel_path, "r", encoding="utf-8") as channel:
            channel_info = dict(json.load(channel))
    recognised = True
    if not channel_path.exists():
        recognised = False
        structure = ""
        chat_info = f"""Convo-ID: {chat_id}
                <br>
                Type: 'c{chat_id}\\channel.json' is missing, as a result, hyper-link IDs will be disabled"""
    elif channel_info["type"] == "DM":
        avail = list(channel_info.keys())
        if "recipients" not in avail: channel_info["recipients"] = ["None"]
        structure = f"https://discord.com/channels/@me/{channel_info["id"]}"
        chat_info = f"""Convo-ID: <a href="https://discord.com/channels/@me/{channel_info["id"]}" target="_blank">{channel_info["id"]}</a>
                <br>
                Type: DM
                <br>
                Participant-IDs:"""
        if channel_info["recipients"] != ["None"]:
            chat_info += f""" <br> {" <br> ".join(f"""<a href="https://discord.com/users/{recipient}" target="_blank">{escape(recipient)}</a>""" for recipient in channel_info["recipients"])}"""
        if channel_info["recipients"] == ["None"]:
            chat_info += """ None"""
    elif channel_info["type"] == "GUILD_TEXT":
        avail = list(channel_info.keys())
        if "name" not in avail: channel_info["name"] = None
        if "guild" not in avail: channel_info["guild"] = {"id": None, "name": None}; recognised = False
        structure = f"https://discord.com/channels/{channel_info["guild"]["id"]}/{channel_info["id"]}"*int(recognised)
        chat_info = f"""Convo-ID: <a href="https://discord.com/channels/{channel_info["guild"]["id"]}/{channel_info["id"]}" target="_blank">{channel_info["id"]}</a>
                <br>
                Type: GUILD_TEXT
                <br>
                Name: {escape(str(channel_info["name"]))}
                <br>
                Guild-id: {channel_info["guild"]["id"]}
                Guild-name: {escape(str(channel_info["guild"]["name"]))}"""
    elif channel_info["type"] == "PUBLIC_THREAD":
        avail = list(channel_info.keys())
        if "name" not in avail: channel_info["name"] = None
        if "guild" not in avail: channel_info["guild"] = {"id": None, "name": None}; recognised = False
        structure = f"https://discord.com/channels/{channel_info["guild"]["id"]}/{channel_info["id"]}"*int(recognised)
        chat_info = f"""Convo-ID: <a href="https://discord.com/channels/{channel_info["guild"]["id"]}/{channel_info["id"]}" target="_blank">{channel_info["id"]}</a>
                <br>
                Type: PUBLIC_THREAD
                <br>
                Name: {escape(str(channel_info["name"]))}
                <br>
                Guild-id: {channel_info["guild"]["id"]}
                Guild-name: {escape(str(channel_info["guild"]["name"]))}"""
    elif channel_info["type"] == "GROUP_DM":
        avail = list(channel_info.keys())
        if "name" not in avail: channel_info["name"] = None
        if "icon_hash" not in avail: channel_info["icon_hash"] = None
        if "recipients" not in avail: channel_info["recipients"] = ["None"]
        structure = f"https://discord.com/channels/@me/{channel_info["id"]}"
        chat_info = f"""Convo-ID: <a href="https://discord.com/channels/@me/{channel_info["id"]}" target="_blank">{channel_info["id"]}</a>
                <br>
                Type: GROUP_DM
                <br>
                Name: {escape(str(channel_info["name"]))}
                <br>
                Icon-Hash: {escape(str(channel_info["icon_hash"]))}
                <br>
                Participant-IDs:"""
        if channel_info["recipients"] != ["None"]:
            chat_info += f""" <br> {" <br> ".join(f"""<a href="https://discord.com/users/{recipient}" target="_blank">{escape(recipient)}</a>""" for recipient in channel_info["recipients"])}"""
        if channel_info["recipients"] == ["None"]:
            chat_info += """ None"""
    elif chat_id in type_exep:
        recognised = False
        structure = ""
        chat_info = f"""Convo-ID: {channel_info["id"]}
                <br>
                Type: {escape(str(channel_info["type"]))} - this channel-type is not recognised by this program, as a result, hyper-link IDs will be disabled"""
    else:
        recognised = False
        structure = ""
        chat_info = f"""Convo-ID: {channel_info["id"]}
                <br>
                Type: {escape(str(channel_info["type"]))} - this channel-type is not recognised by this program, as a result, hyper-link IDs will be disabled"""

    opener = f"""<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Discord Chat</title>
        <style>
            html {{
                scroll-behavior: smooth;
            }}

            body {{
                font-family: Arial, sans-serif;
                background: #0f0f0f;
                padding: 20px;
            }}

            .chat {{
                max-width: 65%;
                margin: auto;
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

            .system-message a {{
                color: #777;
            }}

            .message {{
                background: #222;
                color: white;
                max-width: 60%;
                margin: 8px auto;
                padding: 10px;
                border-radius: 8px;
                overflow-wrap: anywhere;
                text-align: center;
            }}

            .timestamp {{
                color: #0f0;
                font-size: 0.85em;
                font-family: 'Courier New', Courier, monospace;
                text-align: center;
            }}

            .id {{
                font-weight: bold;
                font-family: 'Courier New', Courier, monospace;
                text-align: center;
            }}

            .id a {{
                color: #777;
            }}

            .empty-message {{
                color: #b88600;
                background: yellow;
                font-weight: bold;
                font-family: 'Courier New', Courier, monospace;
            }}

            .url {{
                color: blue;
            }}

            .media-cluster {{
                border: 2px solid white;
                padding: 5px 10px;
                margin-top: 5px;
                margin-bottom: 5px;
                border-radius: 10px;
                text-align: center;
            }}

            .item-name {{
                color: #0f0;
                font-family: Consolas, "Courier New", monospace;
            }}

            div.spacing-container{{
                margin: 5px auto;
            }}

            .attached-image {{
                max-width: 100%;
                max-height: 300px;
                color: red;
                font-weight: bold;
                font-family: 'Courier New', Courier, monospace;
            }}

            .attached-video {{
                max-width: 100%;
                max-height: 300px;
            }}

            .attached-audio {{
                max-width: 100%;
            }}

            .attached-document {{
                color: orange;
                font-family: Consolas, "Courier New", monospace;
            }}

            .attached-file {{
                color: magenta;
                font-family: Consolas, "Courier New", monospace;
            }}

            .icon-container {{
                text-align: center;
                display: block;
                width: fit-content;
                margin-left: auto;
            }}

            .fav-button {{
                background: local;
                border: 2px dotted #fc0;
                color: #fc0;
                font-weight: bolder;
                padding: 10px;
                font-size: larger;
                margin: 5px 5px 5px 5px;
            }}

            .copy-button {{
                display: inline-block;
                background: local;
                border: 2px dotted #08f;
                font-weight: bolder;
                padding: 10px;
                font-size: larger;
                margin: 5px;
            }}
        </style>
        <script></script>
    </head>
    <body>
        <div class="chat">
            <!-- Start of chat -->
            <div class="system-message">
                <h2>Convo Info</h2>
                {chat_info}
            </div>"""
    closer = """
        </div>
    </body>
</html>"""
    with open(message_path, "r", encoding="utf-8", newline="\n") as message_file:
        messages = list(json.load(message_file))
    messages.sort(key=lambda item: (item["Timestamp"], item["ID"]))
    try:
        with open(chat_path, "w", encoding="utf-8-sig") as chat:
            chat.write(opener)
            media_code += f"""
        <DT><H3>{escape(true_path.stem)}</H3>
        <DL><p>"""
            for message in messages:
                message_info = {
                    "date": {},
                    "time": {},
                }
                stamp = message["Timestamp"]
                message_info["date"]["Y"],message_info["date"]["M"],message_info["date"]["D"] = stamp[0:4],stamp[5:7],stamp[8:10]
                message_info["time"]["H"],message_info["time"]["M"],message_info["time"]["S"] = stamp[11:13],stamp[14:16],stamp[17:19]
                chat.write(f"""
            <div class="message" id="{int(message["ID"]):019d}">
                <div class="id">{f"""<a href="{structure}/{int(message["ID"]):019d}" target="_blank">""" * int(recognised)}{int(message["ID"]):019d}{"</a>" * int(recognised)}</div>
                <div class="timestamp">{escape(stamp)}</div>""")
                lines = str(message["Contents"]).splitlines()
                for line in lines:
                    chat.write(f"""\n                <br>""")
                    url_found = False
                    for prefix in url_prefixes:
                        url_found = url_found or bool(re.search(f"(?<!\\S){re.escape(prefix)}\\S+",line))
                    if url_found:
                        urls = []
                        for prefix in url_prefixes:
                            urls += re.findall(f"(?<!\\S){re.escape(prefix)}\\S+",line)
                        if len(urls) == 1:
                            for prefix in url_prefixes:
                                url = re.search(f"(?<!\\S){re.escape(prefix)}\\S+",line)
                                if url != None:
                                    display_text = re.sub(f"(?<!\\S){re.escape(prefix)}\\S+","",line)
                                    url = url.group()
                                    break
                            if display_text.strip() == "":
                                chat.write(f"""\n                <a class="url" href="{escape(url)}" target="_blank">{escape(url)}</a>""")
                            else:
                                chat.write(f"""\n                <a class="url" href="{escape(url)}" target="_blank">{escape(display_text)}</a>""")
                        else:
                            display_text = line
                            for prefix in url_prefixes:
                                display_text = re.sub(f"(?<!\\S){re.escape(prefix)}\\S+",lambda match: f"\\l{match.group()}\\l",display_text)
                            chat.write(f"""\n                """)
                            components = display_text.split("\\l")
                            for component in components:
                                for prefix in url_prefixes:
                                    if component[:len(prefix)] == prefix:
                                        chat.write(f"""<a class="url" href="{escape(component)}" target="_blank">{escape(component)}</a>""")
                                        break
                                else:
                                    chat.write(f"""<span>{escape(component)}</span>""")
                        continue
                    if line != "":
                        chat.write(f"""\n                <span>{escape(line)}</span>""")
                        continue
                    chat.write(f"""<!-- empty-line -->""")
                attachments = str(message["Attachments"]).split(" ")
                if attachments != [""]:
                    chat.write(f"""
                <div class="media-cluster">""")
                    for attachment in attachments:
                        item_name = attachment[(attachment.find("/attachments/")+13+20+20):attachment.find("?ex=")]
                        item_id = attachment[(attachment.find("/attachments/")+13+20):(attachment.find("/attachments/")+13+20+19)]
                        item_type = Path(item_name).suffix
                        item_stem = Path(item_name).stem
                        alert = ""
                        if local_mode:
                            if import_mode == "full":
                                item_path = media_folder / f"{item_stem}{{{item_id}}}{item_type}"
                            if import_mode == "space-saving":
                                item_path = media_folder / item_name
                            src = f"media/{escape(item_name)}"
                            request = Request(attachment,headers=agent_info)
                            if not item_path.exists():
                                if not restricted:
                                    for retry in range(retry_limit):
                                        try:
                                            with urlopen(request,timeout=wait_max) as responce:
                                                source = responce.read()
                                                time.sleep(delay)
                                            if import_mode == "space-saving":
                                                item_id = sha256(source).hexdigest()
                                            local_path = media_folder / f"{item_stem}{{{item_id}}}{item_type}"
                                            temp_path = media_folder / f"{item_id}.tmp"
                                            if not local_path.exists():
                                                with open(temp_path,"wb") as local_copy:
                                                    local_copy.write(source)
                                        except TimeoutError:src = escape(attachment);break
                                        except HTTPError as error:
                                            if error.code == 429:
                                                rest = (error.headers.get("Retry-After"))
                                                if rest == None:time.sleep(5);continue
                                                try:
                                                    rest = float(rest)
                                                except (ValueError):
                                                    try:
                                                        rest_unix = datetime.strptime(rest,"%a, %d %b %Y %H:%M:%S GMT").timestamp()
                                                        current_unix = time.time()
                                                        unix_dif = rest_unix - current_unix
                                                    except (TypeError,ValueError,OverflowError,OSError):
                                                        src = escape(attachment)
                                                        break
                                                    else:
                                                        if not (unix_dif >= 0):src = escape(attachment);break
                                                        if not (unix_dif <= wait_max):src = escape(attachment);break
                                                        time.sleep(unix_dif)
                                                else:
                                                    if rest > wait_max:
                                                        src = escape(attachment)
                                                        break
                                                    if rest <= wait_max:
                                                        time.sleep(rest)
                                            elif error.code in [500,502,503]:
                                                if server_stackup<stackup_limit:
                                                    server_stackup += 1
                                                    time.sleep(5)
                                                elif server_stackup>=stackup_limit:
                                                    server_stackup += 1
                                                    src = escape(attachment)
                                                    break
                                            elif error.code in [404,410]:
                                                alert = " (Attachment appears to no longer be available)"
                                                src = escape(attachment)
                                                break
                                            else:src = escape(attachment);break
                                        except URLError as error:
                                            src = escape(attachment)
                                            break
                                        except MemoryError:src = escape(attachment);break
                                        except PermissionError:
                                            restricted = True
                                            break
                                        except OSError as fail:
                                            if fail.errno == errno.ENOSPC:
                                                print("Insufficient disk space\nPlease free up some space and try again\nExiting now...")
                                                time.sleep(10)
                                                raise SystemExit
                                            else:
                                                raise
                                        else:
                                            if not local_path.exists():
                                                temp_path.rename(local_path)
                                            src = f"media/{escape(local_path.name)}"
                                            server_stackup=0
                                            break
                                    else:src = escape(attachment)
                                if restricted:
                                    src = escape(attachment)
                                    break
                            elif item_path.exists():
                                src = f"media/{escape(item_name)}"
                        if not local_mode:
                            src = escape(attachment)
                        if item_type in media_types["image"]:
                            chat.write(f"""
                    <div class="spacing-container">
                        <a href="{src}" target="_blank">
                            <img class="attached-image" src="{src}" alt="{escape(item_name)} could not be accessed" title="Attachment-Name: {escape(item_name)}">
                        </a>
                    </div>""")
                            media_code += f"""
            <DT><A HREF="{escape(attachment)}">{escape(item_name)}{alert}</A>"""
                        if item_type in media_types["video"]:
                            chat.write(f"""
                    <div class="spacing-container">
                        <video controls loop src="{src}" class="attached-video"></video>
                    </div>""")
                        if item_type in media_types["audio"]:
                            chat.write(f"""
                    <div class="spacing-container">
                        <audio controls src="{src}" class="attached-audio"></audio>
                    </div>""")
                    chat.write(f"""
                </div>""")#Media-Cluster-Closer
                chat.write(f"""
            </div>""")#Message-Closer
            chat.write(closer)
    except OSError as fail:
        if fail.errno == errno.ENOSPC:
            chat_path.unlink(True)
            print("Insufficient disk space\nPlease free up some space and try again\nExiting now...")
            time.sleep(10)
            raise SystemExit
        else:
            raise
    media_code += """
        </DL><p>"""
    if not is_broken: map_code += f"""
            <div class="stable entry" data-hover=" - {escape(index[chat_id])}"><a href="file:///{quote(str(chat_path).replace("\\","/"),safe="/:")}" target="_blank">c{chat_id}</a></div>"""
map_code += map_closer

try:
    with open(map_path, "w", encoding="utf-8-sig") as map_file:
        map_file.write(map_code)
except OSError as fail:
    if fail.errno == errno.ENOSPC:
        map_path.unlink(True)
        print("Insufficient disk space\nPlease free up some space and try again\nExiting now...")
        time.sleep(10)
        raise SystemExit
    else:
        raise

media_code += media_closer

try:
    with open(media_path, "w", encoding="utf-8", newline="\n") as media_file:
        media_file.write(media_code)
except OSError as fail:
    if fail.errno == errno.ENOSPC:
        media_path.unlink(True)
        print("Insufficient disk space\nPlease free up some space and try again\nExiting now...")
        time.sleep(10)
        raise SystemExit
    else:
        raise

print(f"""Process complete
You may open {map_path.name} in your browser to navigate your conversation-transcripts or import {media_path.name} into you browser's bookmark settings to have a bookmarks folder of all the image attatchments discorvered in this export
Enjoy...""")
time.sleep(10)