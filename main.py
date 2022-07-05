import os, sys, argparse, webbrowser, socket

try:
    from pydub import AudioSegment
    from pydub.playback import play 
    from moviepy.editor import concatenate_audioclips, AudioFileClip

except ImportError as err:
    print("Installing Dependecies\n")
    os.system("pip install pydub")
    os.system("pip install moviepy")
    os.system("pip install tqdm")
    
os.system("cls")

try:
    from pydub import AudioSegment
    from pydub.playback import play 
    from moviepy.editor import concatenate_audioclips, AudioFileClip

except ImportError as err:
    print("Failed to install modules: pydub, moviepy, and tqdm.\nPlease install these modules yourself")
    sys.exit()

def generate_audio(text, speaker):
    files = text.split("+")
    i = 0
    for x in files:
        if "!" in text:
            speechType = "exclaim"
        elif "?" in text:
            speechType = "exclaim"
        else:
            speechType = "neutral"
        
        path = f"audioSamples/{speaker}/words/{speechType}/{x}.mp3"
        files[i] = path
        i+=1
    return files

def concatenate_audio_moviepy(audio_clip_paths, output_path):
    """Concatenates several audio files into one audio file using MoviePy
    and save it to `output_path`. Note that extension (mp3, etc.) must be added to `output_path`"""
    clips = [AudioFileClip(c) for c in audio_clip_paths]
    final_clip = concatenate_audioclips(clips)
    final_clip.write_audiofile(output_path, codec="mp3")
    print("Audio succesfully generated")

def createSpeech(text, speaker):
    print(f"Generating speech\nText: {text}\nSpeaker: {speaker}")
    if speaker =='bluey':
        audios = generate_audio(text, speaker)
        concatenate_audio_moviepy(audios, "")
    else:
        print("Speaker not supported")

def main():

    # Define socket host and port
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 8000

    print("Starting Server")

    # Create socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(1)
    print('Listening on port %s \n' % SERVER_PORT)

    webbrowser.open('http://localhost:8000/') # Open webpage


    while 1:
        query = {
            "speaker": '',
            "text": ''
        }
        # Wait for client connections
        c, a = s.accept()

        # Get the client request
        request = c.recv(1024).decode()
        path = ''
        i = 4
        while request[i] != ' ' and request[i] != '?':
             path = path + request[i]
             i += 1
        
        if request[i] == '?':
            i += 10
            while request[i] != '&':
                query["speaker"] = query["speaker"] + request[i]
                i += 1
            i += 6
            while request[i] != ' ':
                query["text"] = query["text"] + request[i]
                i += 1

        i = 0

        text =''
        if query["text"] != '':
            speaker=query["speaker"].lower()
            text=query["text"].lower()
        
        if text == '':
            # Send HTTP response
            html = open("public/index.html", 'r').read()
            font = open("public/font.ttf", 'rb').read()
            css = open("public/style.css", 'r').read()
            loading = open("public/loading.html", 'r').read()

            if path == '/':
                response = 'HTTP/1.0 200 OK\n\n'.encode() + html.encode()
            elif path == '/font':
                response = 'HTTP/1.0 200 OK\n\n'.encode() + font
            elif path == '/style.css':
                response = 'HTTP/1.0 200 OK\n\n'.encode() + css.encode()

            c.sendall(response)
            c.close()
        else:
            print("New speech request detected")
            html = open("public/loading.html", 'r').read()
            response = 'HTTP/1.0 200 OK\n\n' + html
            c.sendall(response.encode())
            c.close()
            text = text.replace("%27","")
            createSpeech(text.replace("%3f","?").replace("%21", "!").replace("%2c", "."), speaker)
            

if __name__ == '__main__':
    main()