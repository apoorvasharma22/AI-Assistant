import os

def generate_answer(message, history, matches):
    if not matches:
        return (
            "I don't know based on the available company documentation. "
            "Please contact a support representative for further assistance.",
            [],
            True,
        )

    context = "\n\n".join(
        f"Source: {item['source']}\nContent: {item['text']}" for item in matches
    )
    sources = list(dict.fromkeys(item["source"] for item in matches))
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return fallback_answer(message, matches), sources, False

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        recent_history = history[-8:]
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an intelligent customer support assistant. "
                    "Answer only from the supplied company documentation. "
                    "If the documentation does not contain enough information, "
                    "say exactly: I don't know based on the available company documentation. "
                    "Keep answers concise, clear and helpful. Never invent company policies."
                ),
            }
        ]
        messages.extend(recent_history)
        messages.append(
            {
                "role": "user",
                "content": f"Company documentation:\n{context}\n\nCustomer question: {message}",
            }
        )
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            temperature=0.2,
        )
        answer = response.choices[0].message.content.strip()
        if answer.lower().startswith("i don't know"):
            return answer, sources, True
        return answer, sources, False
    except Exception:
        return fallback_answer(message, matches), sources, False

def fallback_answer(message, matches):
    best = matches[0]["text"].strip()
    if len(best) > 650:
        best = best[:650].rsplit(" ", 1)[0] + "..."
    return f"According to the company documentation: {best}"
