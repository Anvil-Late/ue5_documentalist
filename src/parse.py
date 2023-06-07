import urllib.request
from urllib.error import URLError, HTTPError
from markdownify import markdownify as md
from utils.parsing_preprocessing import split_text_into_components

def main():
    urls_registry = "/Users/anvil/Documents/python/github/ue5_documentalist/src/utils/urls.txt"
    with open(urls_registry, 'r') as f:
        urls = f.read()
    urls = urls.split('\n')
    for idx, url in enumerate(urls):
        if idx % 100 == 0:
            print(f"Processing url {idx}")
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
        md_content = md(content.decode('utf-8'))
        preproc_content = split_text_into_components(md_content)
        
        with open(f"./documents/subsection_{idx}.txt", "w") as f:
            f.write(preproc_content)


if __name__ == "__main__":
    main()
