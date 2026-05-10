from flask import Flask, jsonify
import pyscreenshot
import os
import time
import threading
from PIL import Image
from colorama import Fore, Back, Style
from pyngrok import ngrok
asciiart="""                            .-'''-.                                   _..._                                                                
                           '   _    \  .---.                       .-'_..._''.                                                             
_________   _...._       /   /` '.   \ |   |                     .' .'      '.\              __.....__           __.....__        _..._    
\        |.'      '-.   .   |     \  ' |   |.-.          .-     / .'                     .-''         '.     .-''         '.    .'     '.  
 \        .'```'.    '. |   '      |  '|   | \ \        / /    . '             .-,.--.  /     .-''"'-.  `.  /     .-''"'-.  `. .   .-.   . 
  \      |       \     \\    \     / / |   |  \ \      / /     | |             |  .-. |/     /________\   \/     /________\   \|  '   '  | 
   |     |        |    | `.   ` ..' /  |   |   \ \    / /   _  | |             | |  | ||                  ||                  ||  |   |  | 
   |      \      /    .     '-...-'`   |   |    \ \  / /  .' | . '             | |  | |\    .-------------'\    .-------------'|  |   |  | 
   |     |\`'-.-'   .'                 |   |     \ `  /  .   | /\ '.          .| |  '-  \    '-.____...---. \    '-.____...---.|  |   |  | 
   |     | '-....-'`                   |   |      \  / .'.'| |// '. `._____.-'/| |       `.             .'   `.             .' |  |   |  | 
  .'     '.                            '---'      / /.'.'.-'  /    `-.______ / | |         `''-...... -'       `''-...... -'   |  |   |  | 
'-----------'                                 |`-' / .'   \_.'              `  |_|                                             |  |   |  | 
                                               '..'                                                                            '--'   '--' """
print(Fore.GREEN + asciiart)
time.sleep(1)
print(Fore.BLACK + Back.RED +"------------------------------------------------------------------------------------" + Style.RESET_ALL)
print(Fore.BLACK + Back.RED +"# DO NOT GO TO THE FLASK LINK IF YOU'RE EPILEPTIC. (something like 127.0.0.1:5000) #" + Style.RESET_ALL)
print(Fore.BLACK + Back.RED +"------------------------------------------------------------------------------------" + Style.RESET_ALL)
input = input('Paste your ngrok key here: ')
port = 5000
print(f'Pixel list: http://127.0.0.1:{port}/api/pixels')

app = Flask(__name__)
folderName = "static/frames"
os.makedirs(folderName, exist_ok=True)
current_frame = 0
latest_data = {
    "width": 50,
    "height": 0,
    "hex_pixels": []
}
ngrok.set_auth_token(input)
public_url = ngrok.connect(5000).public_url
print(f" * ngrok tunnel available at: {public_url} << do not go here if you're epileptic")
print(f" * ngrok public pixel api at: {public_url}/api/pixels << paste this in polytoria game, you can visit this if you're epileptic")

def capture_loop():
    global current_frame
    while True:
        img = pyscreenshot.grab()
        new_num = current_frame + 1
        new_path = os.path.join(folderName, f'frame_{new_num}.png')
        frame_width = 50
        w, h = img.size
        frame_height = int(frame_width * (h / w))
        frame = img.resize((frame_width, frame_height), resample=Image.BILINEAR)
        latest_data["height"] = frame_height
        pixels_dict = {f"pixel{i:04d}": "%02x%02x%02xff" % p for i, p in enumerate(frame.getdata())}
        latest_data["hex_pixels"] = pixels_dict
        frame.save(new_path)

        old_path = os.path.join(folderName, f'frame_{current_frame}.png')
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except:
                pass

        current_frame = new_num
        time.sleep(0.5)

@app.after_request
def add_ngrok_header(response):
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

@app.route("/")
def web_view():
    if current_frame == 0:
        return "<h1>Waiting for first frame...</h1><meta http-equiv='refresh' content='1'>"

    current_img = f"frame_{current_frame}.png"
    return f"""
    <html>
        <head><meta http-equiv="refresh" content="0.5"></head>
        <body>
            <h1>Stream</h1>
            <img src="/static/frames/{current_img}" style="width:80%;">
        </body>
    </html>
    """


@app.route("/api/pixels")
def api_view():
    return jsonify({
        "frame_number": max(0, current_frame - 1),
        "width": 50,
        "height": latest_data["height"],
        "pixels": latest_data["hex_pixels"]
    })


if __name__ == "__main__":
    threading.Thread(target=capture_loop, daemon=True).start()
    app.run(debug=True, port=port, use_reloader=False)
