import pandas as pd
import os
from dotenv import load_dotenv

from qdrant_client import QdrantClient, models
#from fastembed import TextEmbedding


from .config_loader import DATA_PATH, GROUND_TRUTH_PATH, MODEL, COLLECTION_NAME, EMBEDDING_DIMENSIONALITY

TEXT_FIELDS = ["dish_name", "baby_age", "iron_rich", "allergen", "ingredients", "cooking_time","recipe", "texture", 
               "meal_type", "calories", "preparation_difficulty"]



def load_data(path=DATA_PATH):
    df = pd.read_csv(path, sep=';')

    documents = df.to_dict(orient='records')
    return documents


def create_collection_and_upsert(documents, model=MODEL, collection_name=COLLECTION_NAME):
    load_dotenv()
    #
    QD_CLIENT = QdrantClient("http://localhost:6333")
    QD_CLIENT.delete_collection(collection_name=collection_name)
    try:
        QD_CLIENT.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=EMBEDDING_DIMENSIONALITY,
                distance=models.Distance.COSINE
            )
        )
    except Exception as e:
        print(f"Collection {COLLECTION_NAME} already exists. {e}")

    QD_CLIENT.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="id",
        field_schema="keyword"
    )

    points = []

    for i, doc in enumerate(documents):
        text = ' '.join(str(doc.get(field, "")) for field in TEXT_FIELDS)

        vector = models.Document(text=text, model=model)
        point = models.PointStruct(
            id=i,
            vector=vector,
            payload=doc
        )
        points.append(point)

    QD_CLIENT.upsert(
        collection_name=collection_name,
        points=points
    )
    
    return QD_CLIENT
        

def get_ground_truth(path=GROUND_TRUTH_PATH):
    df = pd.read_csv(path, sep=',')
    ground_truth = df.to_dict(orient='records')
    return ground_truth
