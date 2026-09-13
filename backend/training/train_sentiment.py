"""
Fine-tunes WangchanBERTa for 3-class sentiment classification on a
CSV with columns: text, sentiment (positive|neutral|negative).

Usage:
    python train_sentiment.py --data dataset_sample.csv --output ../models/sentiment/wangchanberta_sentiment

This is a *reference* training script sized for a student project —
it prioritizes clarity over speed/scale. Swap dataset_sample.csv for
a larger, properly-labeled gaming-comments dataset before relying on
the resulting model for anything beyond a course demo.
"""
import argparse
import numpy as np
import pandas as pd
from datasets import Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, TrainerCallback,
)
from training_progress import ProgressFileCallback

LABELS = ["negative", "neutral", "positive"]
LABEL2ID = {l: i for i, l in enumerate(LABELS)}
BASE_MODEL = "airesearch/wangchanberta-base-att-spm-uncased"


class EpochProgressCallback(TrainerCallback):
    def on_epoch_end(self, args, state, control, **kwargs):
        print(f"Epoch {state.epoch:.0f}/{args.num_train_epochs} complete", flush=True)


def load_dataset(csv_path: str):
    df = pd.read_csv(csv_path)
    df = df[["text", "sentiment"]].dropna()
    df["label"] = df["sentiment"].map(LABEL2ID)

    # Spec requirement: 80 / 10 / 10 split, test set never touched
    # during training or hyperparameter selection.
    train_df, temp_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df["label"])
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df["label"])
    return train_df, val_df, test_df


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    acc = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="macro", zero_division=0)
    return {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="dataset_sample.csv")
    parser.add_argument("--output", default="../models/sentiment/wangchanberta_sentiment")
    parser.add_argument("--epochs", type=int, default=5)
    args = parser.parse_args()

    train_df, val_df, test_df = load_dataset(args.data)
    test_df.to_csv("sentiment_test_holdout.csv", index=False)  # kept aside, never trained on

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, padding="max_length", max_length=256)

    train_ds = Dataset.from_pandas(train_df[["text", "label"]]).map(tokenize, batched=True)
    val_ds = Dataset.from_pandas(val_df[["text", "label"]]).map(tokenize, batched=True)

    model = AutoModelForSequenceClassification.from_pretrained(BASE_MODEL, num_labels=len(LABELS))

    training_args = TrainingArguments(
        output_dir="./checkpoints_sentiment",
        num_train_epochs=args.epochs,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_steps=10,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
        callbacks=[EpochProgressCallback(), ProgressFileCallback("sentiment")],
    )

    trainer.train()
    trainer.save_model(args.output)
    tokenizer.save_pretrained(args.output)
    print(f"Saved fine-tuned sentiment model to {args.output}")
    print("Run evaluate.py against sentiment_test_holdout.csv for the final report.")


if __name__ == "__main__":
    main()
