import openai
import os
import qdrant_client as qc
import qdrant_client.http.models as models
from rich import print
import webbrowser

CLIENT = qc.QdrantClient(url="localhost")
METRIC = models.Distance.DOT
DIMENSION = 1536

with open('/Volumes/credentials/openai/api_key.txt', 'r') as protected_file:
    api_key = protected_file.read()
openai.api_key = api_key

model = "text-embedding-ada-002"

def embed_query(query):
    response = openai.Embedding.create(
                input=query,
                model=model
    )
    embedding = response['data'][0]['embedding']
    return embedding


def parse_block_types(block_types):
    if block_types is None:
        block_types = ["text"]
    elif type(block_types) == str:
        block_types = [block_types]
    return block_types


def get_collection_name():
    collection_name = os.getenv("UE5_DOCS_COLLECTION_NAME")
    if collection_name is None or collection_name == "None":
        collection_name = "ue5_docs"
    return collection_name


def collection_exists(collection_name):
    collections = CLIENT.get_collections().collections
    collection_names = [collection.name for collection in collections]
    return collection_name in collection_names


def list_collections():
    collections = CLIENT.get_collections().collections
    collection_names = [collection.name for collection in collections]
    print(collection_names)


def query_index(query, top_k=10, block_types=None):
    collection_name = get_collection_name()

    if not collection_exists(collection_name):
        raise Exception(f"Collection {collection_name} does not exist. Exisiting collections are: {list_collections()}")
        


    vector = embed_query(query)

    _search_params = models.SearchParams(
        hnsw_ef=128,
        exact=False
    )

    block_types = parse_block_types(block_types)

    _filter = models.Filter(
        must=[
            models.Filter(
                should= [
                    models.FieldCondition(
                        key="block_type",
                        match=models.MatchValue(value=bt),
                    )
                for bt in block_types
                ]  
            )
        ]
    )

    results = CLIENT.search(
        collection_name=collection_name,
        query_vector=vector,
        query_filter=_filter,
        limit=top_k,
        with_payload=True,
        search_params=_search_params,
    
    )

    results = [
        (
            f"{res.payload['url']}#{res.payload['section_anchor']}", 
            res.payload["text"],
            res.score
        )
        for res in results
    ]

    return results


def format_string(s):
    s = s.replace("\(", "(").replace("\)", ")")
    return s


def print_results(query, results, score=True):
    print('\n'*3)
    print("="*80)
    str = f"Query: {query}"
    print(f"{str: ^80}")
    print("="*80)
    for i in range(len(results)):
        result = format_string(results[i][1])
        print(f"{i+1}) {results[i][0]}")
        print(f"--> {result}")
        if score:
            print(f"Score: {results[i][2]}")
        print("-"*80)
    print('\n'*2)


def fiftyone_docs_search(
    query, 
    top_k=10, 
    block_types=None,
    score=False,
    open_url=True
):
    results = query_index(
        query,
        top_k=top_k,
        block_types=block_types
    )

    print_results(query, results, score=score)
    if open_url:
        top_url = results[0][0]
        webbrowser.open(top_url)



class Ue5DocSearch():
    """Class for handling unreal engine documentation queries."""
    def __init__(
            self, 
            top_k = None, 
            block_types = None, 
            score = False, 
            open_url = True
            ):
        self.default_top_k = top_k
        self.default_block_types = block_types
        self.default_score = score
        self.default_open_url = open_url
        
    def __call__(
            self, 
            query, 
            top_k = None, 
            block_types = None, 
            score = None, 
            open_url = None
            ):
        args_dict = {}

        if top_k is None:
            top_k = self.default_top_k
        if top_k is not None:
            args_dict["top_k"] = top_k

        if block_types is None:
            block_types = self.default_block_types
        if block_types is not None:
            args_dict["block_types"] = block_types

        if score is None:
            score = self.default_score
        if score is not None:
            args_dict["score"] = score

        if open_url is None:
            open_url = self.default_open_url
        if open_url is not None:
            args_dict["open_url"] = open_url

        fiftyone_docs_search(query, **args_dict)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', type=str, default=None)
    parser.add_argument('--top_k', type=int, default=5)
    parser.add_argument('--block_types', type=str, default='text')
    parser.add_argument('--score', type=bool, default=False)
    parser.add_argument('--open_url', type=bool, default=True)
    args = parser.parse_args()
    fosearch = Ue5DocSearch(open_url=args.open_url, top_k=args.top_k, score=args.score, block_types=args.block_types)
    fosearch(args.query)