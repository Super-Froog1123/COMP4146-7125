# prompt_builder.py
# Member C: Build user prompt with context and constraints

def build_user_prompt(
    user_query: str, 
    retrieved_context: str, 
    search_mode: bool = True,
    think_mode: bool = False,
) -> dict:
    """
    Build the user prompt for the LLM
    
    Args:
        user_query: User's original question
        retrieved_context: Formatted context from RAG (with citations)
        search_mode: Whether to use RAG context
        think_mode: Whether to add reasoning instruction
        history: Previous conversation history (list of dicts)
    
    Returns:
        Dict with role and content for the user message
    """
    content_parts = []
    
    # 4.1 Preface (only for search mode)
    if search_mode:
        content_parts.append(
            "You are a strict teaching assistant for HKBU.\n"
            "Use ONLY the context below to answer the question.\n"
            "If the answer is not in the context, say: "
            "\"I don't know based on the provided course documents.\"\n"
        )
    
    # 4.2 Internal data (only for search mode)
    if search_mode and retrieved_context:
        content_parts.append(
            "=== CONTEXT FROM COURSE DOCUMENTS ===\n"
            f"{retrieved_context}\n"
            "=== END OF CONTEXT ===\n"
        )
    
    # 4.3 User input
    content_parts.append(f"Question: {user_query}\n")
    
    # 4.4 Think mode (conflicts with search mode per project spec)
    if think_mode and not search_mode:
        content_parts.append(
            "Reason step by step but keep it brief.\n"
            "Check the answer before you finish.\n"
        )
    
    # 4.5 Output format restriction (for search mode)
    if search_mode:
        content_parts.append(
            "Return exactly one line in this format:\n"
            "ANSWER: <your answer with citations>\n"
            "Example: ANSWER: According to Policy_for_Assessment.pdf page 3, ..."
        )
    
    return {
        "role": "user",
        "content": "\n".join(content_parts)
    }


def build_full_prompt_list(
    system_prompt: str,
    history: list,
    user_prompt: dict
) -> list:
    """
    Build the complete prompt list for Ollama
    
    Args:
        system_prompt: System role message (from Member B)
        history: Conversation history (from Member B)
        user_prompt: Current user prompt (from this file)
    
    Returns:
        List of messages for Ollama
    """
    return [
        {"role": "system", "content": system_prompt},
        *history,
        user_prompt
    ]


# Test code
if __name__ == "__main__":
    # Example usage
    context = "[1] Source: Policy.pdf, Page 3\nLate submission not allowed"
    
    prompt = build_user_prompt(
        user_query="What is late submission policy?",
        retrieved_context=context,
        search_mode=True,
        think_mode=False
    )
    
    print("User Prompt:")
    print(prompt["content"])