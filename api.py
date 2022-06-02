import json
import requests
# 載入Flask套件
from flask import Flask
# 載入Flask RestFul 套件
from flask_restful import Api, Resource

# 創建Flask app物件
app = Flask(__name__)
# 創建Flask api物件
api = Api(app)

# 創建Products 物件並繼承Resource物件
class Products(Resource):
    def get(self, episode_id):
        # 取得資料
        user_agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/99.0.4844.51 Safari/537.36'
        )
        r = requests.get(f'https://api.bgm.tv/v0/episodes/{episode_id}', headers={'User-Agent': user_agent})
        # 回傳資料
        data = json.loads(r.text)
        output = {
            "ep_id": data['id'],
            "subject_id": data['subject_id'],
            "comment": data['comment'],
            "data": [
                {   
                    "floor": "1",
                    "from_name": "河豚酱fuguchan",
                    "from_link": "https://bgm.tv/user/fuguchan1145141",
                    "from_avatar": "https://lain.bgm.tv/pic/user/l/000/62/03/620315.jpg?r=1628535454",
                    "comment": "长颈龙分镜，复刻明日酱ep8？",
                    "reply": [
                        {
                            "floor": "1-1",
                            "from_name": "河豚酱fuguchan",
                            "from_link": "https://bgm.tv/user/fuguchan1145141",
                            "from_avatar": "https://lain.bgm.tv/pic/user/l/000/62/03/620315.jpg?r=1628535454",
                            "comment": "长颈龙分镜，复刻明日酱ep8？",
                            "reply": [],
                        },
                        {
                            "floor": "1-2",
                            "from_name": "河豚酱fuguchan",
                            "from_link": "https://bgm.tv/user/fuguchan1145141",
                            "from_avatar": "https://lain.bgm.tv/pic/user/l/000/62/03/620315.jpg?r=1628535454",
                            "comment": "长颈龙分镜，复刻明日酱ep8？",
                            "reply": [],
                        },
                    ],
                },
            ]
        }
        return output, 200

# 建立API路由products，並將該路由導向Products物件
api.add_resource(Products, '/episodes/comments/<int:episode_id>')

if __name__ == "__main__":
    app.run(port=8080, debug=True)