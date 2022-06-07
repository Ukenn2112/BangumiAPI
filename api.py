import requests
from flask import Flask
from lxml import etree
from flask_restful import Api, Resource
from xml.etree.ElementTree import tostring

# 創建Flask app物件
app = Flask(__name__)
# 創建Flask api物件
api = Api(app)

session = requests.session()

# 創建Products 物件並繼承Resource物件
class Products(Resource):
    def get(self, episode_id):
        # 取得資料
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.46",
        }
        r = session.get(f"https://bgm.tv/ep/{episode_id}", headers=headers)
        html = etree.HTML(r.content)
        error = html.xpath('//*[@id="colunmNotice"]/div/p[1]')
        if error:
            return {"error": 'Episode not found'}, 404, { "Access-Control-Allow-Origin": "*" }
        # 取得資料
        subject_id = html.xpath('//*[@id="headerSubject"]/h1/a/@href')[0].lstrip('/subject/')
        comment_list = html.xpath('//*[@id="comment_list"]/div/@name')
        comment_data_list = []
        for i in comment_list:
            reply_comment_list = html.xpath(f'//div[@name="{i}"]/div[2]/div/div[@class="topic_sub_reply"]/div/@name')
            reply_list = []
            for r in reply_comment_list:
                reply_data = {}
                reply_data['floor'] = r
                reply_data['floor_time'] = html.xpath(f'//div[@name="{r}"]/div[1]/small/text()')[0].lstrip(' - ').rstrip(" ")
                reply_data['from_name'] = html.xpath(f'//div[@name="{r}"]/div[2]/strong/a/text()')[0]
                reply_data['from_link'] = "https://bgm.tv" + html.xpath(f'//div[@name="{r}"]/div[2]/strong/a/@href')[0]
                reply_data['from_avatar'] = "https:" + html.xpath(f'//div[@name="{r}"]/a/span/@style')[0].lstrip("background-image:url('").rstrip("')")
                reply_data['comment'] = tostring(html.xpath(f'//div[@name="{r}"]/div[2]/div[@class="cmt_sub_content"]')[0], encoding="utf-8").decode("utf-8").replace('<div class="cmt_sub_content">','').replace(' </div>\n','').replace('src="/', 'class="bgm-emoji" src="https://bgm.tv/')
                reply_list.append(reply_data)

            comment_data = {}
            comment_data["floor"] = i
            comment_data["floor_time"] = html.xpath(f'//div[@name="{i}"]/div[1]/small/text()')[0].lstrip(' - ')
            comment_data["from_name"] = html.xpath(f'//div[@name="{i}"]/div[2]/strong/a/text()')[0]
            comment_data["from_link"] = "https://bgm.tv" + html.xpath(f'//div[@name="{i}"]/div[2]/strong/a/@href')[0]
            comment_data["from_avatar"] = "https:" + html.xpath(f'//div[@name="{i}"]/a/span/@style')[0].lstrip("background-image:url('").rstrip("')")
            comment_data["comment"] = tostring(html.xpath(f'//div[@name="{i}"]/div[2]/div/div[@class="message clearit"]')[0], encoding="utf-8").decode("utf-8").replace('<div class="message clearit">\n','').replace(' </div>\n','').replace('src="/', 'class="bgm-emoji" src="https://bgm.tv/')
            comment_data["reply"] = reply_list
            comment_data_list.append(comment_data)

        output = {
            "ep_id": int(episode_id),
            "subject_id": int(subject_id),
            "comment": len(comment_list),
            "data": comment_data_list,
        }
        return output, 200, { "Access-Control-Allow-Origin": "*" }


# 建立API路由products，並將該路由導向Products物件
api.add_resource(Products, '/episodes/comments/<int:episode_id>')

if __name__ == "__main__":
    app.run('0.0.0.0', port=8080, debug=False)
