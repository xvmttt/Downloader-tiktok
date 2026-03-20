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

@app.route('/proxy_video')
def proxy_video():
    video_url = request.args.get('url')
    if not video_url:
        return "No URL provided", 400

    cookies_content = os.environ.get('TIKTOK_COOKIES', '')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'video/webapp,video/*,*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.tiktok.com/',
        'Origin': 'https://www.tiktok.com/',
        'Range': 'bytes=0-', 
        'Cookie': cookies_content,
        'Sec-Fetch-Dest': 'video',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'cross-site',
    }

    try:
        # Делаем запрос. timeout 30 секунд, так как проксирование может быть медленным
        req = requests.get(video_url, headers=headers, stream=True, timeout=30, verify=False)
        
        # Если TikTok вернул что-то маленькое (заглушку), мы увидим это в логах Render
        content_length = req.headers.get('Content-Length')
        if content_length and int(content_length) < 5000:
            print(f">>> ВНИМАНИЕ: TikTok отдал файл размером всего {content_length} байт. Это заглушка!")

        # Формируем ответ для браузера
        response = Response(
            req.iter_content(chunk_size=1024*1024),
            status=req.status_code,
            content_type=req.headers.get('Content-Type', 'video/mp4')
        )
        
        # Пробрасываем важные заголовки обратно в браузер
        response.headers['Content-Disposition'] = 'attachment; filename=video.mp4'
        response.headers['Access-Control-Allow-Origin'] = '*'
        # Если TikTok поддерживает докачку (Range), сообщаем об этом браузеру
        if 'Content-Range' in req.headers:
            response.headers['Content-Range'] = req.headers['Content-Range']
            response.status_code = 206 # Partial Content

        return response

    except Exception as e:
        print(f">>> Ошибка проксирования: {str(e)}")
        return f"Proxy Error: {str(e)}", 500

def get_ydl_opts():
    cookies_content = os.environ.get('TIKTOK_COOKIES')
    cookie_file_path = '/tmp/temp_cookies.txt' if IS_RENDER else 'temp_cookies.txt'

    if cookies_content:
        try:
            with open(cookie_file_path, 'w', encoding='utf-8') as f:
                f.write(cookies_content)
        except:
            pass
    opts = {
        'format': 'best',
        'nocheckcertificate': True,
        'quiet': True,
        'no_warnings': True,
        'cookiefile': cookie_file_path if os.path.exists(cookie_file_path) else None,
        'extractor_args': {'tiktok': {'web_visit': True}},
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Referer': 'https://www.tiktok.com/',
        }
    }
    
    if not IS_RENDER:
        opts['proxy'] = 'http://127.0.0.1:12334'
        # Если дома файл называется иначе, поправь здесь:
        if os.path.exists('cookies.txt'):
            opts['cookiefile'] = 'cookies.txt'
            
    return opts

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