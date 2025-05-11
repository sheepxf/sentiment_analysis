import requests
from bs4 import BeautifulSoup
import time
import re
import json

def get_movie_comments(movie_id, pages=1):
    comments = []
    base_url = f"https://movie.douban.com/subject/{movie_id}/comments"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for start in range(0, pages * 20, 20):
        url = f"{base_url}?start={start}&limit=20&status=P&sort=new_score"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            comment_items = soup.find_all('div', class_='comment-item')
            print(comment_items)
            comments=[]
            for item in comment_items:
                comment_id=item.get('data-cid')
                rating_span = item.find("span", class_=re.compile(r'allstar\d+ rating'))
                score=rating_span["class"][0].split('allstar')[1]
                comment_rating=int(score)/10

                comment_content=item.find('span',class_='short').get_text().strip()
                comment_info={
                    'comment_cid':comment_id,
                    'comment_rating':comment_rating,
                    'comment_content':comment_content
                }
                comments.append(comment_info)

            # 避免请求过于频繁，设置适当的延迟
            time.sleep(2)

        except requests.RequestException as e:
            print(f"请求出错: {e}")
        except Exception as e:
            print(f"发生未知错误: {e}")

    return comments

def get_movie_inf(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)

    bs = BeautifulSoup(response.text, "html.parser")
    items = bs.find_all('div', class_='item')
    movies = []
    for item in items:
        movie_url = item.find('a', href=True)['href']
        movie_id = movie_url.split('/')[-2]
        movie_title = item.find('span', class_='title').get_text().strip()
        movie_rating = item.find('span', class_='rating_num').get_text().strip()
        movies.append({
            "movie_id": movie_id,
            "movie_title": movie_title,
            "movie_rating": movie_rating,

        })
    with open('json/movie_info.json', 'w', encoding='utf-8') as f:
            json.dump(movies, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    url = "https://movie.douban.com/top250"
    get_movie_inf(url)
    movie_id = "1291546"
    movie_comments = get_movie_comments(movie_id)
    for comment in movie_comments:
        print(comment)