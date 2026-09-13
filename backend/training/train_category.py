"""
Fine-tunes WangchanBERTa for MULTI-LABEL gaming-topic classification
(12 classes). The CSV's `category` column holds semicolon-separated
labels per comment, e.g. "character;gameplay".

Usage:
    python train_category.py --data dataset_sample.csv --output ../models/category/wangchanberta_category
"""
import argparse
import numpy as np
import pandas as pd
from datasets import Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score
from sklearn.preprocessing import MultiLabelBinarizer
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer, TrainerCallback
from training_progress import ProgressFileCallback

LABELS = ["gameplay", "character", "weapon", "map", "graphics", "update",
          "bug", "ranking", "skin", "price", "performance", "other"]
BASE_MODEL = "airesearch/wangchanberta-base-att-spm-uncased"
THRESHOLD = 0.5


class EpochProgressCallback(TrainerCallback):
    def on_epoch_end(self, args, state, control, **kwargs):
        print(f"Epoch {state.epoch:.0f}/{args.num_train_epochs} complete", flush=True)


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    probs = 1 / (1 + np.exp(-logits))
    preds = (probs >= THRESHOLD).astype(int)
    macro_f1 = f1_score(labels, preds, average="macro", zero_division=0)
    micro_f1 = f1_score(labels, preds, average="micro", zero_division=0)
    subset_acc = accuracy_score(labels, preds)  # exact-match accuracy
    return {"macro_f1": macro_f1, "micro_f1": micro_f1, "subset_accuracy": subset_acc}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="dataset_sample.csv")
    parser.add_argument("--output", default="../models/category/wangchanberta_category")
    parser.add_argument("--epochs", type=int, default=5)
    args = parser.parse_args()

    df = pd.read_csv(args.data)[["text", "category"]].dropna()
    df["labels_list"] = df["category"].apply(lambda s: [c.strip() for c in s.split(";")])

    mlb = MultiLabelBinarizer(classes=LABELS)
    label_matrix = mlb.fit_transform(df["labels_list"]).astype(float)
    df["labels"] = list(label_matrix)

    train_df, temp_df = train_test_split(df, test_size=0.2, random_state=42)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42)
    test_df.drop(columns=["labels"]).to_csv("category_test_holdout.csv", index=False)

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

    def tokenize(batch):
        enc = tokenizer(batch["text"], truncation=True, padding="max_length", max_length=256)
        enc["labels"] = batch["labels"]
        return enc

    train_ds = Dataset.from_pandas(train_df[["text", "labels"]]).map(tokenize, batched=True)
    val_ds = Dataset.from_pandas(val_df[["text", "labels"]]).map(tokenize, batched=True)

    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL, num_labels=len(LABELS), problem_type="multi_label_classification"
    )

    training_args = TrainingArguments(
        output_dir="./checkpoints_category",
        num_train_epochs=args.epochs,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        logging_steps=10,
    )

    trainer = Trainer(model=model, args=training_args, train_dataset=train_ds,
                       eval_dataset=val_ds, compute_metrics=compute_metrics,
                       callbacks=[EpochProgressCallback(), ProgressFileCallback("category")])
    trainer.train()
    trainer.save_model(args.output)
    tokenizer.save_pretrained(args.output)
    print(f"Saved fine-tuned category model to {args.output}")


if __name__ == "__main__":
    main()
