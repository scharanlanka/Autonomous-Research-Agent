from ara.azure_llm import AzureChatLLM

SYSTEM = """You are CriticAgent.
Review the draft report for:
- Missing citations where factual claims are made
- Over-claiming beyond provided sources
- Poor structure or unclear key findings
- Vague wording that can be made more specific
Return:
1) A brief critique (bullets)
2) A revised improved report in Markdown

Requirements for the revised report:
- Keep the same citation markers [n] and add missing citations where needed.
- Preserve a clear sectioned structure with headings.
- Prefer concrete wording (dates, numbers, source-attributed claims) over generic statements.

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
        max_tokens=2200,
        continue_on_length=True,
        max_continuations=2,
    )
