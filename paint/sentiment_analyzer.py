from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import torch  # 新增：用于设备检测


class SentimentAnalyzer:
    def __init__(self):
        try:
            # 检测是否支持 GPU（避免硬编码 device 参数）
            device = 0 if torch.cuda.is_available() else -1

            # 初始化情感分析模型（移除 deprecated 的 device 参数）
            self.semantic_cls = pipeline(
                Tasks.text_classification,
                'damo/nlp_structbert_sentiment-classification_chinese-tiny',
                # 移除 device 参数，modelscope 会自动处理设备分配
            )
        except Exception as e:
            print(f"情感分析模型加载失败: {e}")
            self.semantic_cls = None

    def analyze(self, comments):
        if not self.semantic_cls:
            return [{'is_positive': 0, 'positive_probs': 0.5, 'negative_probs': 0.5} for _ in comments]

        comment_contents = [item["comment_content"] for item in comments if "comment_content" in item]

        if not comment_contents:
            print("警告：未检测到有效评论内容")
            return []

        try:
            # 直接调用模型获取结果（模型自动适配设备）
            results = self.semantic_cls(input=comment_contents)
        except Exception as e:
            print(f"情感分析失败: {e}")
            return []

        processed_results = []
        for item in results:
            # 解析标签和概率（更简洁的排序方式）
            labels = item['labels']
            scores = item['scores']
            pos_idx = labels.index('正面') if '正面' in labels else 0
            neg_idx = 1 - pos_idx  # 假设标签只有正反两类

            is_positive = 1 if scores[pos_idx] >= scores[neg_idx] else 0
            processed_result = {
                "is_positive": is_positive,
                "positive_probs": scores[pos_idx],
                "negative_probs": scores[neg_idx]
            }
            processed_results.append(processed_result)

        return processed_results