def render_tabs(string: str, tab_width: int = 4) -> str:

    result = ""

    for line in string.splitlines(True):

        index = 0

        for char in line:

            if char == "\t":
                width = tab_width - index % tab_width
                result += " " * width
                index += width
                continue

            result += char
            index += 1

    return result

