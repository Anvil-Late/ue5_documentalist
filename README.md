# UE5 Documentalist

UE5 Documentalist is a Python Project that allows user to make natural language queries to the Unreal Engine documentation

## Example

![](./resources/example_use.gif)

## Setup

Before running the script, you need to perform the following steps:

1. Parse the documentation using `parse.py`: `python parse.py --security public`
2. Embed the subsections using `embed.py`: `python embed.py --embedder openai --security public`
3. Create a Qdrant vector index by running the following commands: `docker pull qdrant/qdrant docker run -d -p 6333:6333 qdrant/qdrant`
4. Install the Qdrant client using `pip install qdrant-client` (this is included in `requirements.txt`).

## Usage

1. Set your OpenAI API key as an environment variable: `export API_KEY=your-api-key` (only if you want to use OpenAI's text-embedding-ada-002 embedder)
2. Run the script: `python query_index.py --embdedder <EMBEDDER> --query <QUERY>`

## Options

- `--embedder`: The embedding model to use. Can be 'openai' or 'instructor'. Default is 'instructor'.
- `--top_k`: The number of results to display. Default is 5.
- `--block_types`: Allows to filter the type of block searched. For the Unreal Engine 5 documentation, everything is text, but this parameter can be useful if a documentation has both text and code, for instance. Default is 'text'
- `--score`: Shows the confidence score of each result shown. Default is False.
- `--open_url`: Automatically opens a web page to the top scored documentation. Default is True.

## License

UE5 Documentalist is licensed under the MIT License. See LICENSE for more information.

