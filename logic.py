from flask import Flask, request, jsonify
from flask_cors import CORS  
import yt_dlp
import os

IS_RENDER = os.environ.get('RENDER')

app = Flask(__name__)
CORS(app)

def get_ydl_opts():
    opts = {
        'format': 'best',
        'nocheckcertificate': True,
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'tiktok': {
                'web_visit': True,
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.tiktok.com/',
        }
    }
    
    # Если мы НЕ на Render, используем твой локальный прокси Hiddify
    if not IS_RENDER:
        opts['proxy'] = 'http://127.0.0.1:12334'
        print("Запуск: Локально (используем прокси)")
    else:
        print("Запуск: Render (прокси отключен)")
        
    # Куки на Render загружать сложно, попробуем сначала без них
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