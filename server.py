import requests
from flask import Flask, render_template, request, Response


app = Flask(__name__)

app.config['DEBUG'] = False
if app.config['DEBUG']:
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['PROXY'] = True


def stream(request):
    for line in request.iter_content():
        yield line


def get_sec(time):
    t = time.split(':')
    if len(t) == 3:
        sec = int(t[0]) * 3600 + int(t[1]) * 60 + int(t[2])
    if len(t) == 3:
        sec = int(t[0]) * 60 + int(t[1])
    if len(t) == 1:
        sec = int(t[0])
    return sec


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Initialize variables
        youtube_url = request.form['url']
        params = {
            'format': 'JSON',
            'video': youtube_url
        }
        if 'start' in request.form:
            start = request.form['start']
            params['start'] = get_sec(start)
        if 'end' in request.form:
            end = request.form['end']
            params['end'] = get_sec(end)

        # Optional: proxies
        if app.config['PROXY']:
            proxies = {
                'http': 'socks5://username:password@localhost:1080',
                'https': 'socks5://username:password@localhost:1080'
            }
        else:
            proxies = None

        # Request download link
        r = requests.get('http://www.youtubeinmp3.com/fetch/',
                         params=params, proxies=proxies)
        response = r.json()
        link = response['link']
        # Request MP3
        req = requests.get(link, proxies=proxies, stream=True)
        response = Response(stream(req), headers=dict(req.headers))
        return response
    else:
        return render_template('index.html')
