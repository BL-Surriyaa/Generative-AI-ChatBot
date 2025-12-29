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

    # 1. --- BOOK SEARCH USING KEYWORDS ---
    matched_books = []
    for book in BOOKS:
        if (any(word in book["title"].lower() for word in query_lower.split()) or
            any(word in book["author"].lower() for word in query_lower.split()) or
            book["category"].lower() in query_lower or
            book["description"].lower() in query_lower):
            matched_books.append(book)

    if matched_books:
        results["books"] = matched_books

    # 2. --- LIST ALL BOOKS ---
    if "list" in query_lower and "book" in query_lower:
        results["all_books"] = BOOKS

    # 3. --- LIST ALL AUTHORS ---
    if ("author" in query_lower and "list" in query_lower) or "authors" in query_lower:
        results["authors"] = list({book["author"] for book in BOOKS})

    # 4. --- LIST ALL PRICES ---
    if "price" in query_lower and ("all" in query_lower or "books" in query_lower):
        results["prices"] = [{"title": b["title"], "price": b["price"]} for b in BOOKS]

    # 5. --- CHEAPEST BOOK ---
    if "cheapest" in query_lower or "lowest price" in query_lower:
        cheapest = min(BOOKS, key=lambda x: x["price"])
        results["cheapest_book"] = cheapest

    # 6. --- BOOKS BY PRICE MATCH ---
    import re
    price_match = re.findall(r'\b\d+\b', query_lower)
    if price_match:
        price_value = int(price_match[0])
        results["books_by_price"] = [b for b in BOOKS if b["price"] == price_value]

    # 7. --- STORE NAME / SHOP NAME ---
    if any(k in query_lower for k in ["shop name", "store name", "bookstore name", "name of bookstore"]):
        results["store_name"] = STORE_INFO["name"]

    # 8. --- STORE LOCATION ---
    if any(k in query_lower for k in ["location", "where is", "where it is"]):
        results["store_location"] = STORE_INFO["location"]

    # 9. --- CONTACT INFO ---
    if "contact" in query_lower or "phone" in query_lower or "email" in query_lower:
        results["contact"] = STORE_INFO["contact"]

    # 10. --- WORKING HOURS ---
    if "time" in query_lower or "working hours" in query_lower or "open" in query_lower:
        results["working_hours"] = STORE_INFO["working_hours"]

    # 11. --- FAQ MATCH ---
    for faq in FAQS:
        if any(word in faq["question"].lower() for word in query_lower.split()):
            results["faq"] = faq

    # 12. --- RETURN POLICY ---
    if "return" in query_lower:
        results["return_policy"] = POLICIES["return_policy"]

    # 13. --- PAYMENT METHODS ---
    if "payment" in query_lower or "pay" in query_lower:
        results["payment_methods"] = POLICIES["payment_methods"]

    return results



# -------------------------
# Gemini LLM
# -------------------------
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
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
print("MODEL USED:", model.model_name)

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
