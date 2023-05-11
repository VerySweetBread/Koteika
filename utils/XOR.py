def char_encode(text, key):
    itext = ''
    ikey = ''
    out = ''

    for char in text:
        char = str(bin(ord(char)))
        char = char.replace('0b', '')
        while len(char) < 16:
            char = '0' + char
        itext += char

    for char in key:
        char = str(bin(ord(char)))
        char = char.replace('0b', '')
        while len(char) < 16:
            char = '0' + char
        ikey += char

    if len(itext) > len(ikey):
        tmp = ikey
        ikey = tmp * int(len(itext) / len(tmp))
        ikey += tmp[:(len(itext) % len(tmp))]

    for i in range(len(itext)):
        a = itext[i]
        b = ikey[i]

        if a == b:
            out += '0'
        else:
            out += '1'
    tmp = list(out)
    out = ''

    while len(tmp) >= 16:
        char = ''.join(tmp[:16])
        char = int(char, 2)
        out += chr(char)

        del tmp[:16]

    return out


if __name__ == '__main__':
    cat = char_encode('123123', 'кот')
    print(cat)
    print(char_encode(cat, 'кот'))
