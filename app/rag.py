import re
import json
import os
from groq import Groq
import logging
import pandas as pd
from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

from . import get_data
from .config_loader import MODEL, COLLECTION_NAME, GROQ_MODEL

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Load data and initialize Qdrant client
logging.info("Loading documents and ground truth...")
documents = get_data.load_data()
qd_client = get_data.create_collection_and_upsert(documents)
ground_truth = get_data.get_ground_truth()

# Initialize embedding model
logging.info(f"Loading embedding model: {MODEL}")
embedding_model = TextEmbedding(MODEL)
GROQ_CLIENT = Groq(api_key=os.getenv("GROQ_API_KEY"))


def vector_search(question, top_k=1):
    """Search Qdrant for top_k most relevant documents."""
    logging.info(f"Running vector search for query: {question}")

    query_vector = list(next(embedding_model.embed([question])))

    query_points = qd_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True
    )

    results = [p.payload for p in query_points.points if p.payload]
    logging.info(f"Found {len(results)} results.")
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
Dish: {dish_name}
Baby Age: {baby_age}
Iron Rich: {iron_rich}
Allergen: {allergen}
Ingredients: {ingredients}
Cooking Time: {cooking_time}
Texture: {texture}
Meal Type: {meal_type}
Calories: {calories}
Preparation Difficulty: {preparation_difficulty}
Recipe: {recipe}
""".strip()


def build_prompt(query, search_results):
    """Build a structured prompt for the LLM."""
    logging.info("Building prompt...")
    context = ""
    for hit in search_results:
        doc = hit if isinstance(hit, dict) else getattr(hit, "payload", {}) or {}
        safe_doc = {k: doc.get(k, "N/A") for k in [
            "dish_name", "baby_age", "iron_rich", "allergen", "ingredients",
            "cooking_time", "texture", "meal_type", "calories", "preparation_difficulty", "recipe"
        ]}
        context += entry_template.format(**safe_doc) + "\n\n"

    return prompt_template.format(question=query, context=context.strip())


def llm(prompt):
    """Call the Groq LLM for inference."""
    logging.info("Querying Groq LLM...")
    response = GROQ_CLIENT.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    final_answer = response.choices[0].message.content
    clean_answer = re.sub(r"<think>.*?</think>\s*", "", final_answer, flags=re.DOTALL).strip()
    return clean_answer


def hit_rate(relevance_total):
    """Calculate hit rate metric."""
    return sum(True in line for line in relevance_total) / len(relevance_total)


def mrr(relevance_total):
    """Calculate Mean Reciprocal Rank."""
    total_score = 0.0
    for line in relevance_total:
        for rank, rel in enumerate(line):
            if rel:
                total_score += 1 / (rank + 1)
                break
    return total_score / len(relevance_total)


def evaluate(ground_truth, search_function):
    """Evaluate search function performance."""
    logging.info("Evaluating search function...")
    relevance_total = []
    for q in ground_truth:
        doc_id = q.get('id')
        query = q.get('question', '')
        results = search_function(query)
        relevance = [d.get('id') == doc_id for d in results if d]
        relevance_total.append(relevance)

    return {
        'hit_rate': hit_rate(relevance_total),
        'mrr': mrr(relevance_total),
    }


def rag(query):
    """Run full RAG pipeline: search -> prompt -> LLM answer."""
    logging.info(f"Running RAG pipeline for query: {query}")
    search_results = vector_search(query)
    prompt = build_prompt(query, search_results)
    answer = llm(prompt)
    return answer


def cosine_similarity(ground_truth, documents):
    """Compare LLM answers and original answers using cosine similarity."""
    logging.info("Calculating cosine similarity...")
    answers = {}
    doc_idx = {d['id']: d for d in documents}

    for i, rec in enumerate(ground_truth):
        if i in answers:
            continue

        answer_llm = rag(rec.get('question', ''))
        doc_id = rec.get('id')
        original_doc = doc_idx.get(doc_id, {})
        answer_orig = (
            f"{original_doc.get('dish_name', '')}. "
            f"{original_doc.get('baby_age', '')}. "
            f"{original_doc.get('iron_rich', '')} "
            f"{original_doc.get('allergen', '')}. "
            f"{original_doc.get('ingredients', '')}. "
            f"{original_doc.get('recipe', '')} "
            f"{original_doc.get('texture', '')}. "
            f"{original_doc.get('meal_type', '')}. "
            f"{original_doc.get('preparation_difficulty', '')}"
        ).strip()

        answers[i] = {
            'answer_llm': answer_llm,
            'answer_orig': answer_orig,
            'document': doc_id,
            'question': rec.get('question', '')
        }

    df_groq = pd.DataFrame(answers).T
    answers_orig = df_groq['answer_orig'].astype(str).tolist()
    answers_llm = df_groq['answer_llm'].astype(str).tolist()

    v_orig = list(embedding_model.embed(answers_orig))
    v_llm = list(embedding_model.embed(answers_llm))

    import numpy as np
    v_orig = np.array(v_orig)
    v_llm = np.array(v_llm)

    norm_orig = v_orig / np.linalg.norm(v_orig, axis=1, keepdims=True)
    norm_llm = v_llm / np.linalg.norm(v_llm, axis=1, keepdims=True)
    similarity = (norm_llm * norm_orig).sum(axis=1)

    return similarity
