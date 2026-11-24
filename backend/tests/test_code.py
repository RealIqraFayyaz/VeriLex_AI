from app.ml.code_similarity import compare_code
def test_ast_and_tokens():
    a="def add(x,y):\n return x+y"
    b="def sum_values(first,second):\n return first+second"
    r=compare_code(a,b,"py")
    assert r["ast_similarity"]>.7
    assert 0<=r["final_score"]<=1
