import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

# Load API KEY
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# -------------------------
# Load Training Data (JSON)
# -------------------------
def load_store_data():
    with open("../bookstore_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

DATA = load_store_data()

BOOKS = DATA["books"]
CATEGORIES = DATA["categories"]
FAQS = DATA["faqs"]
STORE_INFO = DATA["store_info"]
POLICIES = DATA["policies"]

# -------------------------
# Rule-Based Retrieval
# -------------------------
def retrieve(query):
    query_lower = query.lower()
    results = {}

    # 1. Search books
    matched_books = []
    for book in BOOKS:
        if (query_lower in book["title"].lower() or
            query_lower in book["author"].lower() or
            query_lower in book["category"].lower() or
            query_lower in book["description"].lower()):
            matched_books.append(book)

    if matched_books:
        results["books"] = matched_books

    # 2. Store info
    if any(k in query_lower for k in ["store", "location", "contact", "working hours", "timing"]):
        results["store_info"] = STORE_INFO

    # 3. Category search
    for cat in CATEGORIES:
        if cat.lower() in query_lower:
            results["category_books"] = [b for b in BOOKS if b["category"] == cat]

    # 4. FAQs
    for faq in FAQS:
        if query_lower in faq["question"].lower():
            results["faq"] = faq

    # 5. Policies
    if "return" in query_lower:
        results["return_policy"] = POLICIES["return_policy"]
    if "payment" in query_lower or "pay" in query_lower:
        results["payment_methods"] = POLICIES["payment_methods"]

    return results


# -------------------------
# Gemini LLM
# -------------------------
model = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    system_instruction="""
    You are a trained assistant for Tamil Nadu Heritage Bookstore.

    You must answer ONLY from the data provided to you.
    NEVER use external knowledge.

    If the user asks anything unrelated to:
    - Books in the JSON
    - Store details
    - Policies
    - Categories
    - FAQs

    Respond with:
    "Sorry, I don’t know. This information is not available in my store data."

    Do NOT hallucinate. Do NOT guess.
    Keep answers friendly, polite, and short.
    """
)

print("📚 Tamil Nadu Heritage Bookstore Chatbot Ready!")
print("Type 'exit' to stop.\n")

# -------------------------
# Chat Loop
# -------------------------
while True:
    user_query = input("User: ")

    if user_query.lower() == "exit":
        print("Bot: Goodbye!")
        break

    # STEP 1: retrieve relevant JSON data
    result = retrieve(user_query)

    # If nothing matched → reject politely
    if not result:
        print("Bot: Sorry, I don’t know. This information is not available in my store data.")
        continue

    # STEP 2: Convert retrieval to clean json string
    context = json.dumps(result, indent=2, ensure_ascii=False)

    # STEP 3: Build LLM prompt
    prompt = f"""
    User Query: {user_query}

    Relevant Training Data:
    {context}

    Use ONLY this information to answer.
    If something cannot be answered using this data, respond:
    "Sorry, I don’t know. This information is not available in my store data."
    """

    # STEP 4: Gemini response
    response = model.generate_content(prompt)
    print("Bot:", response.text)
