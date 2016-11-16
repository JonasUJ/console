import re

COMMENT_PATTERN = re.compile(r'^# .*')
HEADER_PATTERN = re.compile(r'^- .*')
CONTENT_PATTERN = re.compile(r'{\n*(?:([^\n\r{}]+: [^\n\r{}]+\n?))*\n*}')

def parse_file(file):
    with open(file, 'r') as f:
        contents = f.read()

    headers = []
    for line in contents.split('\n'):
        try:
            contents = contents.replace(COMMENT_PATTERN.match(line).string, '')
        except AttributeError:
            pass
        if HEADER_PATTERN.match(line):
            headers.append(HEADER_PATTERN.match(line).string.replace('- ', ''))

    final_dict = []
    for header in headers:
        header_dict = []
        ncontents = CONTENT_PATTERN.search(contents[contents.index(header):]).group(0)
        ncontents = ncontents.replace('{', '').replace('}', '')
        for line in ncontents.split('\n'):
            if len(tuple(line.split(': '))) == 2:
                header_dict.append(tuple(line.split(': ')))
        header_dict = dict(header_dict)
        final_dict.append((header, header_dict))

    return dict(final_dict)