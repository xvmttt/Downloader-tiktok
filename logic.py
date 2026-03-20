from flask import Flask, request, jsonify
from flask_cors import CORS  
import yt_dlp
import os
import urllib3
import requests 
from flask import Response

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

IS_RENDER = os.environ.get('RENDER')
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def get_ydl_opts():
    # Получаем ту самую длинную строку куков из Render
    cookies_content = os.environ.get('TIKTOK_COOKIES', '')

    opts = {
        'format': 'best',
        'nocheckcertificate': True,
        'quiet': True,
        'no_warnings': True,
        # УДАЛЯЕМ строку 'cookiefile', она больше не нужна!
        'extractor_args': {'tiktok': {'web_visit': True}},
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Referer': 'https://www.tiktok.com/',
            'Cookie': cookies_content  # Передаем куки как заголовок!
        }
    }
    
    if not IS_RENDER:
        opts['proxy'] = 'http://127.0.0.1:12334'
            
    return opts

@app.route('/proxy_video')
def proxy_video():
    video_url = request.args.get('url')
    if not video_url:
        return "No URL provided", 400

    cookies_content = os.environ.get('TIKTOK_COOKIES', '')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': 'https://www.tiktok.com/',
        'Cookie': cookies_content, # Здесь строка работает отлично
        'Range': 'bytes=0-'
    }

    try:
        req = requests.get(video_url, headers=headers, stream=True, timeout=30, verify=False)
        
        # Если TikTok все равно ругается, выводим статус
        if req.status_code >= 400:
             return f"TikTok Proxy Error: {req.status_code}", req.status_code

        return Response(
            req.iter_content(chunk_size=1024*1024),
            content_type=req.headers.get('Content-Type', 'video/mp4'),
            headers={
                "Content-Disposition": "attachment; filename=video.mp4",
                "Access-Control-Allow-Origin": "*"
            }
        )
    except Exception as e:
        return f"Proxy Error: {str(e)}", 500

@app.route('/download', methods=['POST', 'OPTIONS'])
def download_video():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL не предоставлен'}), 400
    
    video_url = data.get('url')

    try:
        # Пытаемся получить инфо
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            return jsonify({
                'title': info.get('title', 'TikTok Video'),
                'download_url': info.get('url'),
                'thumbnail': info.get('thumbnail')
            }), 200
    except Exception as e:
        # САМОЕ ВАЖНОЕ: возвращаем реальный текст ошибки yt-dlp
        error_message = str(e)
        print(f">>> Ошибка yt-dlp: {error_message}")
        return jsonify({'message': error_message}), 400
    

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port, host='0.0.0.0')