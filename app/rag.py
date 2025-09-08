import re
from qdrant_client import QdrantClient, models

import get_data

from config_loader import MODEL, COLLECTION_NAME, GROQ_CLIENT


qd_client = get_data.QD_CLIENT

def vector_search(question):
    print('vector_search is used')
    
    query_points = qd_client.query_points(
        collection_name=COLLECTION_NAME,
        query=models.Document(
            text=question,
            model=MODEL
        ),
        limit=2,
        with_payload=True
    )
    
    results = []
    
    for point in query_points.points:
        results.append(point.payload)
    
    return results


prompt_template = """
You are a helpful AI food assistant. Answer the QUESTION using only the information in CONTEXT. 
If the answer is not in CONTEXT, say you don't know.

Provide concise, factual answers with a recipe per dish. If multiple dishes match, summarize clearly.

QUESTION: {question}

CONTEXT:
{context}
""".strip()

entry_template = """
'dish_name': '{dish_name}',
'baby_age' : {baby_age},
'iron_rich': {iron_rich},
'allergen': {allergen},
'ingredients': '{ingredients}',
'cooking_time': {cooking_time},
'texture': '{texture}',
'meal_type': '{meal_type}',
'calories': {calories},
'preparation_difficulty': '{preparation_difficulty}',
'recipe': '{recipe}'
""".strip()


def build_prompt(query, search_results):

    context = ""

    for doc in search_results:
        context = context + entry_template.format(**doc) + "\n\n"

    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt


def llm(prompt):
    response = GROQ_CLIENT.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    final_answer = response.choices[0].message.content

    return re.sub(r"<think>.*?</think>\s*", "", final_answer, flags=re.DOTALL).strip()




evaluation_prompt_template = """
You emulate a user who is searching for a recipe for a baby. 
Formulate 5 questions this user might ask based on a baby food recipe. The record
should contain the answer to the questions, and the questions should be complete and not too short.
Use as fewer words as possible from the record. 

The record:


'dish_name': '{dish_name}',
'baby_age' : {baby_age},
'iron_rich': {iron_rich},
'allergen': {allergen},
'ingredients': '{ingredients}',
'cooking_time': {cooking_time},
'texture': '{texture}',
'meal_type': '{meal_type}',
'calories': {calories},
'preparation_difficulty': '{preparation_difficulty}',
'recipe': '{recipe}'


Provide the output in parsable JSON without using code blocks:

["question1", "question2", ..., "question5"]
""".strip()

def evaluate_relevance(question, answer):
    prompt = evaluation_prompt_template.format(question=question, answer=answer)
    evaluation = llm(prompt)

    try:
        json_eval = json.loads(evaluation)
        return json_eval
    except json.JSONDecodeError:
        result = {"Relevance": "UNKNOWN", "Explanation": "Failed to parse evaluation"}
        return result

def rag(query):
    search_results = vector_search(query)
    prompt = build_prompt(query, search_results)
    answer = llm(prompt)
    return answer