import re
from urllib.parse import urlparse

def remove_dash_sequences(string):
    """Remove dash sequences from the string.

    Args:
        string (str): String to remove dash sequences from.

    Returns:
        str: String with dash sequences removed.
    """
    pattern = r'-(-+)'  # Negative lookbehind and lookahead to match single dashes
    result = re.sub(pattern, '', string)
    return result

def remove_images(string):
    return re.sub('!\[.+\]\(.*\)', '', string)

def remove_header(string):
    if len(string) > 0 and string[0] == "#":
        return re.sub('#( *)', '', string)
    return string

def remove_starting_special_characters(string):
    result = re.sub(r'^[^\w\s]+( *)', '', string)
    return result

def remove_extra_newlines(string):
    string = re.sub(r'\n{3,}', '\n\n', string)
    return string

def remove_bolding(string):
    string = string.replace("**", "")
    return string

def remove_footer(string):
    return string.split("[Next ![]")[0]

def remove_links(string):
    """Remove links from the string.
    
    Args:
        string (str): String to remove links from.
        
    Returns:
        str: String with links removed.
            
    """
    match = re.search('\[.*?\]\(.*?\)', string)
    if match is not None:
        start, end = match.span()
        link = string[start:end]
        link_text = link[1:].split(']')[0]
        if link_text != "¶":
            return string[:start] + link_text + remove_links(string[end:])
        else:
            return string[:end] + link + remove_links(string[end:])
    return string

def split_text_into_components(text):
    """Split the text into components.

    Args:
        text (str): Text to split.

    Returns:
        str: The text split into components.
    """
    components = []
    paragraphs = text.split('\n\n\n')
    start_saving = False
    for paragraph in paragraphs:
        if "\n--" in paragraph:
            start_saving = True
        
        paragraph = remove_dash_sequences(paragraph)
        paragraph = remove_images(paragraph)
        paragraph = remove_bolding(paragraph)
        paragraph = remove_header(paragraph)
        paragraph = remove_starting_special_characters(paragraph)
        paragraph = paragraph.strip().replace("\n\n\n", "\n")
        paragraph = remove_links(paragraph)
        if paragraph is None:
            continue
        if paragraph.startswith("On this page"):
            continue
        if start_saving:
            if len(paragraph) > 0:
                components.append(paragraph)

    return "\n".join(components)


def extract_info_from_url(url):
    """Extract the info from the url.

    Args:
        url (str): Url to extract the info from.

    Returns:
        str: The info extracted from the url.
    """
    parsed_url = urlparse(url)
    path = parsed_url.path.strip('/')  # Remove leading and trailing slashes

    if path.endswith('/'):
        path = path[:-1]  # Remove trailing slash

    # Extract the last part of the path
    info = path.split('/')[-1]

    return info


def check_total_number_of_characters(files_dir):
    """Check the total number of characters in the files.
    
    Args:
        files_dir (str): Directory containing the files.
        
    Returns:
        None
    """
    import glob
    files = glob.glob(files_dir + "/*.txt")
    total_characters = 0
    for file in files:
        with open(file, 'r') as f:
            content = f.read()
        total_characters += len(content)
    print(f"Total number of characters: {total_characters}")


def check_total_number_of_words(files_dir):
    import glob
    files = glob.glob(files_dir + "/*.txt")
    total_words = 0
    for file in files:
        with open(file, 'r') as f:
            content = f.read()
        total_words += len(content.split())
    print(f"Total number of words: {total_words}")
