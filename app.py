from flask import Flask, request
import requests
import time
import threading

app = Flask(__name__)

wledUrl = "http://wled.local/win"
loadPresetUrl = wledUrl + "&PL="
savePresetUrl = wledUrl + "&PS="

standardTime = 5
standardColor = 0, 0, 255

TEMPORARY_PRESET = 255
ALARM_PRESET = 2
BLINK_PRESET = 4

sequenceRunning = False


def loadWledPreset(preset):
    requests.get(loadPresetUrl + str(preset))


def saveWledPreset(preset):
    requests.get(savePresetUrl + str(preset))


def setWledPreset(preset, t, r=-1, g=-1, b=-1):
    global sequenceRunning
    saveWledPreset(TEMPORARY_PRESET)
    loadWledPreset(preset)
    if r != -1 and g != -1 and b != -1:
        setWledColor(r, g, b)
    time.sleep(t)
    loadWledPreset(TEMPORARY_PRESET)
    sequenceRunning = False


def setWledColor(r, g, b):
    requests.get(wledUrl + "&R=" + str(r) + "&G=" + str(g) + "&B=" + str(b))


@app.route('/api/wledNotify/Alarm')
def n_alarm():
    global sequenceRunning
    if sequenceRunning:
        return 'another sequence is currently running'
    sequenceRunning = True
    if 't' in request.args:
        try:
            t = int(request.args['t'])
        except ValueError:
            t = standardTime
    else:
        t = standardTime
    threading.Thread(target=setWledPreset, args=(ALARM_PRESET, t)).start()
    return 'Alarm sequence started'


@app.route('/api/wledNotify/Flash')
def n_flash():
    global sequenceRunning
    if sequenceRunning:
        return 'another sequence is currently running'
    sequenceRunning = True
    if 't' in request.args:
        try:
            t = int(request.args['t'])
        except ValueError:
            t = standardTime
    else:
        t = standardTime
    if 'r' in request.args:
        try:
            r = int(request.args['r'])
        except ValueError:
            r = standardColor[0]
    else:
        r = standardColor[0]
    if 'g' in request.args:
        try:
            g = int(request.args['g'])
        except ValueError:
            g = standardColor[1]
    else:
        g = standardColor[1]
    if 'b' in request.args:
        try:
            b = int(request.args['b'])
        except ValueError:
            b = standardColor[2]
    else:
        b = standardColor[2]
    threading.Thread(target=setWledPreset, args=(BLINK_PRESET, t, r, g, b)).start()
    return 'Flash sequence started'


@app.route('/api/wledNotify/Stop')
def n_stop():
    global sequenceRunning
    sequenceRunning = False
    loadWledPreset(TEMPORARY_PRESET)
    return 'current sequence stopped'


if __name__ == '__main__':
    app.run()
