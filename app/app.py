from flask import Flask, request, jsonify
import uuid
import logging
from rag import rag

# Setup Flask app
app = Flask(__name__)

# In-memory storage for conversation results and feedback 
conversations = {}
feedback_store = {}

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


@app.route('/ask', methods=['POST'])
def ask():
    """Handle user question, call RAG pipeline, and return response with a conversation ID."""
    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({'error': 'Question is required'}), 400

    logging.info(f"Received question: {question}")

    # Generate unique conversation ID
    conversation_id = str(uuid.uuid4())

    # Get answer from RAG pipeline
    try:
        answer = rag(question)
        conversations[conversation_id] = {
            'question': question,
            'answer': answer
        }
        logging.info(f"Answer generated for conversation {conversation_id}")
        return jsonify({
            'conversation_id': conversation_id,
            'question': question,
            'answer': answer
        })
    except Exception as e:
        logging.error(f"Error processing question: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/feedback', methods=['POST'])
def feedback():
    """Receive feedback (+1/-1) for a conversation ID."""
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    feedback = data.get('feedback')

    if conversation_id not in conversations:
        return jsonify({'error': 'Invalid conversation_id'}), 400

    if feedback not in [+1, -1]:
        return jsonify({'error': 'Feedback must be +1 or -1'}), 400

    feedback_store[conversation_id] = feedback
    logging.info(f"Feedback for conversation {conversation_id}: {feedback}")

    return jsonify({
        'message': 'Feedback recorded',
        'conversation_id': conversation_id,
        'feedback': feedback
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
