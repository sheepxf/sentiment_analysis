import time
import os
import json
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

# 输入文件路径
input_path = "../json/movie_comment.json"
# 输出文件路径
now_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
output_path = f"json/{now_time}_comment_emotion.json"

# 创建输出目录（如果不存在）
os.makedirs(os.path.dirname(output_path), exist_ok=True)

try:
    # 读取 JSON 输入文件
    with open(input_path, 'r', encoding='UTF-8') as f:
        data = json.load(f)

    # 提取评论内容
    comment_contents = [item["comment_content"] for item in data if isinstance(data, list) and "comment_content" in item]

    if not comment_contents:
        raise ValueError("No comments found in input file")

    # 执行情感分析
    semantic_cls = pipeline(Tasks.text_classification, 'damo/nlp_structbert_sentiment-classification_chinese-tiny')
    results = semantic_cls(input=comment_contents)

    # 处理分析结果
    processed_results = []
    for item in results:
        pos_label, pos_probs = sorted(zip(item['labels'], item['scores']), key=lambda x: x[0] == '正面', reverse=True)[0]
        neg_label, neg_probs = sorted(zip(item['labels'], item['scores']), key=lambda x: x[0] == '正面', reverse=True)[1]
        is_positive = 1 if pos_probs >= neg_probs else 0

        processed_result = {
            "is_positive": is_positive,
            "positive_probs": pos_probs,
            "negative_probs": neg_probs
        }
        processed_results.append(processed_result)

    # 写入 JSON 输出文件
    with open(output_path, 'w', encoding='UTF-8') as f:
        json.dump(processed_results, f, ensure_ascii=False, indent=2)

    print({"code": 1, "msg": f"Success! Results saved to {output_path}"})

except FileNotFoundError:
    print({"code": 0, "msg": "Input file not found"})
except json.JSONDecodeError:
    print({"code": 0, "msg": "Invalid JSON format"})
except ValueError as ve:
    print({"code": 0, "msg": str(ve)})