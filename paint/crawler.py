# crawler.py - 爬虫模块
import requests
from bs4 import BeautifulSoup
import time
import re


class DoubanCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_movie_info(self, movie_id):
        url = f"https://movie.douban.com/subject/{movie_id}/"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.find('span', property='v:itemreviewed').get_text().strip()
            rating = soup.find('strong', property='v:average').get_text().strip()
            year = soup.find('span', class_='year').get_text().strip('()')

            # 获取电影封面图片
            try:
                cover = soup.find('img', rel='v:photo')['src']
            except:
                cover = 'https://picsum.photos/200/300'  # 默认图片

            return {
                'movie_id': movie_id,
                'title': title,
                'rating': rating,
                'year': year,
                'cover': cover
            }
        except Exception as e:
            print(f"获取电影信息失败: {e}")
            return {
                'movie_id': movie_id,
                'title': '未知标题',
                'rating': '0',
                'year': '未知年份',
                'cover': 'https://picsum.photos/200/300'
            }

    def get_movie_comments(self, movie_id, pages=1):
        comments = []
        base_url = f"https://movie.douban.com/subject/{movie_id}/comments"

        for start in range(0, pages * 20, 20):
            url = f"{base_url}?start={start}&limit=20&status=P&sort=new_score"
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                comment_items = soup.find_all('div', class_='comment-item')

                for item in comment_items:
                    comment_id = item.get('data-cid')
                    rating_span = item.find("span", class_=re.compile(r'allstar\d+ rating'))
                    if rating_span:
                        score = rating_span["class"][0].split('allstar')[1]
                        comment_rating = int(score) / 10
                    else:
                        comment_rating = 0  # 没有评分的情况

                    comment_content = item.find('span', class_='short').get_text().strip()
                    comment_info = {
                        'comment_cid': comment_id,
                        'comment_rating': comment_rating,
                        'comment_content': comment_content
                    }
                    comments.append(comment_info)

                # 避免请求过于频繁
                time.sleep(2)

            except requests.RequestException as e:
                print(f"请求出错: {e}")
            except Exception as e:
                print(f"发生未知错误: {e}")

        return comments