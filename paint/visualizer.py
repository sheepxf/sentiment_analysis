# visualizer.py - 可视化模块
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import jieba
from wordcloud import WordCloud
from matplotlib.font_manager import FontProperties, fontManager
import os


class Visualizer:
    def __init__(self):
        # 配置字体
        self.font_path = "past/SimHei.ttf"  # 确保字体文件在应用目录中
        fontManager.addfont(self.font_path)
        self.font = FontProperties(fname=self.font_path)

        # 设置中文字体
        plt.rcParams["font.family"] = self.font.get_name()
        plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题
        plt.rcParams["font.size"] = 14

        # 创建结果目录
        self.results_dir = 'static/results'
        os.makedirs(self.results_dir, exist_ok=True)

    def generate_charts(self, comments, sentiment_results, movie_info):
        # 情感分布饼图
        positive_count = sum(1 for r in sentiment_results if r['is_positive'] == 1)
        negative_count = len(sentiment_results) - positive_count

        plt.figure(figsize=(8, 6))
        plt.pie(
            [positive_count, negative_count],
            labels=['正面评价', '负面评价'],
            autopct='%1.1f%%',
            startangle=90,
            colors=['#66BB6A', '#EF5350']
        )
        plt.axis('equal')
        plt.title(f"{movie_info['title']} ({movie_info['year']}) 影评情感分布")
        pie_chart_path = os.path.join(self.results_dir, f"pie_{movie_info['movie_id']}.png")
        plt.savefig(pie_chart_path)
        plt.close()

        # 评分与情感关系散点图
        ratings = [c['comment_rating'] for c in comments]
        positive_probs = [r['positive_probs'] for r in sentiment_results]

        plt.figure(figsize=(10, 6))
        plt.scatter(ratings, positive_probs, alpha=0.6, color='#42A5F5')
        plt.xlabel('用户评分')
        plt.ylabel('正面情感概率')
        plt.title(f"{movie_info['title']} 评分与情感关系")
        plt.grid(True, linestyle='--', alpha=0.7)
        scatter_path = os.path.join(self.results_dir, f"scatter_{movie_info['movie_id']}.png")
        plt.savefig(scatter_path)
        plt.close()

        # 生成词云
        all_comments = ' '.join([c['comment_content'] for c in comments])
        cut_text = " ".join(jieba.lcut(all_comments))

        # 从文件加载停用词
        try:
            with open('userless.txt', 'r', encoding='utf-8') as f:
                stopwords = set(f.read().split())
        except FileNotFoundError:
            # 如果停用词文件不存在，使用默认停用词
            stopwords = set(
                ['的', '了', '和', '是', '在', '我', '有', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到',
                 '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'])

        # 添加一些额外的停用词
        stopwords.update(['电影', '一部', '感觉', '觉得', '非常', '那个', '真的', '这个', '就是', '还是'])

        wordcloud = WordCloud(
            width=800, height=400,
            background_color='white',
            font_path=self.font_path,
            stopwords=stopwords,
            max_words=100,
            max_font_size=100,
            random_state=42
        ).generate(cut_text)

        plt.figure(figsize=(10, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f"{movie_info['title']} 影评词云")
        wordcloud_path = os.path.join(self.results_dir, f"wordcloud_{movie_info['movie_id']}.png")
        plt.savefig(wordcloud_path)
        plt.close()

        return {
            'pie_chart': pie_chart_path,
            'scatter_plot': scatter_path,
            'wordcloud': wordcloud_path
        }