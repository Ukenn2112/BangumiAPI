from xml.etree.ElementTree import tostring
from datetime import datetime, timedelta
import pytz
import requests
from flask import Flask, request
from flask_restful import Api, Resource
from lxml import etree
from waitress import serve

# 創建Flask app物件
app = Flask(__name__)
# 創建Flask api物件
api = Api(app)

session = requests.session()
session.headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

# 創建Products 物件並繼承Resource物件
class Episode(Resource):
    def get(self, episode_id):
        # 取得資料
        r = session.get(f"https://bgm.tv/ep/{episode_id}")
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
                floor_time = html.xpath(f'//div[@name="{r}"]/div[1]/small/text()')[0].lstrip(' - ').rstrip(" ")
                reply_data['floor_time'] = int(datetime.strptime(floor_time, '%Y-%m-%d %H:%M').timestamp())
                reply_data['from_name'] = html.xpath(f'//div[@name="{r}"]/div[2]/strong/a/text()')[0]
                if from_tip := html.xpath(f'//div[@name="{r}"]/div[2]/span/text()'):
                    reply_data['from_tip'] = from_tip[0].replace('(', '').replace(')', '')
                else:
                    reply_data['from_tip'] = None
                reply_data['from_link'] = "https://bgm.tv" + html.xpath(f'//div[@name="{r}"]/div[2]/strong/a/@href')[0]
                reply_data['from_avatar'] = "https:" + html.xpath(f'//div[@name="{r}"]/a/span/@style')[0].lstrip("background-image:url('").rstrip("')")
                reply_data['comment'] = tostring(html.xpath(f'//div[@name="{r}"]/div[2]/div[@class="cmt_sub_content"]')[0], encoding="utf-8").decode("utf-8").replace('<div class="cmt_sub_content">','').replace(' </div>\n','').replace('src="/', 'class="bgm-emoji" src="https://bgm.tv/')
                reply_list.append(reply_data)

            comment_data = {}
            comment_data["floor"] = i
            floor_timee = html.xpath(f'//div[@name="{i}"]/div[1]/small/text()')[0].lstrip(' - ')
            comment_data["floor_time"] = int(datetime.strptime(floor_timee, '%Y-%m-%d %H:%M').timestamp())
            comment_data["from_name"] = html.xpath(f'//div[@name="{i}"]/div[2]/strong/a/text()')[0]
            if from_tip := html.xpath(f'//div[@name="{i}"]/div[2]/span/text()'):
                comment_data['from_tip'] = from_tip[0].replace('(', '').replace(')', '')
            else:
                comment_data['from_tip'] = None
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


class Subject(Resource):
    def get(self, subject_id):
        # 取得資料
        page = request.args.get('page') or 1
        r = session.get(f"https://bgm.tv/subject/{subject_id}/comments?page={page}")
        html = etree.HTML(r.content, etree.HTMLParser(encoding='utf-8'))
        error = html.xpath('//*[@id="colunmNotice"]/div/p[1]')
        if error:
            return {"error": 'Subject not found'}, 404, { "Access-Control-Allow-Origin": "*" }
        comment_list = html.xpath('//div[@id="comment_box"]/div[@class="item clearit"]')
        comment_data_list = []
        for i in comment_list:
            comment_data = {}
            comment_data["from_name"] = i.xpath('./div/div/a/text()')[0]
            if score := i.xpath('./div/div/span[@class="starstop-s"]/span/@class'):
                comment_data["from_score"] = int(score[0].lstrip('starlight stars'))
            else:
                comment_data["from_score"] = None
            from_time: str = i.xpath('./div/div/small[@class="grey"]/text()')[0].replace('@', '').strip()
            if 'm' in from_time or 'h' in from_time or 'd' in from_time:
                now = datetime.now(pytz.timezone('Asia/Hong_Kong')).timestamp()
                timestamp = from_time.replace(' ago', '').replace('d', '*86400+').replace('h', '*3600+').replace('m', '*60+')
                timestamp = int(now - eval(timestamp[:-1]))
            else:
                timestamp = datetime.strptime(from_time, '%Y-%m-%d %H:%M').timestamp()
            comment_data["from_time"] = int(timestamp)
            comment_data["from_link"] = "https://bgm.tv" + i.xpath('./div/div/a/@href')[0]
            comment_data["from_avatar"] = "https:" + i.xpath('./a[@class="avatar"]/span/@style')[0].lstrip("background-image:url('").rstrip("')")
            comment_data["comment"] = i.xpath('./div/div[@class="text"]/p/text()')[0]
            comment_data_list.append(comment_data)
        if all_page := html.xpath('//div[@class="page_inner"]/a[@class="p"]'):
            if all_page[-1].text == '››':
                all_page = int(all_page[-2].text)
            else:
                all_page = int(all_page[-1].xpath('./@href')[0].replace('?page=', ''))
        else:
            all_page = 1
        output = {
            "subject_id": int(subject_id),
            "now_page": int(page),
            "all_page": all_page,
            "data": comment_data_list,
        }
        return output, 200, { "Access-Control-Allow-Origin": "*" }


# 建立API路由products，並將該路由導向Products物件
api.add_resource(Episode, '/episodes/comments/<int:episode_id>')
api.add_resource(Subject, '/subjects/comments/<int:subject_id>')

if __name__ == "__main__":
    serve(app, listen="127.0.0.1:8080")
