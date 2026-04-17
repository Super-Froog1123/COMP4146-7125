from Modules.rag_3.rag_retriever import init_rag, retrieve_context
from Modules.rag_3.prompt_builder import build_user_prompt, build_full_prompt_list

class PromptBuilder:
    
    def __init__(self):
        init_rag()

    def get_full_prompt_list(
        question: str,
        context: list = [],
        system_prompt: str = "",
        is_search = False,
        use_embedding_retrieval = False,
        think_mode = False,
        is_study_plan = False
    ) -> list:
        # RAG
        retrieved_context = ''
        if is_search:
            if not use_embedding_retrieval:
                retrieved_context, _, _ = retrieve_context(question, top_k=3)
            else:
                retrieved_context = ''

        # prompt builder
        user_prompt = build_user_prompt(
            user_query=question,
            retrieved_context=retrieved_context,
            search_mode=is_search,
            think_mode=think_mode,
        )

        return build_full_prompt_list(
            system_prompt=system_prompt,
            history=context,
            user_prompt=user_prompt
        )
    