# app.py - 主应用文件
from flask import Flask, render_template, request, jsonify, send_file
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
import threading
import queue
from datetime import datetime
import os

# 导入各个功能模块
from crawler import DoubanCrawler
from sentiment_analyzer import SentimentAnalyzer
from visualizer import Visualizer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
Bootstrap(app)

# 创建各个功能实例
crawler = DoubanCrawler()
analyzer = SentimentAnalyzer()
visualizer = Visualizer()

# 任务队列和结果存储
task_queue = queue.Queue()
task_results = {}


# 表单类 - 用于收集用户输入
class MovieForm(FlaskForm):
    movie_id = StringField('豆瓣电影ID', validators=[DataRequired()])
    pages = IntegerField('爬取页数', default=1, validators=[DataRequired()])
    submit = SubmitField('开始分析')


# 处理任务的工作线程
def task_worker():
    while True:
        task_id, movie_id, pages = task_queue.get()
        try:
            # 更新任务状态为处理中
            task_results[task_id]['status'] = 'processing'

            # 获取电影信息和评论
            movie_info = crawler.get_movie_info(movie_id)
            comments = crawler.get_movie_comments(movie_id, pages)

            if not comments:
                task_results[task_id] = {
                    'status': 'error',
                    'message': '未能获取到任何评论，请检查电影ID是否正确'
                }
                continue

            # 情感分析
            sentiment_results = analyzer.analyze(comments)

            # 合并结果
            for i in range(len(comments)):
                comments[i].update(sentiment_results[i])

            # 生成图表
            charts = visualizer.generate_charts(comments, sentiment_results, movie_info)

            # 计算统计数据
            positive_ratio = sum(1 for c in comments if c['is_positive'] == 1) / len(comments)
            average_rating = sum(c['comment_rating'] for c in comments) / len(comments)

            # 更新任务结果
            task_results[task_id] = {
                'status': 'completed',
                'movie_info': movie_info,
                'comments': comments,
                'charts': charts,
                'stats': {
                    'total_comments': len(comments),
                    'positive_ratio': positive_ratio,
                    'average_rating': average_rating
                }
            }
        except Exception as e:
            task_results[task_id] = {
                'status': 'error',
                'message': f'处理过程中出错: {str(e)}'
            }
        finally:
            task_queue.task_done()


# 启动工作线程
worker_thread = threading.Thread(target=task_worker, daemon=True)
worker_thread.start()


# 路由
@app.route('/', methods=['GET', 'POST'])
def index():
    form = MovieForm()
    task_id = None

    if form.validate_on_submit():
        # 生成唯一任务ID
        task_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
        movie_id = form.movie_id.data
        pages = form.pages.data

        # 初始化任务状态
        task_results[task_id] = {
            'status': 'queued',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # 添加任务到队列
        task_queue.put((task_id, movie_id, pages))

    return render_template('index.html', form=form, task_id=task_id)


@app.route('/task_status/<task_id>')
def task_status(task_id):
    result = task_results.get(task_id, {'status': 'unknown'})
    return jsonify(result)


@app.route('/result/<task_id>')
def result(task_id):
    result = task_results.get(task_id)

    if not result or result['status'] == 'unknown':
        return "任务不存在或已过期", 404

    if result['status'] != 'completed':
        return "任务尚未完成，请稍后再试", 400

    return render_template('result.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)