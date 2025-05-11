from flask import Flask,render_template

app = Flask(__name__,template_folder='templates')

#你们函数名称统一一下，爬虫就叫douban_crawler,情感分析就叫sentiment_analysis
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        movie_name = request.form['movie_name']
    #调用函数部分

        start_time = time.time()
        result = douban_crawler(movie_name)

        if result:
            # 计算处理时间
            process_time = round(time.time() - start_time, 2)
            return render_template('result.html',
                                   movie_name=movie_name,
                                   data=result,
                                   time=process_time)
        else:
            return render_template('index.html',
                                   error="未找到相关电影或爬取失败")

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

