import os
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import json
import jieba
from wordcloud import WordCloud
from matplotlib.font_manager import FontProperties, fontManager

# 手动添加字体
font_path = "/home/feng/桌面/sentiment_analysis/paint/SimHei.ttf"
fontManager.addfont(font_path)
font = FontProperties(fname=font_path)

# 数据处理路径（假设影评数据文件名为 movie_xxx.json）
movie_path = os.getcwd() + "/json/" + "movie_info.json"  # 电影信息
comment_path = os.getcwd() + "/json/" + "movie_comment.json"  # 影评内容
emotion_path = os.getcwd() + "/json/" + "comment_emotion.json"  # 情感分析结果

# 字段名适配影评场景（将 "book" 改为 "movie"）
movie_name = "movie_name"
movie_id = "movie_id"  # 原 book_id 改为 movie_id
is_positive = "is_positive"
comment_content = "comment_content"


# 生成柱状图并保存为文件
def generate_bar_chart():
    movie_names = []
    total_comments = []
    positive_comments = []
    negative_comments = []

    with open(movie_path, 'r', encoding="UTF-8") as m_file, \
            open(comment_path, 'r', encoding="UTF-8") as c_file, \
            open(emotion_path, 'r', encoding='UTF-8') as e_file:

        movies = json.load(m_file)
        comments = json.load(c_file)
        emotions = json.load(e_file)

        for i in range(len(movies)):
            movie_names.append(movies[i][movie_name])
            total = 0
            positive = 0
            negative = 0
            for j in range(len(comments)):
                if movies[i][movie_id] == comments[j][movie_id]:
                    total += 1
                    if emotions[j][is_positive] == 1:
                        positive += 1
                    else:
                        negative += 1
            total_comments.append(total)
            positive_comments.append(positive)
            negative_comments.append(negative)

    # 绘制柱状图
    plt.figure(figsize=(12, 6))
    x = np.arange(len(movie_names))
    width = 0.25
    plt.bar(x - width, total_comments, width, label='总评论数')
    plt.bar(x, positive_comments, width, label='积极评论')
    plt.bar(x + width, negative_comments, width, label='消极评论')

    plt.ylabel('数量', fontproperties=font)
    plt.title('电影评论情感分布', fontproperties=font)
    plt.xticks(x, movie_names, rotation=45, fontproperties=font)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)

    # 保存为文件（避免中文路径问题，使用英文名称）
    chart_path = "movie_comment_bar.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    return chart_path


# 生成词云图并保存为文件
def generate_wordcloud(movie_id):
    comment_text = ""
    with open(comment_path, 'r', encoding="UTF-8") as c_file, \
            open(movie_path, 'r', encoding="UTF-8") as m_file:
        comments = json.load(c_file)
        movies = json.load(m_file)

        # 过滤指定电影的评论
        target_movie_comments = [c[comment_content] for c in comments if c[movie_id] == movie_id]
        comment_text = " ".join(target_movie_comments)

    if not comment_text:
        print({"code": -1, "message": "无该电影的评论数据"})
        return None

    # 分词与停用词处理
    cut_text = " ".join(jieba.lcut(comment_text))
    with open('userless.txt', 'r', encoding='utf-8') as f:
        stopwords = f.read().split() + ['\n', '，', ' ', '的', '了']  # 补充常用停用词

    # 生成词云
    wordcloud = WordCloud(
        font_path=font_path,
        width=800, height=400,
        background_color='white',
        stopwords=stopwords,
        max_words=300
    ).generate(cut_text)

    # 保存为文件
    wordcloud_path = f"movie_{movie_id}_wordcloud.png"
    wordcloud.to_file(wordcloud_path)
    return wordcloud_path


if __name__ == '__main__':
    # 生成柱状图
    bar_chart = generate_bar_chart()

    # 生成指定电影的词云（假设电影 ID 为 6518605，需根据实际数据修改）
    wordcloud_img = generate_wordcloud("6518605")

    print(f"柱状图保存路径：{bar_chart}")
    print(f"词云图保存路径：{wordcloud_img}")