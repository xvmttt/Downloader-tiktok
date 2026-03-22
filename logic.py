from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
# Включаем CORS максимально широко, чтобы ошибки не маскировались под CORS
CORS(app, resources={r"/*": {"origins": "*"}})

COOKIE_PATH = '/tmp/tiktok_cookies.txt'

def prepare_cookies():
    """Создает файл куков, если его нет. Никаких принтов в заголовки!"""
    if not os.path.exists(COOKIE_PATH):
        initial_cookies = os.environ.get('TIKTOK_COOKIES', '')
        if initial_cookies:
            with open(COOKIE_PATH, 'w', encoding='utf-8') as f:
                f.write(initial_cookies)

def get_ydl_opts():
    prepare_cookies()
    return {
        'format': 'best',
        'nocheckcertificate': True,
        'quiet': True,
        'no_warnings': True,
        'cookiefile': COOKIE_PATH if os.path.exists(COOKIE_PATH) else None,
        'extractor_args': {'tiktok': {'web_visit': True}},
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Referer': 'https://www.tiktok.com/',
        }
    }

@app.route('/proxy_video')
def proxy_video():
    video_url = request.args.get('url')
    if not video_url: return "No URL", 400

    # Здесь мы НЕ передаем заголовок 'Cookie' из переменной, 
    # чтобы не вызвать ошибку InvalidHeader
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': 'https://www.tiktok.com/',
        'Range': request.headers.get('Range', 'bytes=0-')
    }

    try:
        r = requests.get(video_url, headers=headers, stream=True, verify=False, timeout=15)
        
        def generate():
            for chunk in r.iter_content(chunk_size=1024*512):
                yield chunk
        
        resp = Response(generate(), status=r.status_code, content_type='video/mp4')
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Accept-Ranges'] = 'bytes'
        if 'Content-Range' in r.headers:
            resp.headers['Content-Range'] = r.headers['Content-Range']
        return resp
    except Exception as e:
        return str(e), 500

@app.route('/download', methods=['POST', 'OPTIONS'])
def download_video():
    if request.method == 'OPTIONS':
        return Response(status=200, headers={'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type'})
    
    data = request.get_json()
    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(data.get('url'), download=False)
            return jsonify({
                'title': info.get('title', 'Video'),
                'download_url': info.get('url')
            }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)