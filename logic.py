from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import os
import requests
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

COOKIE_PATH = '/tmp/tiktok_cookies.txt'

def get_ydl_opts():
    if not os.path.exists(COOKIE_PATH):
        initial_cookies = os.environ.get('TIKTOK_COOKIES', '')
        with open(COOKIE_PATH, 'w') as f:
            f.write(initial_cookies)
            
    return {
        'format': 'best',
        'nocheckcertificate': True,
        'quiet': True,
        'no_warnings': True,
        # КЛЮЧЕВОЙ МОМЕНТ: yt-dlp будет читать И записывать обновления сюда
        'cookiefile': COOKIE_PATH, 
        'extractor_args': {'tiktok': {'web_visit': True}},
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.tiktok.com/',
        }
    }
    
    # Если на Render нет файла, мы можем подгрузить "стартовый капитал" из переменной
    if not os.path.exists(cookie_path):
        initial_cookies = os.environ.get('TIKTOK_COOKIES', '')
        with open(cookie_path, 'w') as f:
            f.write(initial_cookies)
            
    return opts
@app.route('/proxy_video')
def proxy_video():
    video_url = request.args.get('url')
    if not video_url: return "No URL", 400

    cookies_content = os.environ.get('TIKTOK_COOKIES', '').strip()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': 'https://www.tiktok.com/',
        'Cookie': cookies_content,
        'Range': request.headers.get('Range', 'bytes=0-')
    }

    # Делаем запрос к TikTok
    r = requests.get(video_url, headers=headers, stream=True, verify=False, timeout=20)
    
    # Пересылаем ответ TikTok пользователю
    def generate():
        for chunk in r.iter_content(chunk_size=1024*1024):
            yield chunk

    return Response(generate(), 
                    status=r.status_code, 
                    content_type=r.headers.get('Content-Type', 'video/mp4'),
                    headers={'Access-Control-Allow-Origin': '*'})

@app.route('/download', methods=['POST', 'OPTIONS'])
def download_video():
    if request.method == 'OPTIONS': return '', 200
    data = request.get_json()
    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(data.get('url'), download=False)
            return jsonify({
                'title': info.get('title', 'Video'),
                'download_url': info.get('url')
            }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))