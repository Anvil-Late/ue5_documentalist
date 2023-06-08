import openai
from openai.error import InvalidRequestError
import glob
import argparse
import pickle
import json
import os

def embed(subsection_dict_path, security):
    """Embed the files in the directory.

    Args:
        subsection_dict_path (dict): Path to the dictionary containing the subsections.
        security (str): Security setting. Either "activated" or "deactivated".
                        prevents the function from running if not "deactivated" 
                        and avoids unexpected costs.

    Returns:
        embeddings (dict): Dictionary containing the embeddings.
    """

    # check security
    if security != "deactivated":
        raise Exception("Security is not deactivated.")
    
    # load subsections
    with open(subsection_dict_path, 'r') as f:
        subsection_dict = json.load(f)

    # initialize dictionary to store embeddings
    embeddings = {}

    # For debugging purposes only
    # Compute average text length to embed
    dict_len = len(subsection_dict)
    total_text_len = 0
    for url, subsection in subsection_dict.items():
        total_text_len += len(subsection['content'])
    avg_text_len = total_text_len / dict_len

    # initialize openai api
    model = "text-embedding-ada-002"
    with open('/Volumes/credentials/openai/api_key.txt', 'r') as protected_file:
        api_key = protected_file.read()
    openai.api_key = api_key
    
    # loop through subsections
    for url, subsection in subsection_dict.items():
        subsection_name = subsection['title']
        text_to_embed = subsection['content']
        # make request for embedding
        try:
            response = openai.Embedding.create(
                input=text_to_embed,
                model=model
            )
            embedding = response['data'][0]['embedding']

        except InvalidRequestError as e:
            print(f"Error with url {url}")
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
            print(f'Tried to embed {len(text_to_embed)} characters while average is {avg_text_len}')
            continue

        # add embedding to dictionary
        embeddings[url] = {
            "title": subsection_name,
            "embedding": embedding
        }

    return embeddings

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--subsections_path', type=str, default='./documents/subsections.json')
    parser.add_argument('--security', type=str, default='activated')
    args = parser.parse_args()
    embeddings = embed(args.subsections_path, args.security)
    # save embeddings to pickle file
    with open(os.path.join("./embeddings", 'embeddings.pkl'), 'wb') as f:
        pickle.dump(embeddings, f)
    # save embeddings to json file
    with open(os.path.join("./embeddings", 'embeddings.json'), 'w') as f:
        json.dump(embeddings, f)

