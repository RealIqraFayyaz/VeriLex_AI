import ast,io,tokenize,re
from difflib import SequenceMatcher
def tokens(src,lang):
    if lang=="py":
        try: return [t.string for t in tokenize.generate_tokens(io.StringIO(src).readline) if t.type not in (tokenize.COMMENT,tokenize.NL,tokenize.NEWLINE,tokenize.INDENT,tokenize.DEDENT,tokenize.ENDMARKER)]
        except Exception: pass
    src=re.sub(r"//.*?$|/\*.*?\*/|#.*?$"," ",src,flags=re.M|re.S)
    return re.findall(r"[A-Za-z_$][\w$]*|\d+|==|!=|<=|>=|&&|\|\||[^\s]",src)
def ast_nodes(src):
    try: return [type(n).__name__ for n in ast.walk(ast.parse(src))]
    except SyntaxError: return []
def compare_code(a,b,lang):
    ta,tb=tokens(a,lang),tokens(b,lang)
    ts=SequenceMatcher(None,ta,tb,autojunk=False).ratio() if ta or tb else 0
    asts=None
    if lang=="py":
        na,nb=ast_nodes(a),ast_nodes(b); asts=SequenceMatcher(None,na,nb,autojunk=False).ratio() if na or nb else 0
    vals=[ts]+([asts] if asts is not None else [])
    return {"language":lang,"token_similarity":round(ts,4),"ast_similarity":round(asts,4) if asts is not None else None,"final_score":round(sum(vals)/len(vals),4),"method":"Python AST node sequence + token comparison" if lang=="py" else "Lexical token comparison only","execution":"Uploaded source code was not executed."}
