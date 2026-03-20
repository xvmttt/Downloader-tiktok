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
    cookies_content = os.environ.get('TIKTOK_COOKIES', '').strip().replace('\n', '').replace('\t', ' ')

    opts = {
        'format': 'best',
        'nocheckcertificate': True,
        'quiet': True,
        'no_warnings': True,
        # Мы НЕ используем 'cookiefile' вообще!
        'extractor_args': {'tiktok': {'web_visit': True}},
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/', # Притворимся, что пришли из поиска
            'Cookie': cookies_content 
        }
    }
    
    # Убедись, что ниже нет блоков, которые добавляют opts['cookiefile']
    if not IS_RENDER:
        opts['proxy'] = 'http://127.0.0.1:12334'
        # Если ты на локалке, проверь, чтобы здесь тоже не подмешивался файл
            
    return opts

@app.route('/proxy_video')
def proxy_video():
    video_url = request.args.get('url')
    if not video_url:
        return "No URL provided", 400

    cookies_content = os.environ.get('TIKTOK_COOKIES', '').strip()

    # Улучшенные заголовки для обхода 403 при стриминге
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': 'https://www.tiktok.com/',
        'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cookie': cookies_content,
        'Connection': 'keep-alive',
        'Range': request.headers.get('Range', 'bytes=0-') # Передаем Range от браузера
    }

    try:
        # Используем сессию для стабильности
        session = requests.Session()
        req = session.get(video_url, headers=headers, stream=True, timeout=15, verify=False)
        
        if req.status_code == 403:
             return f"TikTok Proxy Error 403: Доступ запрещен. Попробуйте обновить куки в Render.", 403

        # Создаем ответ с правильными заголовками стриминга
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        resp_headers = [(name, value) for (name, value) in req.raw.headers.items()
                        if name.lower() not in excluded_headers]

        return Response(
            req.iter_content(chunk_size=1024*1024),
            status=req.status_code,
            content_type=req.headers.get('Content-Type'),
            headers=resp_headers
        )
    except Exception as e:
        return f"Proxy Error: {str(e)}", 500

@app.route('/download', methods=['POST', 'OPTIONS'])
def download_video():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    video_url = data.get('url')

    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Отдаем все данные фронтенду
            return jsonify({
                'title': info.get('title', 'TikTok Video'),
                'download_url': info.get('url'), # Прямая ссылка mp4
                'thumbnail': info.get('thumbnail')
            }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400    
    

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000)) 
    app.run(host='0.0.0.0', port=port)