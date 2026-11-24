import re,math
from collections import Counter
def analyze(text):
    words=re.findall(r"\b[\w'-]+\b",text.lower()); sents=[s for s in re.split(r"[.!?؟۔]+",text) if s.strip()]
    if len(words)<80: return {"classification":"INSUFFICIENT_EVIDENCE","score":None,"warning":"At least 80 words required; this is not a validated AI authorship detector."}
    c=Counter(words); n=len(words); entropy=-sum((v/n)*math.log2(v/n) for v in c.values())
    return {"classification":"EXPLORATORY_SIGNALS_ONLY","score":None,"confidence":"not_calibrated","signals":{"lexical_diversity":round(len(c)/n,3),"word_entropy_bits":round(entropy,3),"average_sentence_words":round(sum(len(s.split()) for s in sents)/len(sents),2),"repetition_ratio":round(1-len(c)/n,3)},"warning":"Descriptive statistics cannot establish whether text was written by a human or AI."}
