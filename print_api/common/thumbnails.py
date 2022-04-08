import os
import re
import base64
from PIL import Image


def extract_thumbnail(gcode_file_path):
    """
    Function to extract the encoded thumbnail within a PrusaSlicer gcode file.
    :param gcode_file_path: the path to the file to have the thumbnail extracted from.
    """
    regex = r"(?:^; thumbnail begin \d+[x ]\d+ \d+)(?:\n|\r\n?)((?:.+(?:\n|\r\n?))+?)(?:^; thumbnail end)"
    # Open the file and extract all the comments to a string.
    with open(gcode_file_path, 'rb') as g_file:
        concat_string = ""
        for line in g_file:
            line = line.decode("utf-8", "ignore")
            if line.startswith(";"):
                concat_string += line@
        # match the thumbnail regex to the string.
        matches = re.findall(regex, concat_string, re.MULTILINE)
        # CHeck the thumbnail exists
        if len(matches) > 1:
            file_name = os.path.basename(gcode_file_path)
            with open(file_name + ".png", "wb") as img:
                # decode the base64 image and write it to a file.
                img.write(base64.b64decode(matches[-1:][0].replace("; ", "").encode()))
        else:
            return None