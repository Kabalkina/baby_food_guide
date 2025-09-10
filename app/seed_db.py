import uuid
import random
from datetime import datetime, timedelta, timezone

from app.db import save_conversation, save_feedback

# Dummy questions and answers
QUESTIONS = [
    "Is this recipe good for iron intake?",
    "Can I give this to my 6-month-old?",
    "How much protein does it contain?",
    "Does this contain common allergens?",
    "Is this recipe vegan-friendly?",
    "Can I prepare it in under 15 minutes?",
    "Is this suitable for 12-18 months?",
    "What texture should I aim for?",
    "Is this calorie-dense enough for toddlers?",
    "Does it support brain development?"
]

ANSWERS = [
    "Yes, this recipe is rich in iron from spinach.",
    "It’s suitable but introduce gradually at 6 months.",
    "Contains around 8g of protein per portion.",
    "Yes, it contains milk, which is a common allergen.",
    "Yes, the recipe is fully plant-based.",
    "Preparation takes around 10 minutes.",
    "Yes, works well for 12-18 months.",
    "Aim for mashed texture, not fully pureed.",
    "Each portion provides ~150 kcal.",
    "Rich in omega-3, good for brain development."
]

def seed_database():
    now = datetime.now(timezone.utc)

    for i in range(10):
        conv_id = str(uuid.uuid4())
        question = QUESTIONS[i]
        answer = ANSWERS[i]

        # Fake answer metadata
        answer_data = {
            "answer": answer,
            "model_used": "qwen/qwen3-32b",
            "response_time": round(random.uniform(0.2, 1.0), 2),
            "relevance": random.choice(["high", "medium", "low"]),
            "relevance_explanation": "Dummy explanation for demo",
            "prompt_tokens": random.randint(50, 200),
            "completion_tokens": random.randint(20, 100),
            "total_tokens": random.randint(70, 300),
            "eval_prompt_tokens": random.randint(50, 200),
            "eval_completion_tokens": random.randint(20, 100),
            "eval_total_tokens": random.randint(70, 300),
            "openai_cost": round(random.uniform(0.001, 0.02), 4),
        }

        timestamp = now - timedelta(minutes=(10 - i) * 5)

        # Save conversation
        save_conversation(conv_id, question, answer_data, timestamp=timestamp)

        # Random feedback (±1)
        if random.random() > 0.3:  # ~70% of rows get feedback
            feedback_value = random.choice([1, -1])
            save_feedback(conv_id, feedback_value, timestamp=timestamp)

    print("✅ Seeded database with 10 dummy conversations and feedback.")

if __name__ == "__main__":
    seed_database()
