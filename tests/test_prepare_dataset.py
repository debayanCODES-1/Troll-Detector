from data.prepare_dataset import prepare


def test_prepare_deduplicates_and_splits():
    rows = [
        {"text": "I disagree with the evidence", "label": 0, "source": "cmv"},
        {"text": "I disagree with the evidence", "label": 0, "source": "other"},
        {"text": "You are an idiot", "label": 1, "source": "jigsaw"},
        {"text": "That argument is stupid", "label": 1, "source": "logic"},
    ]
    splits = prepare(rows)
    flattened = [row["text"] for split in splits.values() for row in split]
    assert len(flattened) == 2
    assert len(set(flattened)) == 2
    assert {row["label"] for split in splits.values() for row in split} == {0, 1}
    assert sum(row["label"] == 0 for split in splits.values() for row in split) == 1
    assert sum(row["label"] == 1 for split in splits.values() for row in split) == 1
