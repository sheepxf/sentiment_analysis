from urllib.parse import parse_qs, urlparse
from bs4 import BeautifulSoup
import json
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
url = "https://movie.douban.com/top250"

response=requests.get(url,headers=headers)

bs = BeautifulSoup(response.text, "html.parser")
print(bs)
#items=bs.find_all("div",{"class":"comment-item"})
#print(items)
#comments=[]

#for item in items:
    #comment_avatar=item.find("a")
    #comment_nickname=comment_avatar['href'].split('/')[-2]
    #comment_content=item.find("span",class_="short").get_text().strip()
        #rating_span=item.find("span", class_=re.compile(r'allstar\d+ rating'))
        #comment_rating=rating_span["class"][0].split('allstar')[1]
        #score=int(comment_rating)/10
    #comments.append({
     #       "comment_avatar":comment_nickname,
            #"comment_rating":score,
      #      "comment_content":comment_content,
      #  })

#with open("json/movie_comment.json", "w", encoding='utf-8')as f:
        #json.dump(comments,f,ensure_ascii=False,indent=4)

items=bs.find_all('div',class_='item')
movies=[]
for item in items:
    movie_url=item.find('a',href=True)['href']
    movie_id=movie_url.split('/')[-2]
    movie_title=item.find('span',class_='title').get_text().strip()
    movie_rating=item.find('span',class_='rating_num').get_text().strip()
    movies.append({
        "movie_id":movie_id,
        "movie_title":movie_title,
        "movie_rating":movie_rating,

            })

    with open('json/movie.json', 'w', encoding='utf-8') as f:
            json.dump(movies, f, ensure_ascii=False, indent=4)

