import sys

log_file = sys.argv[1]
file_prev = ""
tags = tuple(sys.argv[2].split(","))


def str_diff(str1:str,str2:str) -> str:
    return str1[len(str2):]
        


while 1:
    try:
        new_log = ""
        with open("logs/" + log_file,"r") as f:
            file_current = f.read()
        if file_prev != file_current:
            for log in str_diff(file_current,file_prev).split("\n"):
                for tag in tags:
                    if log.startswith("[{}]".format(tag)):
                            new_log += log + "\n"
        print(new_log, end="")
        file_prev = file_current
    except KeyboardInterrupt:
        print("Interrupt detected, quitting!")
        exit(0)
        break



