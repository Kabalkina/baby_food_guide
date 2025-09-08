# Baby Food Guide
A recipe book for babies up to 3 years old as part of LLM Zoomcamp project.

a young mom is very often owehwelmed which the amount of knowdelge and stuff she need to learn and adopt during first months with a baby. It is hard to keep everything in the head. To to save time and worries what what the baby can eat and what to cook today to keep the ration variaty wiede the repipe assistent was designed. He can answer all your question like - what to cook for a 10 months baby? what ellergies are in the cetrain dish? how long is the cooking time? can give suggestion with iron.rich food and so on. 

# Project Structure

# Technologies

* Groq as LLM
* Qdrant for vector search

# Rerun

run docker for Qdrant

´´´bash
docker pull qdrant/qdrant

docker run -p 6333:6333 -p 6334:6334 \
   -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
   qdrant/qdrant
´´´

run docker for elastic search (for evaluation part)
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


# Evaluation

## Retrival evaluation

for the evaluation I compared 3 models - minsearch, vertor and elastic search with hit rate and MRR, the result was the following:
* Minsearch: Hit rate = 0.297, MRR = 0.185
* Elastic search: Hit rate = 0.293, MRR = 0.181 
* Vector search: Hit rate = 0.306, MRR = 0.178

So though the results are relatevely low, vector search has the best performance.

## LLM evaluation

the evaluation was done on the sample of 200 records from the ground_truch dataset. The cosine similarity mean = 0.556 and meadian = 0.554.