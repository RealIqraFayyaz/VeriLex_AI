from functools import lru_cache
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.core.config import settings
@lru_cache(maxsize=1)
def model():
    if not settings.enable_sentence_transformers: return None
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(settings.embedding_model)
    except Exception: return None
def compare(a,b):
    if not a.strip() or not b.strip(): return {"score":0.0,"method":"empty_input"}
    m=model()
    if m:
        v=m.encode([a,b],normalize_embeddings=True); score=float(v[0]@v[1]); method="sentence-transformers:"+settings.embedding_model
    else:
        v=TfidfVectorizer(ngram_range=(1,2),max_features=12000).fit_transform([a,b]); score=float(cosine_similarity(v[0:1],v[1:2])[0][0]); method="tfidf_fallback"
    return {"score":round(max(0,min(1,score)),4),"method":method}
def compare_chunks(a,b):
    found=[]
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            r=compare(x,y)
            if r["score"]>=.45: found.append({"source_chunk":i,"matched_chunk":j,**r,"source_excerpt":x[:400],"matched_excerpt":y[:400]})
    return sorted(found,key=lambda z:z["score"],reverse=True)[:25]
