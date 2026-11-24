from app.services.extraction import chunks,language
from app.ml.semantic import compare_chunks
from app.ml.code_similarity import compare_code
from app.ml.ai_signals import analyze
from app.agents.workflow import AnalysisOrchestratorAgent,DocumentIntelligenceAgent,MultilingualAnalysisAgent,ReportGenerationAgent
def run(text,filename,kind,corpus):
    ext=filename.rsplit(".",1)[-1].lower() if "." in filename else ""
    lang=language(text); plan=AnalysisOrchestratorAgent().plan(ext,kind)
    result={"analysis_plan":plan,"detected_language":lang,"analysis_type":kind,"interpretation":"Similarity is evidence for human review, not a misconduct verdict.","document_intelligence":DocumentIntelligenceAgent().validate(text)}
    if ext in {"py","java","js","jsx","ts","tsx","c","cpp","h","hpp","php"} or kind=="code":
        matches=[]
        for item in corpus:
            other_ext=item["filename"].rsplit(".",1)[-1].lower()
            if other_ext==ext and item["text"]: matches.append({"filename":item["filename"],**compare_code(text,item["text"],"py" if ext=="py" else ext)})
        result["code"]={"comparisons":sorted(matches,key=lambda x:x["final_score"],reverse=True)[:20]}
    else:
        cs=chunks(text); matches=[]
        for item in corpus:
            if item["text"]: matches.extend([{"source_filename":item["filename"],**m} for m in compare_chunks(cs,chunks(item["text"]))])
        matches.sort(key=lambda x:x["score"],reverse=True)
        result["semantic"]={"chunks_analyzed":len(cs),"matches":matches[:25],"top_similarity":matches[0]["score"] if matches else 0,"language_evaluation":MultilingualAnalysisAgent().metadata(lang)}
        result["ai_content"]=analyze(text) if kind in {"complete","ai_content"} else None
    result["report_validation"]=ReportGenerationAgent().validate({"method":"analysis_pipeline","matches":result.get("semantic",{}).get("matches",[])})
    return result
