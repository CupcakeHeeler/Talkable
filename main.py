import os, sys, argparse, webbrowser, socket, wave

os.system("cls")

validSpeakers = ["bluey", "brandy", "bingo"]

def generate_audio(text, speaker):
    files = text.split("+")
    i = 0
    speechType = "neutral"

    for x in files:
        if x.endswith("!"):
            speechtype="exclaim"
        elif x.endswith("?"):
            speechtype="question"
        speechType = "neutral"

        word = x.replace("!", "").replace("?", "")

        path = f"audioSamples/{speaker}/words/{speechType}/{word}.wav"
        if os.path.isfile(path):
            files[i] = path
        elif os.path.isfile(f"audioSamples/{speaker}/words/neutral/{word}.wav"):
            files[i] =      f"audioSamples/{speaker}/words/neutral/{word}.wav"
        elif os.path.isfile(f"audioSamples/{speaker}/words/question/{word}.wav"):
            files[i] =      f"audioSamples/{speaker}/words/question/{word}.wav"
        elif os.path.isfile(f"audioSamples/{speaker}/words/exclaim/{word}.wav"):
            files[i] =      f"audioSamples/{speaker}/words/exclaim/{word}.wav"
        else:
            if word.endswith("s"):
                word = word.replace("s","")
                path = f"audioSamples/{speaker}/words/{speechType}/{word}.wav"
                if os.path.isfile(path):
                    files[i] = path
                elif os.path.isfile(f"audioSamples/{speaker}/words/neutral/{word}.wav"):
                    files[i] =      f"audioSamples/{speaker}/words/neutral/{word}.wav"
                elif os.path.isfile(f"audioSamples/{speaker}/words/question/{word}.wav"):
                    files[i] =      f"audioSamples/{speaker}/words/question/{word}.wav"
                elif os.path.isfile(f"audioSamples/{speaker}/words/exclaim/{word}.wav"):
                    files[i] =      f"audioSamples/{speaker}/words/exclaim/{word}.wav"
                else:
                    print(f"ERROR: Couldn't find plural for {x}! D:")
                    return "Error"
            else:
                print(f"ERROR: {x} is not a valid word! (No plurals found)")
                return "Error"
        i+=1

    return files

def concatenate(audio_clip_paths, output_path):
    i = 0
    data = []
    while i < len(audio_clip_paths):
        audio = wave.open(audio_clip_paths[i], "rb")
        data.append([audio.getparams(), audio.readframes(audio.getnframes())])
        i += 1
    
    output = wave.open(output_path, "wb")
    output.setparams(data[0][0])
    for i in range(len(data)):
        output.writeframes(data[i][1])
    output.close()

    print("Audio succesfully generated")

def createSpeech(text, speaker):
    print(f"Generating speech\nText: {text}\nSpeaker: {speaker}")
    if speaker in validSpeakers:
        audios = generate_audio(text, speaker)
        if audios == "Error":
            return "Error"
        else:
            concatenate(audios, "public/temp/audio.wav")
    else:
        print("Speaker not supported")
        return "Error"

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
        try:
            query = {"speaker":'',"text":''}

            c, a = s.accept()
            request = c.recv(1024).decode()

            path = ''
            i = 4
            print(request)
            while request[i] != ' ' and request[i] != '?' and i < len(request)-1:
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
                html = open("public/main.html", 'r').read()
                get = open("public/get.js", 'r').read()
                index = open("public/index.html", 'r').read()
                font = open("public/font.ttf", 'rb').read()
                fav = open("public/fav.png", 'rb').read()
                css = open("public/style.css", 'r').read()

                #for i in range(20): html = html.replace('  ','')
                #html = html.replace('\n','')

                if path == '/':
                    response = 'HTTP/1.0 200 OK\n\n'.encode() + html.encode()
                elif path == "/index":
                    response = 'HTTP/1.0 200 OK\n\n'.encode() + index.encode()
                elif path == "/get":
                    response = 'HTTP/1.0 200 OK\n\n'.encode() + get.encode()
                elif path == "/fav":
                    response = 'HTTP/1.0 200 OK\n\n'.encode() + fav
                elif path == '/font':
                    response = 'HTTP/1.0 200 OK\n\n'.encode() + font
                elif path == '/style.css':
                    response = 'HTTP/1.0 200 OK\n\n'.encode() + css.encode()
                elif path == '/audio':
                    response = 'HTTP/1.0 200 OK\n\n'.encode() + open("public/temp/audio.wav", 'rb').read()


                c.sendall(response)
                c.close()
            else:
                print("New speech request detected")

                if os.path.isfile("public/temp/audio"):
                    os.remove("public/temp/audio")

                text = text.replace("%27","").replace(".", ",")

                text = text.replace("know", "no").replace("write", "right").replace("theyre","there").replace("their", "there").replace("theyve", "they").replace("ok","okay").replace("eye","i")

                if createSpeech(text.replace("%20","+").replace(",", "+,"), speaker) == "Error":
                    print("Failed to generate audio")
                    response = 'HTTP/1.0 400 BAD REQUEST'
                    c.sendall(response.encode())
                    c.close()
                else:
                    response = 'HTTP/1.0 200 OK\n\n'
                    c.sendall(response.encode())
                    c.close()
        except:
            print("Someone sent a funny request...")
            

if __name__ == '__main__':
    main()