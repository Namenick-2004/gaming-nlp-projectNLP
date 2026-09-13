"""
Generates the "Model Evaluation" report (accuracy, precision, recall,
F1, confusion matrix) that the frontend's Model Evaluation page reads.

Run this AFTER training, against the *_test_holdout.csv files that
train_*.py set aside — never against data the model has seen.

Usage:
    python evaluate.py --task sentiment --model ../models/sentiment/wangchanberta_sentiment --data sentiment_test_holdout.csv
    python evaluate.py --task emotion   --model ../models/emotion/wangchanberta_emotion     --data emotion_test_holdout.csv
    python evaluate.py --task category  --model ../models/category/wangchanberta_category   --data category_test_holdout.csv
"""
import argparse
import json
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support, confusion_matrix, f1_score
)
from transformers import AutoTokenizer, AutoModelForSequenceClassification

TASK_LABELS = {
    "sentiment": ["negative", "neutral", "positive"],
    "emotion": ["joy", "anger", "sadness", "surprise", "fear", "neutral"],
    "category": ["gameplay", "character", "weapon", "map", "graphics", "update",
                 "bug", "ranking", "skin", "price", "performance", "other"],
}


def evaluate_single_label(model_path, data_path, task):
    labels = TASK_LABELS[task]
    label2id = {l: i for i, l in enumerate(labels)}
    df = pd.read_csv(data_path)
    col = "sentiment" if task == "sentiment" else "emotion"
    y_true = df[col].map(label2id).tolist()

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path).eval()

    y_pred = []
    with torch.no_grad():
        for text in df["text"]:
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
            logits = model(**inputs).logits
            y_pred.append(int(torch.argmax(logits, dim=-1)))

    acc = accuracy_score(y_true, y_pred)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=range(len(labels)), zero_division=0
    )
    cm = confusion_matrix(y_true, y_pred, labels=range(len(labels))).tolist()
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)

    report = {
        "model_name": task,
        "accuracy": round(acc, 4),
        "macro_f1": round(macro_f1, 4),
        "per_class": [
            {"label": lab, "precision": round(p, 4), "recall": round(r, 4),
             "f1": round(f, 4), "support": int(s)}
            for lab, p, r, f, s in zip(labels, precision, recall, f1, support)
        ],
        "confusion_matrix": cm,
        "labels": labels,
    }
    return report


def evaluate_multilabel(model_path, data_path):
    from sklearn.preprocessing import MultiLabelBinarizer
    labels = TASK_LABELS["category"]
    df = pd.read_csv(data_path)
    df["labels_list"] = df["category"].apply(lambda s: [c.strip() for c in s.split(";")])
    mlb = MultiLabelBinarizer(classes=labels)
    y_true = mlb.fit_transform(df["labels_list"])

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path).eval()

    y_pred = []
    with torch.no_grad():
        for text in df["text"]:
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
            probs = torch.sigmoid(model(**inputs).logits).squeeze().tolist()
            y_pred.append([1 if p >= 0.5 else 0 for p in probs])
    y_pred = np.array(y_pred)

    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    micro_f1 = f1_score(y_true, y_pred, average="micro", zero_division=0)
    acc = accuracy_score(y_true, y_pred)  # exact match accuracy

    per_class = []
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, zero_division=0
    )
    for lab, p, r, f, s in zip(labels, precision, recall, f1, support):
        per_class.append({"label": lab, "precision": round(p, 4), "recall": round(r, 4),
                           "f1": round(f, 4), "support": int(s)})

    return {
        "model_name": "category",
        "accuracy": round(acc, 4),
        "macro_f1": round(macro_f1, 4),
        "micro_f1": round(micro_f1, 4),
        "per_class": per_class,
        "confusion_matrix": [],  # not meaningful for multi-label; per-class PR shown instead
        "labels": labels,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, choices=["sentiment", "emotion", "category"])
    parser.add_argument("--model", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", default=None, help="Write JSON report here")
    args = parser.parse_args()

    if args.task == "category":
        report = evaluate_multilabel(args.model, args.data)
    else:
        report = evaluate_single_label(args.model, args.data, args.task)

    out_path = args.out or f"{args.task}_evaluation_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nSaved report to {out_path}")


if __name__ == "__main__":
    main()
