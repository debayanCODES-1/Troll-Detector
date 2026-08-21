"""Fine-tune DistilBERT and export the best checkpoint to ONNX."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from datasets import load_dataset
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support, precision_recall_curve
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments


def metrics(eval_prediction):
    logits, labels = eval_prediction
    predictions = np.argmax(logits, axis=-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average="binary", zero_division=0)
    print("confusion_matrix=", confusion_matrix(labels, predictions).tolist())
    return {"accuracy": accuracy_score(labels, predictions), "precision": precision, "recall": recall, "f1": f1}


def select_threshold(logits, labels, minimum_precision: float = 0.9) -> float:
    probabilities = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
    positive_scores = (probabilities / probabilities.sum(axis=-1, keepdims=True))[:, 1]
    precision, recall, thresholds = precision_recall_curve(labels, positive_scores)
    f1 = 2 * precision[:-1] * recall[:-1] / np.maximum(precision[:-1] + recall[:-1], 1e-12)
    eligible = np.where(precision[:-1] >= minimum_precision)[0]
    candidates = eligible if len(eligible) else np.arange(len(thresholds))
    return float(thresholds[candidates[np.argmax(f1[candidates])]])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="distilbert-base-uncased")
    parser.add_argument("--data-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--output-dir", type=Path, default=Path("models/checkpoint"))
    args = parser.parse_args()
    dataset = load_dataset("csv", data_files={name: str(args.data_dir / f"{name}.csv") for name in ("train", "val", "test")})
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    encoded = dataset.map(lambda batch: tokenizer(batch["text"], truncation=True, padding="max_length", max_length=128), batched=True)
    encoded = encoded.rename_column("label", "labels")
    encoded.set_format("torch", columns=["input_ids", "attention_mask", "labels"])
    model = AutoModelForSequenceClassification.from_pretrained(args.model, num_labels=2)
    training = TrainingArguments(output_dir=str(args.output_dir), eval_strategy="epoch", save_strategy="epoch", load_best_model_at_end=True, metric_for_best_model="f1", greater_is_better=True, logging_strategy="epoch", report_to=[])
    trainer = Trainer(model=model, args=training, train_dataset=encoded["train"], eval_dataset=encoded["val"], compute_metrics=metrics, tokenizer=tokenizer)
    trainer.train()
    validation = trainer.predict(encoded["val"])
    threshold = select_threshold(validation.predictions, np.asarray(encoded["val"]["labels"]))
    final = trainer.evaluate(encoded["test"])
    labels = np.asarray(encoded["test"]["labels"])
    predictions = np.argmax(trainer.predict(encoded["test"]).predictions, axis=-1)
    report = {"metrics": {key: float(value) for key, value in final.items() if key.startswith("eval_")}, "confusion_matrix": confusion_matrix(labels, predictions).tolist(), "selected_positive_threshold": threshold, "threshold_note": "Selected on validation data with a 0.90 minimum positive precision target."}
    Path("models").mkdir(exist_ok=True)
    Path("models/eval_report.md").write_text("# Evaluation\\n\\n```json\\n" + json.dumps(report, indent=2) + "\\n```\\n", encoding="utf-8")
    Path("models/threshold.json").write_text(json.dumps({"positive_threshold": threshold}, indent=2) + "\\n", encoding="utf-8")
    export_dir = Path("models/tokenizer")
    export_dir.mkdir(parents=True, exist_ok=True)
    tokenizer.save_pretrained(export_dir)
    trainer.save_model(args.output_dir)
    print("Training complete. Export the checkpoint with: optimum-cli export onnx --model", args.output_dir, "models")


if __name__ == "__main__":
    main()
