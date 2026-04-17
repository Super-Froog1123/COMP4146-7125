def messages_to_prompt(messages: list[dict]) -> str:
    """
    Convert Olama Chat formatted messages to Generate API prompts
    """
    prompt_parts = []
    
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        
        if role == "system":
            prompt_parts.append(f"System: {content}")
        elif role == "user":
            prompt_parts.append(f"User: {content}")
        elif role == "assistant":
            prompt_parts.append(f"Assistant: {content}")
    
    prompt_parts.append("Assistant: ")
    
    return "\n".join(prompt_parts)