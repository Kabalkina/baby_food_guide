from flask import Flask, request, jsonify, Response
import uuid, logging
from rag import rag
from db import save_conversation, save_feedback
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Prometheus metrics
REQUEST_COUNT = Counter("api_requests_total", "Total API requests", ["endpoint", "method", "status"])
REQUEST_LATENCY = Histogram("api_request_latency_seconds", "Request latency in seconds", ["endpoint"])
FEEDBACK_COUNT = Counter("feedback_total", "Feedback counts", ["feedback"])

@app.route('/metrics')
def metrics():
    """Expose Prometheus metrics."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/ask', methods=['POST'])
def ask():
    start = time.time()
    data = request.get_json()
    question = data.get('question')
    if not question:
        REQUEST_COUNT.labels("/ask", "POST", "400").inc()
        return jsonify({'error': 'Question is required'}), 400

    conversation_id = str(uuid.uuid4())
    try:
        answer = rag(question)
        save_conversation(conversation_id, question, answer)
        latency = time.time() - start
        REQUEST_COUNT.labels("/ask", "POST", "200").inc()
        REQUEST_LATENCY.labels("/ask").observe(latency)

        return jsonify({'conversation_id': conversation_id, 'question': question, 'answer': answer})
    except Exception as e:
        REQUEST_COUNT.labels("/ask", "POST", "500").inc()
        logging.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    start = time.time()
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    feedback_value = data.get('feedback')

    if feedback_value not in [+1, -1]:
        REQUEST_COUNT.labels("/feedback", "POST", "400").inc()
        return jsonify({'error': 'Feedback must be +1 or -1'}), 400

    try:
        save_feedback(conversation_id, feedback_value)
        FEEDBACK_COUNT.labels(str(feedback_value)).inc()
        latency = time.time() - start
        REQUEST_COUNT.labels("/feedback", "POST", "200").inc()
        REQUEST_LATENCY.labels("/feedback").observe(latency)

        return jsonify({'message': 'Feedback recorded'})
    except Exception as e:
        REQUEST_COUNT.labels("/feedback", "POST", "500").inc()
        logging.error(f"Error saving feedback: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
