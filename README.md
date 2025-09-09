# Baby Food Guide
A recipe book for babies up to 3 years old as part of LLM Zoomcamp project.

a young mom is very often owehwelmed which the amount of knowdelge and stuff she need to learn and adopt during first months with a baby. It is hard to keep everything in the head. To to save time and worries what what the baby can eat and what to cook today to keep the ration variaty wiede the repipe assistent was designed. He can answer all your question like - what to cook for a 10 months baby? what ellergies are in the cetrain dish? how long is the cooking time? can give suggestion with iron.rich food and so on. 

# Project Structure

baby_food_guide/           
├── app/                   
│   ├── app.py             # Flask entrypoint
│   ├── rag.py             # RAG pipeline
│   ├── get_data.py        # Data loading + Qdrant indexing
│   ├── config_loader.py   # Config loader
│   └── config.yaml        # Config file
├── data/                  
│   ├── answers_groq.csv
│   ├── baby_recipes_cleaned.csv
│   ├── baby_recipes.csv   
│   └── ground-truth-data.csv
├── docker/
│   ├── grafana/                 # Grafana dashboards
│   │   └── dashboards.json
│   └── postgres-init.sql        # DB init script
├── notebooks/ 
│   ├── evaluation_data_generation.ipynb    # generates ground_truth dataset 
│   ├── generator.py    # generates raw data (baby_recipes.csv)
│   ├── retrieval_evaluation.ipynb  # 1. Retrival evaluation with hit rate and MRR and 2. LLM evaluation with cosine similarity
│   └── vetor_search.ipynb  # RAG flow with Vector search (Qrandt)
├── docker-compose.yml
├── Dockerfile                   # For the Flask app
├── test.py                # Script to test the API
├── requirements.txt
└── venv/                  

# Technologies

* Groq as LLM
* Qdrant as vector search
* Flask as API
* Postgres as Database
* Grafana as monitoring tool
* Prometheus as metrics for monitoring

# Run the application

clone git repo and install dependencies

[add code snippets]
´´´bash
pip install -r reqirements.txt
´´´

### Run with docker-compose

Flow overview


´´´bash
#  1. Build and start all services
docker-compose --env-file .env up --build

# 2. Run DB init:
docker-compose exec app python -m app.db_prep

#  3. Access services
# Flask app: http://localhost:5000
# Qdrant dashboard: http://localhost:6333/dashboard
# Grafana: http://localhost:3000
# Postgres: localhost:5432

# 4. Test API
python test.py
´´´

Use APIs:
* /ask: Saves conversations to DB
* /feedback: Saves feedback to DB

Monitor in Grafana:
* Query Postgres directly for stats


Optional: run docker for elastic search (for evaluation part)
´´´bash
docker run -it \
    --rm \
    --name elasticsearch \
    -m 4GB \
    -p 9200:9200 \
    -p 9300:9300 \
    -e "discovery.type=single-node" \
    -e "xpack.security.enabled=false" \
    docker.elastic.co/elasticsearch/elasticsearch:8.4.3
´´´

### To run it locally and test an API

´´´bash
python app.py
´´´
in a seperate bash:
´´´bash
python test.py
´´´

You will get a respond similar to this one:

question:  How long can zucchini purée be stored in the fridge or freezer?
{'answer': 'Zucchini purée can be stored in the fridge for up to **2 days** or frozen for up to **1 month**.  \n\n**Recipe Summary:**  \n- **Ingredients:** Zucchini, water.  \n- **Method:** Steam/simmer zucchini until tender, blend with water or breastmilk/formula, and cool before storing.', 'conversation_id': '0f14d100-cad2-4d6b-821f-a730a9a2e59f', 'question': 'How long can zucchini purée be stored in the fridge or freezer?'}


# Evaluation

## Retrival evaluation

for the evaluation I compared 3 models - minsearch, vertor and elastic search with hit rate and MRR, the result was the following:
* Minsearch: Hit rate = 0.297, MRR = 0.185
* Elastic search: Hit rate = 0.293, MRR = 0.181 
* Vector search: Hit rate = 0.306, MRR = 0.178

So though the results are relatevely low, vector search has the best performance.

## LLM evaluation

the evaluation was done on the sample of 200 records from the ground_truch dataset. The cosine similarity mean = 0.556 and meadian = 0.554.


# Flask API

1. POST /ask

    * Input JSON: {"question": "What are iron-rich meals for 6-month-old?"}
    * Calls rag() from rag_fixed.py.
    * Returns:
        {
        "conversation_id": "uuid",
        "question": "...",
        "answer": "..."
        }

2. POST /feedback

    * Input JSON: {"conversation_id": "...", "feedback": +1}
    * Saves feedback to memory