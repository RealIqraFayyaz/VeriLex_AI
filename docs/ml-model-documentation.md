# ML model documentation
Semantic model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, lazy-loaded. If disabled/unavailable, TF-IDF cosine similarity is used and identified as fallback.

Cross-lingual: shared embedding space is a candidate approach, not a guarantee. Evaluate Urdu, Pashto, Punjabi, Balochi, Saraiki, Arabic and each language pair with labelled copied/translated/paraphrased/unrelated examples. Mark unsupported pairs experimental.

Code: Python AST node-type sequence plus token comparison; other languages currently token-only. Uploaded code is never executed.

AI-writing: descriptive lexical diversity, entropy, sentence length and repetition only. No AI probability or authorship verdict is generated. A classifier requires a licensed dataset, leakage-resistant split, calibration and independent evaluation.

Record dataset/license, preprocessing, split, model version, precision, recall, F1, ROC-AUC, retrieval Precision@K/Recall@K/MRR/nDCG and per-language results. Never invent accuracy.
