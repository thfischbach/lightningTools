GRAY    = "30"
RED     = "31"  
GREEN   = "32"
YELLOW  = "33"
BLUE    = "34"
MAGENTA = "35"
CYAN    = "36"

def printFormatted(text, color=None, bold=False):
    s = "\033["
    if bold:
        s += "1"
    else:
        s += "0"
    s += ";"
    s += color
    s += "m"
    s += text
    s += "\033[0;0m"
    print(s)
    
def printRed(text):
    printFormatted(text, RED)

def printGreen(text):
    printFormatted(text, GREEN)

def printYellow(text):
    printFormatted(text, YELLOW)