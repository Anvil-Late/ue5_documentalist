# UE5 Documentalist

UE5 Documentalist is a Python Project that allows users to make natural language queries to the Unreal Engine documentation.

You can, for instance ask 'what system can I to avoid collision between agents?' and be redirected to the documentation that best suits your needs.

## Example

![](./resources/example_use.gif)

## Setup

Before running the script, you need to perform the following steps:

**Parsed documentation and embeddings are provided in the repo. If you simply want query the Unreal Engine documentation, you can skip directly to step 3.**
If you want to built this from scratch for your own use case, start from step 1.

1. Parse the documentation using `parse.py`: `python src/parse.py --urls_registry <PATH_TO_URLS_TO_PARSE> --subsections_path <OUTPUT_PATH>`
2. Embed the subsections using `embed.py`: `python src/embed.py --embedder <EMBEDDER> --subsections_path <OUTPUT_PATH_OF_PARSE.PY>`. Embedder can be either `instructor` or `openai`. If you use `openai`, since it is a pay-as-you-go API, you need to add `--security deactivated`, which is a param I set to avoid running the script by mistake and spend money on it.
3. Create a Qdrant vector index by running the following commands:  `docker pull qdrant/qdrant`  and  `docker run -d -p 6333:6333 qdrant/qdrant`
4. Install the Qdrant client using `pip install qdrant-client` (this is included in `requirements.txt`).
5. Populate the Qdrant vector index unsing `create_index.py`: `python src/create_index.py --embedder <EMBEDDER> --embeddings_path <OUTPUT_PATH_OF_EMBED.PY> --content_path <OUTPUT_PATH_OF_PARSE.PY>`

## Usage

1. Set your OpenAI API key as an environment variable: `export API_KEY=your-api-key` (only if you want to use OpenAI's text-embedding-ada-002 embedder)
2. Run the script: `python query_index.py --embdedder <EMBEDDER> --query <QUERY>`

### Options

- `--embedder`: The embedding model to use. Can be 'openai' or 'instructor'. Default is 'instructor'.
- `--top_k`: The number of results to display. Default is 5.
- `--block_types`: Allows to filter the type of block searched. For the Unreal Engine 5 documentation, everything is text, but this parameter can be useful if a documentation has both text and code, for instance. Default is 'text'
- `--score`: Shows the confidence score of each result shown. Default is False.
- `--open_url`: Automatically opens a web page to the top scored documentation. Default is True.

## License

UE5 Documentalist is licensed under the MIT License. See LICENSE for more information.

