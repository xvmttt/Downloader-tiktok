import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) 

TIKWM_API_URL = "https://www.tikwm.com/api/"

@app.route('/download', methods=['POST']) # Уберите 'OPTIONS' из методов, Flask-CORS сам их обработает
def download_video():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json()
    video_url = data.get('url')
    
    if not video_url:
        return jsonify({'message': 'URL is required'}), 400

    try:
        # Отправляем запрос к бесплатному API TikWM
        response = requests.get(TIKWM_API_URL, params={'url': video_url})
        res_data = response.json()

        if res_data.get('code') == 0:
            video_info = res_data['data']
            return jsonify({
                'title': video_info.get('title', 'TikTok Video'),
                # 'play' - это видео без водяного знака
                'download_url': "https://www.tikwm.com" + video_info.get('play'),
                'author': video_info.get('author', {}).get('nickname')
            }), 200
        else:
            return jsonify({'message': 'TikTok API error: ' + res_data.get('msg', 'Unknown')}), 400

    except Exception as e:
        return jsonify({'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)