"""Export a trained Transformers checkpoint to the server's exact ONNX path."""
from pathlib import Path
import shutil

from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer

CHECKPOINT = Path("models/checkpoint")
OUTPUT = Path("models")
TOKENIZER = OUTPUT / "tokenizer"

model = ORTModelForSequenceClassification.from_pretrained(CHECKPOINT, export=True)
model.save_pretrained(OUTPUT)
AutoTokenizer.from_pretrained(CHECKPOINT).save_pretrained(TOKENIZER)
source = OUTPUT / "model.onnx"
target = OUTPUT / "fallacy_classifier.onnx"
if source.exists():
    shutil.move(source, target)
print(f"Exported {target}")
