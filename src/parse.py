import urllib.request
from urllib.error import URLError, HTTPError
from markdownify import markdownify as md
import json
from utils.parsing_preprocessing import split_text_into_components, extract_info_from_url

def main(limit=100):
    urls_registry = "/Users/anvil/Documents/python/github/ue5_documentalist/src/utils/urls.txt"
    with open(urls_registry, 'r') as f:
        urls = f.read()
    urls = urls.split('\n')

    # initialize dictionary to store subsections
    subsections = {}
    for idx, url in enumerate(urls):
        # stop if limit is reached
        if limit is not None:
            if idx > limit:
                break
        if idx % 100 == 0:
            print(f"Processing url {idx}")

        # make request
        try:
            with urllib.request.urlopen(url) as f:
                content = f.read()
        except HTTPError as e:
            print(f"Error with url {url}")
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
            continue
        except URLError as e:
            print(f"Error with url {url}")
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
            continue
        # parse content
        md_content = md(content.decode('utf-8'))
        preproc_content = split_text_into_components(md_content)
        # extract info from url name
        subsection_title = extract_info_from_url(url)
        # add to dictionary
        subsections[url] = {
            "title": subsection_title,
            "content": preproc_content
        }
    # save dictionary
    with open('./documents/subsections.json', 'w') as f:
        json.dump(subsections, f)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=None)
    main(limit=parser.parse_args().limit)
