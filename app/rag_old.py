import re
import json
import pandas as pd
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

import get_data

from config_loader import MODEL, COLLECTION_NAME, GROQ_CLIENT, GROQ_MODEL


documents = get_data.load_data()
qd_client = get_data.create_collection_and_upsert(documents)
ground_truth = get_data.get_ground_truth()

#model_name = 'multi-qa-MiniLM-L6-cos-v1'
#model = SentenceTransformer(model_name)

def vector_search(question):

    
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

    for hit in search_results:
        doc = hit if isinstance(hit, dict) else getattr(hit, "payload", {}) or {}
        safe_doc = {k: doc.get(k, "N/A") for k in [
            "dish_name", "baby_age", "iron_rich", "allergen", "ingredients",
            "cooking_time", "texture", "meal_type", "calories", "preparation_difficulty", "recipe"
        ]}
    context += entry_template.format(**safe_doc) + "\n\n"

    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt


def llm(prompt):
    response = GROQ_CLIENT.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    final_answer = response.choices[0].message.content

    return re.sub(r"<think>.*?</think>\s*", "", final_answer, flags=re.DOTALL).strip()



def hit_rate(relevance_total):
    cnt = 0

    for line in relevance_total:
        if True in line:
            cnt = cnt + 1

    return cnt / len(relevance_total)

def mrr(relevance_total):
    total_score = 0.0

    for line in relevance_total:
        for rank in range(len(line)):
            if line[rank] == True:
                total_score = total_score + 1 / (rank + 1)

    return total_score / len(relevance_total)

def evaluate(ground_truth, search_function):
    relevance_total = []

    for q in ground_truth:
        doc_id = q['id']
        results = search_function(q)
        relevance = [d['id'] == doc_id for d in results]
        relevance_total.append(relevance)

    return {
        'hit_rate': hit_rate(relevance_total),
        'mrr': mrr(relevance_total),
    }

def rag(query):
    search_results = vector_search(query)
    prompt = build_prompt(query, search_results)
    answer = llm(prompt)
    return answer



def cosine_similarity(ground_truth, documents):
    answers = {}
    doc_idx = {d['id']: d for d in documents}

    for i, rec in enumerate(ground_truth):
        if i in answers:
            continue

        answer_llm = rag(rec['question'])
        doc_id = rec['id']
        original_doc = doc_idx[doc_id]
        answer_orig = (original_doc['dish_name'] + ". " + original_doc['baby_age'] + "." + original_doc['iron_rich'] + 
                    original_doc['allergen'] + ". " + original_doc['ingredients'] + "." + original_doc['recipe'] +
                    original_doc['texture'] + ". " + original_doc['meal_type'] + ". " + original_doc['preparation_difficulty']).strip()

        answers[i] = {
            'answer_llm': answer_llm,
            'answer_orig': answer_orig,
            'document': doc_id,
            'question': rec['question']
        }

    df_groq = pd.DataFrame(answers).T
    answers_orig = df_groq['answer_orig'].astype(str).tolist()
    answers_llm = df_groq['answer_llm'].astype(str).tolist()

    v_orig = model.encode(answers_orig)
    v_llm = model.encode(answers_llm)

    similarity = (v_llm * v_orig).sum(axis=1)

    return similarity

