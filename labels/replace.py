import fileinput

def nth_repl_all(s, sub, repl, nth):
    find = s.find(sub)
    # loop util we find no match
    i = 1
    while find != -1:
        # if i  is equal to nth we found nth matches so replace
        if i == nth:
            s = s[:find]+repl+s[find + len(sub):]
            i = 0
        # find + len(sub) + 1 means we start after the last match
        find = s.find(sub, find + len(sub) + 1)
        i += 1
    return s

def replace_file_text(string1, string2, output_file='label.xml'):
    with fileinput.FileInput(output_file, inplace=True, backup='.bak') as file:
        for line in file:
            print(line.replace(string1, string2), end='')
    return