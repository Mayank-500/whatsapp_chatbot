import os
from google import genai
from google.genai import types

def run_gemini(user_message, product_data, combo_data):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    model = "gemini-2.5-pro"

    product_blocks = "\n".join([
        f"🧴 *{title}*\n🔗 {url}"
        for title, url in product_data.items() if title.lower() in user_message
    ])

    combo_blocks = "\n".join([
        f"🎁 *{title}*\n🔗 {url}"
        for title, url in combo_data.items() if title.lower() in user_message
    ])

    contents = [
        types.Content(role="user", parts=[types.Part.from_text(user_message)])
    ]

    response = client.models.generate_content(
        model=model,
        contents=contents,
        generation_config=types.GenerationConfig(temperature=0.8)
    )
    final_text = response.candidates[0].content.parts[0].text

    if product_blocks:
        final_text += "\n\n⭐ Recommended TACX Product:\n" + product_blocks
    if combo_blocks:
        final_text += "\n\n🎁 Combo Offer:\n" + combo_blocks

    return final_text
