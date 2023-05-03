from PIL import Image, ImageDraw  # Подключим необходимые библиотеки.


def write(ifile, ofile, text):
    secret = ''

    for char in text:
        ccode = str(bin(ord(char)))[2:]
        while len(ccode) < 16:
            ccode = '0' + ccode
        secret += ccode
    secret += '0000000000000000'

    image = Image.open(ifile)
    draw = ImageDraw.Draw(image)
    width, height = image.size
    pix = image.load()

    dindex = 0

    for w in range(width):
        for h in range(height):

            red = pix[w, h][0]
            green = pix[w, h][1]
            blue = pix[w, h][2]

            try:
                if blue % 2 != int(secret[dindex]):
                    blue += 1
                    if blue > 255:
                        blue -= 2
                dindex += 1
            except IndexError:
                if blue % 2 != 0:
                    blue += 1
                    if blue > 255:
                        blue -= 2

            draw.point((w, h), (red, green, blue))
    fformat = 'PNG'

    if ofile[-3].endswith('png'):
        fformat = 'PNG'
    elif ofile[-3].endswith('jpg'):
        fformat = 'JPEG'

    image.save(ofile, fformat)



def read(file):
    image = Image.open(file)
    width = image.size[0]
    height = image.size[1]
    pix = image.load()

    solve = ''
    out = ''

    for w in range(width):
        for h in range(height):
            blue = pix[w, h][2]
            solve += str(blue % 2)

    solve = list(solve)

    i = 0
    while len(solve) >= 16:
        char = ''.join(solve[:16])
        char = int(char, 2)
        if char == 0:
            break
        out += chr(char)

        del solve[:16]

        i += 1

    return out


if __name__ == '__main__':
    choose = input('Прочесть или записать? [r/w] ')

    if choose == 'w':
        text = input('Введи текст для зашифроки: ')
        write('unknown.png', 'secret.png', text)

    elif choose == 'r':
        print(read('secret.png'))
