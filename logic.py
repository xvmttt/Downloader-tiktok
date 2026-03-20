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

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': 'https://www.tiktok.com/'
    }

    try:
        # verify=False убирает ошибки SSL, которые часто бывают на Render
        req = requests.get(video_url, headers=headers, stream=True, timeout=20, verify=False)
        
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

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json() # Используем этот метод
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    video_url = data.get('url')

    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(video_url, download=False)

            result = {
                    'title': info.get('title', 'TikTok Video'),
                    'download_url': info.get('url'), # Это прямая ссылка
                    'thumbnail': info.get('thumbnail')
                }
            return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port, host='0.0.0.0')