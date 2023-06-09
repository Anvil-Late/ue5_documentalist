import openai
from InstructorEmbedding import INSTRUCTOR
import os
import qdrant_client as qc
import qdrant_client.http.models as models
from rich import print
import webbrowser
import torch

CLIENT = qc.QdrantClient(url="localhost")
METRIC = models.Distance.DOT

def embed_query(query, embedder):

    if embedder == "openai":
        # Fetch API key from environment variable or prompt user for it
        api_key = os.getenv('API_KEY')
        if api_key is None:
            api_key = input("Please enter your OpenAI API key: ")
        
        openai_model = "text-embedding-ada-002"

        openai.api_key = api_key
        response = openai.Embedding.create(
                    input=query,
                    model=openai_model
        )
        embedding = response['data'][0]['embedding']

    elif embedder == "instructor":
        instructor_model = INSTRUCTOR('hkunlp/instructor-xl')
         # set device to gpu if available
        if (torch.backends.mps.is_available()) and (torch.backends.mps.is_built()):
            device = torch.device("mps")
        elif torch.cuda.is_available():
            device = torch.device("cuda")
        else:
            device = torch.device("cpu")

        instruction = "Represent the UnrealEngine query for retrieving supporting documents:"
        embedding = instructor_model.encode([[instruction, query]], device=device)
        embedding = [float(x) for x in embedding.squeeze().tolist()]
    else:
        raise ValueError("Embedder must be 'openai' or 'instructor'")
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


def query_index(query, embedder, top_k=10, block_types=None):
    """
    Queries the OpenAI index for documents that match the given query.

    Args:
        query (str): The query to search for.
        top_k (int, optional): The maximum number of documents to return. Defaults to 10.
        block_types (str or list of str, optional): The types of document blocks to search in. Defaults to "text".

    Returns:
        A list of dictionaries representing the matching documents, sorted by relevance. Each dictionary contains the following keys:
        - "id": The ID of the document.
        - "score": The relevance score of the document.
        - "text": The text content of the document.
        - "block_type": The type of the document block that matched the query.
    """
    collection_name = get_collection_name()

    if not collection_exists(collection_name):
        raise Exception(f"Collection {collection_name} does not exist. Exisiting collections are: {list_collections()}")
        


    vector = embed_query(query, embedder)

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


def ue5_docs_search(
    query, 
    embedder=None,
    top_k=10, 
    block_types=None,
    score=False,
    open_url=True
):
    """
    Searches the OpenAI index for documents related to the given query and prints the top results.

    Args:
        query (str): The query to search for.
        top_k (int, optional): The maximum number of documents to return. Defaults to 10.
        block_types (str or list of str, optional): The types of document blocks to search in. Defaults to "text".
        score (bool, optional): Whether to include the relevance score in the output. Defaults to False.
        open_url (bool, optional): Whether to open the top URL in a web browser. Defaults to True.

    Returns:
        None
    """
    # Check if embedder is 'openai' or 'instructor'. raise error if not
    assert embedder in ['openai', 'instructor'], f"Embedder must be 'openai' or 'instructor'. Not {embedder}"

    results = query_index(
        query,
        embedder=embedder,
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
            embedder = "openai",
            top_k = None, 
            block_types = None, 
            score = False, 
            open_url = True
            ):
        self.default_embedder = embedder
        self.default_top_k = top_k
        self.default_block_types = block_types
        self.default_score = score
        self.default_open_url = open_url
        
    def __call__(
            self, 
            query, 
            embedder = None,
            top_k = None, 
            block_types = None, 
            score = None, 
            open_url = None
            ):
        args_dict = {}

        if embedder is None:
            embedder = self.default_embedder
        if embedder is not None:
            args_dict["embedder"] = embedder

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

        ue5_docs_search(query, **args_dict)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', type=str, default=None)
    parser.add_argument('--top_k', type=int, default=5)
    parser.add_argument('--block_types', type=str, default='text')
    parser.add_argument('--score', type=bool, default=False)
    parser.add_argument('--open_url', type=bool, default=True)
    parser.add_argument('--embedder', type=str, default='instructor')
    args = parser.parse_args()
    if args.embedder == 'openai':
        DIMENSION = 1536
    else:
        DIMENSION = 768
    fosearch = Ue5DocSearch(embedder=args.embedder, open_url=args.open_url, top_k=args.top_k, score=args.score, block_types=args.block_types)
    fosearch(args.query)