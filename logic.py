from flask import Flask, request, jsonify
from flask_cors import CORS  
import yt_dlp
import requests


proxies = {
    'http': 'http://127.0.0.1:12334',
    'https': 'http://127.0.0.1:12334',
}

try:
    response = requests.get('https://api.ipify.org?format=json', proxies=proxies, timeout=5)
    print("Твой IP через VPN:", response.json()['ip'])
except Exception as e:
    print("Ошибка подключения к прокси:", e)

app = Flask(__name__)
CORS(app, resources={r"/download": {"origins": "http://127.0.0.1:5500"}})

ydl_opts = {
        'proxy': 'http://127.0.0.1:12334',
        'format': 'best',
        'cookiefile': 'cookies.txt', 
        'force_generic_extractor': False,
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

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json() # Используем этот метод
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    video_url = data.get('url')

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
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
    app.run(debug=True, port=5000)