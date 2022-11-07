def content_between(separator: str, string: str) -> list[str]:
    """Get the content between two separators of a string"""
    
    assert len(separator) > 1, "Invalid separator! Only 1 char is accepted ..."

    content_open = False
    content = []

    for char in string:

        if char == separator:
            if content_open:
                content_open = False
            else:
                content.append("")
                content_open = True
        else:
            if content_open:
                content[-1] += char

    return content

