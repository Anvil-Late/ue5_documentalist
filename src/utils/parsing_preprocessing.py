import urllib.request
from markdownify import markdownify as md
import re


url = "https://docs.unrealengine.com/5.1/en-US/using-groom-caches-with-hair-in-unreal-engine/"
with urllib.request.urlopen(url) as f:
    content = f.read()


def remove_dash_sequences(string):
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

def remove_xml(string):
    lines = string.split('\n')
    lines = [line for line in lines if not line.startswith('<?xml')]
    return "\n".join(lines)

def remove_extra_newlines(string):
    string = re.sub(r'\n{3,}', '\n\n', string)
    return string

def remove_unicode(string):
    for uchar in ["\u2500", "\u2514", "\u251c", "\u2502"]:
        string = string.replace(uchar, "")
    for uchar in ["\u2588", "\u2019"]:
        string = string.replace(uchar, "'")
    for uchar in ["\u201d", "\u201c"]:
        string = string.replace(uchar, "\"")
    string = string.replace("\u00a9", "copyright")
    return string

def remove_bolding(string):
    string = string.replace("**", "")
    return string

def remove_footer(string):
    return string.split("[Next ![]")[0]

def split_text_into_components(text):
    components = []
    paragraphs = text.split('\n\n\n')
    start_saving = False
    for paragraph in paragraphs:
        if "\n--" in paragraph:
            start_saving = True
        paragraph = paragraph.strip().replace("\n", "")
        paragraph = remove_dash_sequences(paragraph)
        paragraph = remove_images(paragraph)
        paragraph = remove_links(paragraph)
        paragraph = remove_bolding(paragraph)
        paragraph = remove_header(paragraph)
        paragraph = remove_starting_special_characters(paragraph)
        if paragraph is None:
            continue
        if paragraph.startswith("On this page"):
            continue
        if start_saving:
            if len(paragraph) > 0:
                components.append(paragraph)

    return "\n".join(components)