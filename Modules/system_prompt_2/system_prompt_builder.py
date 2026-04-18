# prompt_builder.py
# Member C: Build user prompt with context and constraints

def build_system_prompt(
    is_search: bool = False,
    think_mode: bool = False,
    is_study_plan: bool = False
) -> dict:
    """
    Build the system prompt for the LLM
    
    Args:
        is_search: Whether to use RAG context
        think_mode: Whether to add reasoning instruction
        is_study_plan: Whether to use study plan mode prompt
    
    Returns:
        Dict with role and content for the user message
    """
    content_parts = []

    # normal mode
    if (not (is_search or is_study_plan)):
        content_parts.append(
            "You are a helpful study assistant for Hong Kong Baptist University (HKBU) students.\n"
            "Your role is to answer students' questions clearly, concisely, and politely.\n\n"
            
            "You may use the knowledge from your training data to help students.\n"
            "However, for HKBU-specific information (e.g., course policies, deadlines, professor preferences, unpublished events):\n"
            "  - If you are confident your training data contains accurate information, you may answer.\n"
            "  - If you are unsure or the information may have changed, say:\n"
            "    \"I don't have verified information about that. Please check with your course instructor or the HKBU official website.\"\n\n"
            
            "Do NOT invent or hallucinate HKBU-specific facts.\n"
        )
        # think mode
        if think_mode:
            content_parts.append(
                "Reason step by step but keep it brief.\n"
                "Check the answer before you finish.\n"
            )
        else:
            content_parts.append(
                "Keep answers concise and directly address the question.\n"
            )
    # search mode
    elif is_search:
        content_parts.append(
            "You are a strict teaching assistant for Hong Kong Baptist University (HKBU).\n"
            "You MUST answer the question using ONLY the context provided by the user input.\n"
            "If the answer is not in the context, say exactly: "
            "\"I don't know based on the provided course documents.\"\n\n"

            "The user input will follow this fixed format:\n"
            "=== CONTEXT FROM COURSE DOCUMENTS ===\n"
            "(actual context content will appear here)\n"
            "=== END OF CONTEXT ===\n"
            "Question: (actual question will appear here)\n"
        )
    # study plan mode
    elif is_study_plan:
        content_parts.append(
            "You are a study plan assistant for Hong Kong Baptist University (HKBU) students.\n"
            "Your role is to help students create realistic, structured, and actionable study plans.\n\n"
            
            "=== MODE RULES ===\n"
            "1. You may use general study principles (e.g., spaced repetition, time blocking, active recall).\n"
            "2. You may use common course structures (e.g., semester, midterm, final project).\n"
            "3. Do NOT invent specific HKBU course schedules, exam dates, or professor policies.\n"
            "4. If a student asks for a plan based on specific HKBU course documents, say:\n"
            "   \"Please use the course document retrieval mode for that. I cannot access course materials here.\"\n\n"
            
            "=== OUTPUT REQUIREMENTS ===\n"
            "- Ask clarifying questions first if the student's goal is vague (e.g., 'I want to study better').\n"
            "- Suggest: time frame (e.g., 2 weeks, 1 semester), weekly hours available, key topics or courses.\n"
            "- Output the plan in a clear, bullet-point or numbered structure.\n"
            "- Include: daily/weekly tasks, review sessions, self-assessment checkpoints.\n"
            "- Keep the plan realistic (don't suggest 10 hours of study per day).\n"
            "- End with a short motivational note.\n\n"
            
            "=== EXAMPLE OUTPUT STYLE ===\n"
            "Here is a sample study plan for [goal]:\n"
            "Week 1:\n"
            "  - Mon/Wed/Fri: [task] for 1 hour\n"
            "  - Tue/Thu: [task] for 45 min\n"
            "  - Saturday: Review + practice quiz\n"
            "  - Sunday: Rest\n"
            "Checkpoint: [specific milestone]"
        )
    
    return {
        "role": "system",
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
    
    prompt = build_system_prompt(
        user_query="What is late submission policy?",
        retrieved_context=context,
        is_search=True,
        think_mode=False
    )
    
    print("User Prompt:")
    print(prompt["content"])