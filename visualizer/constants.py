CMD_FILE_PATH = "visualizer/commands.txt"
TEMPLATE_CMD_FILE_PATH = "visualizer/template_commands.txt"
CLASS_FILE_PLACEHOLDER = "##PLACEHOLDER_CLASS_FILE##"


class Color:
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    TITLE = UNDERLINE + BOLD + BLUE
