from textwrap import dedent

def get_response_format_instructions(
    is_search: bool = False,  # search mode
    require_citations: bool = True,    # 是否要求引用上下文片段
    is_study_plan: bool = False # study plan spawner
) -> str:
    """
    仅生成响应格式控制部分的提示词
    返回值可直接拼接到你的RAG上下文+用户问题之后
    """
    
    if is_search:
        # study mode
        return dedent("""
        Return exactly one line in this format, no extra content:
        ANSWER: <search result from context>
        """).strip()
    
    # 完整模式基础结构
    format_parts = []
    
    # 基础回答结构
    base_format = dedent("""
    Structure your answer clearly:
    1. Direct answer to the question
    """)
    format_parts.append(base_format)
    
    # 引用要求（可选）
    if require_citations:
        citation_format = dedent("""
        2. Supporting evidence: exact snippet from the provided context, enclosed in double quotes
        """)
        format_parts.append(citation_format)
    
    # 额外信息部分
    format_parts.append("3. Additional relevant information (if any)")
    
    # study mode spawner
    if is_study_plan:
        study_plan_format = dedent("""
        
        For study plan requests specifically:
        - Break down tasks by day/week based on user's time constraints
        - Assign priority levels (High/Medium/Low)
        - Include realistic time estimates for each task
        - Add review sessions if applicable
        """)
        format_parts.append(study_plan_format)
    
    # 拼接所有格式要求
    return "\n".join(part.strip() for part in format_parts)


# --------------------------
# 使用示例（你只需要这样调用）
# --------------------------
if __name__ == "__main__":
    # 场景1：普通问答，需要引用
    print("=== 场景1：普通问答 ===")
    format1 = get_response_format_instructions()
    print(format1)
    print("\n" + "-"*50 + "\n")
    
    # 场景2：严格搜索模式（单行输出）
    print("=== 场景2：严格搜索模式 ===")
    format2 = get_response_format_instructions(is_search=True)
    print(format2)
    print("\n" + "-"*50 + "\n")
    
    # 场景3：学习计划生成
    print("=== 场景3：学习计划生成 ===")
    format3 = get_response_format_instructions(is_study_plan=True)
    print(format3)
