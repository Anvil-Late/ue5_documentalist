import qdrant_client as qc
import qdrant_client.http.models as qmodels
import uuid
import json
import argparse
from tqdm import tqdm

client = qc.QdrantClient(url="localhost")
METRIC = qmodels.Distance.DOT
DIMENSION = 1536
COLLECTION_NAME = "ue5_docs"

def create_index():
    client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config = qmodels.VectorParams(
            size=DIMENSION,
            distance=METRIC,
        )
    )


def create_subsection_vector(
    subsection_content,
    section_anchor,
    page_url
    ):

    id = str(uuid.uuid1().int)[:32]
    payload = {
        "text": subsection_content,
        "url": page_url,
        "section_anchor": section_anchor,
        "block_type": 'text'
    }
    return id, payload


def add_doc_to_index(embeddings, content_dict):
    ids = []
    vectors = []
    payloads = []
    
    for url, content in tqdm(embeddings.items()):
        print(f"Processing url {url}")
        section_anchor = content['title']
        section_vector = content['embedding']
        section_content = content_dict[url]['content']
        id, payload = create_subsection_vector(
            section_content,
            section_anchor,
            url
    )
        ids.append(id)
        vectors.append(section_vector)
        payloads.append(payload)
    
    ## Add vectors to collection
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=qmodels.Batch(
            ids = ids,
            vectors=vectors,
            payloads=payloads
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--embeddings_path', type=str, default='./embeddings/embeddings.json')
    parser.add_argument('--content_path', type=str, default='./documents/subsections.json')
    args = parser.parse_args()
    
    with open(args.embeddings_path, 'r') as f:
        embeddings = json.load(f)
    with open(args.content_path, 'r') as f:
        content_dict = json.load(f)
    
    create_index()
    add_doc_to_index(embeddings, content_dict)