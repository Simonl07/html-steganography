import click
import re
import AES
import base64

prefix_regex = re.compile('^(?P<match>[\s]+)\S')
suffix_regex = re.compile('\S(?P<match>[\s]+)$')


bit_space_map = {
     '0': 1,
     '1': 4
}

bit_char_map = {
    '0': ' ',
    '1': '\t'
}

bit_flip_map = {
    '0': '1',
    '1': '0'
}

char_bit_map = {
    ' ': '0',
    '\t': '1'
}


def bytes_2_bins(bs):
    out = ''
    for b in bs:
        out += byte_2_bin(b)
    return out


def byte_2_bin(b):
    return "{:08b}".format(int(b))


def bins_2_bytes(b):
    bytes = [b[i:i + 8] for i in range(0, len(b), 8)]
    output = []
    for byte in bytes:
        output.append(bin_2_byte(byte))
    return b''.join(output)


def bin_2_byte(b):
    return int(b, 2).to_bytes(len(b) // 8, byteorder='big')


def encode_line(line, queue):
    if line.strip() == '':
        return '\n'
    trailing_spaces = get_space(line, prefix_regex)
    capacity = 0
    for s in trailing_spaces:
        capacity += bit_space_map[char_bit_map[s]]
    padded = False
    prefix = ''

    while len(queue) != 0 and bit_space_map[queue[0]] <= capacity:
        bit = queue.pop(0)
        capacity -= bit_space_map[bit]
        prefix += bit_char_map[bit]

    if capacity != 0:
        padded = True
        prefix += ' ' * capacity

    line = prefix + line[len(trailing_spaces):]

    if padded:
        line = re.sub('[\t \n]*$', (' ' * capacity) + "\n", line)

    return line


def decode_line(line, queue):
    prefix = get_space(line, prefix_regex)
    suffix_match = re.search('\S(?P<match>[\t ]+)$', line)
    if not suffix_match:
        suffix = ''
    else:
        suffix = suffix_match.group('match')

    temp = prefix[: len(prefix) - len(suffix)]
    queue.append(temp)


def get_space(line, regex):
    match = regex.match(line)
    if not match:
        return ''

    trailing = match.group('match')
    return trailing


@click.version_option(0.1)
@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.pass_context     # ctx
def cli(ctx):
    """ A tool to encrypt and encode messages into any space-insensitive programming language """
    pass


@cli.command(short_help='encode a given HTML file')
@click.argument('input_file', type=click.File('r'))
@click.argument('output', type=click.File('w'))
@click.argument('message', type=str)
def encode(input_file, output, message):
    lines = input_file.readlines()
    key, c, iv = AES.encrypt(message)
    temp = bytes_2_bins(c)
    print(temp)

    print(f"input size(after padding): {len(temp)}")
    s = list(temp)
    results = []
    for line in lines:
        results.append(encode_line(line, s))

    if len(s) != 0:
        print(f"Insufficient space, need larger cover ({len(s)} more bits) for given message")
        output.writelines(results)
        return

    output.writelines(results)
    key = base64.b64encode(key)
    iv = base64.b64encode(iv)
    print(f"KEY: {key.decode()} iv: {iv.decode()}")


@cli.command(short_help='decode a given HTML file')
@click.argument('input_file', type=click.File('r+'))
@click.argument('key', type=str)
@click.argument('iv', type=str)
def decode(input_file, key, iv):
    key = base64.b64decode(key)
    iv = base64.b64decode(iv)
    lines = input_file.readlines()

    s = []
    for line in lines:
        decode_line(line, s)

    temp = ''
    s = ''.join(s)
    for c in s:
        if c == ' ':
            temp += '0'
        else:
            temp += '1'
    print(temp)
    temp = bins_2_bytes(temp)

    print(AES.decrypt(temp, key, iv))


@cli.command(short_help='calculate the maximum capacity of the given HTML document')
@click.argument('input_file', type=click.File('r+'))
def maxcap(input_file):
    lines = input_file.readlines()
    total = 0
    for line in lines:
        if line.strip() == '':
            continue
        trailing_spaces = get_space(line, prefix_regex)
        for c in trailing_spaces:
            total += bit_space_map[char_bit_map[c]]

    print(f"Longest(all 0): {total}, Biggest(all 1): {total // 4}")


if __name__ == '__main__':
    cli()
