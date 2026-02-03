def refine_prompt(prompt, bot):
    """Use the local LLM to clarify or rephrase the prompt for accuracy."""
    clarification = (
        f"You are an expert AI assistant. The user said: '{prompt}'.\n"
        "Restate the user's intent as a clear, actionable instruction for an AI agent. "
        "Never assume or fabricate information. If details are missing, investigate and gather all available system information, use sudo and any available tools or permissions. "
        "If the prompt is ambiguous, ask clarifying questions or attempt to discover missing info. If it is complex, break it into steps. "
        "If it is clear, rephrase it for precision."
    )
    refined = bot.force_uncensor(clarification)
    return refined.strip()