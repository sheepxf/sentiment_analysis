import time
import os
import csv
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

if __name__ == '__main__':
    # 将书籍评论文件名替换为自己实验使用的书评文件名
    path = "csv/20230208225135_book_comment.csv"
    if not os.path.exists(path):
        print({"code": 0, "msg": "file is not exists"})
    now_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    analysis_path = "csv/" + now_time + "_comment_emotion.csv"
    key_list = ["is_positive", "positive_probs", "negative_probs"]

    # 评论内容列表
    comment_contents = []
    with open(path, encoding="UTF-8") as file:
        c_csv = list(csv.reader(file))
        c_header = c_csv[0]
        # 获取评论内容
        for i in range(1, len(c_csv)):
            comment_contents.append(c_csv[i][6])

    semantic_cls = pipeline(Tasks.text_classification, 'damo/nlp_structbert_sentiment-classification_chinese-tiny')
    result = semantic_cls(input=comment_contents)

    # 新建文件存储情感数据
    with open(analysis_path, 'w', newline='', encoding='UTF-8') as file:
        writer = csv.DictWriter(file, fieldnames=key_list)
        writer.writeheader()
        for item in result:
            sorted_labels_scores = sorted(zip(item['labels'], item['scores']), key=lambda x: x[0] == '正面', reverse=True)
            positive_label, positive_probs = sorted_labels_scores[0]
            negative_label, negative_probs = sorted_labels_scores[1]
            is_positive = 1 if positive_probs >= negative_probs else 0
            value = {"is_positive": is_positive, "positive_probs": format(positive_probs, ".4f"), "negative_probs": format(negative_probs, ".4f")}
            writer.writerow(value)
    print({"code": 1, "msg": "success"})