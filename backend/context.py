def assemble_context(
    retrieved_chunks: list[dict],
    max_chars: int = 3500
) -> str:
   # Returns:single context string
   
    context_parts = []
    seen = set()
    current_length = 0

    # sort highest relevance first 
    retrieved_chunks = sorted(
        retrieved_chunks,
        key=lambda x: x.get("score", 0),
        reverse=True
    )

    for chunk in retrieved_chunks:
        text = chunk.get("text", "").strip()

        if not text:
            continue

        # avoid duplicates
        if text in seen:
            continue

        # stop if context too long
        if current_length + len(text) > max_chars:
            break

        context_parts.append(text)
        seen.add(text)
        current_length += len(text)

    return "\n\n".join(context_parts)
