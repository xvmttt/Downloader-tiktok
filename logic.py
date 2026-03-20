from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

def get_ydl_opts():
    cookies_content = os.environ.get('TIKTOK_COOKIES', '').strip().replace('\n', '').replace('\t', ' ')
    return {
        'format': 'best',
        'nocheckcertificate': True,
        'quiet': True,
        'extractor_args': {'tiktok': {'web_visit': True}},
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Cookie': cookies_content,
            'Referer': 'https://www.tiktok.com/'
        }
    }

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