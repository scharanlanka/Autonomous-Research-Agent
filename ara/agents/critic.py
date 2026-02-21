from ara.azure_llm import AzureChatLLM

SYSTEM = """You are CriticAgent.
Review the draft report for:
- Missing citations where factual claims are made
- Over-claiming beyond provided sources
- Poor structure or unclear key findings
Return:
1) A brief critique (bullets)
2) A revised improved report in Markdown

Format:
## Critique
- ...
## Revised Report
...
"""

def run_critic(draft_report: str) -> str:
    llm = AzureChatLLM()
    return llm.chat(
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": draft_report},
        ],
        temperature=0.2,
        max_tokens=1700,
    )