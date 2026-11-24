# Five controlled agents. They coordinate deterministic services; no unrestricted tools.
class AnalysisOrchestratorAgent:
    def plan(self,ext,kind):
        if ext in {"py","java","js","jsx","ts","tsx","c","cpp","php"} or kind=="code":
            return ["document_intelligence","code_analysis","report_generation"]
        return ["document_intelligence","multilingual_analysis"]+(["ai_content_signals"] if kind in {"complete","ai_content"} else [])+["report_generation"]
class DocumentIntelligenceAgent:
    def validate(self,text): return {"characters":len(text),"nonempty":bool(text.strip()),"ready":len(text.strip())>=10}
class MultilingualAnalysisAgent:
    def metadata(self,lang): return {"detected_language":lang,"evaluation_status":"experimental_or_unverified" if lang in {"ur","ps","pa","ar","unknown"} else "requires_dataset_validation"}
class CodeAnalysisAgent:
    def method(self): return "static_ast_and_token_analysis"
class ReportGenerationAgent:
    def validate(self,result): return {"method_present":bool(result.get("method")),"evidence_count":len(result.get("matches",[]))}
