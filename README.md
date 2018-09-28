# HTML Steganography
A tool to steganographically hide data into HTML files, or any space-insensitive languages.

## How it works
An intuitive approach to encrypt hidden bits into html is to append them as plain text at the end of every line. Although the text is added to the HTML, the secret text is never rendered to the browser. This approach is to encode binary data as space and tabs to replace the existing spaces in the beginning and the end of the line. This way even the source code appears similar to the original source code.

## Why HTML
Ideally, if this script is more perfected, the encoding scheme used in this script can apply to any space/format-insensitive languages like java and C. The reason HTML is particularly interesting is that it could allow secret communication between client and server. But still need more fine tune for this script to adapt to all types of HTML and space-insensitive documents.

## Usage
<pre>
Usage: stego.py [OPTIONS] COMMAND [ARGS]...

  A tool to encrypt and encode messages into any space-insensitive
  programming language
  
Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.
Commands:
  decode  decode a given HTML file
  encode  encode a given HTML file
  maxcap  calculate the maximum capacity of the given HTML document
</pre>

## Encoding flow
The input message is:
1. Pad the message into AES block size
2. Encrypt using AES128, with a random key generated upon encoding/encrypting
3. Convert the encypted cipher text to binary string
4. Encode each bit within the binary string into the HTML using the Schema below.

> Decoding is just the reverse process of encoding.

## Encoding Schema:
| bit | character |
|-----|-----------|
| 0   | '  ' (a space character)      |
| 1   | '\t'      |

| bit | length    |
|-----|-----------|
| 0   | 1      |
| 1   | 4      |

#### Example
I will use `\s` to represent a normal space character below.
Assume that we want to insert the binary `10010` into the line 
```
\t\t\t<div> some text </div>\n
```

First, calculate total number of spaces in the beginning of a line: length of \t x 3 = 12 spaces avaliable.
Then, fit the first bit from the binary 1, which is a tab character and have length 4, into the output string
```
\t
```
the capacity now has 8 left, fit the next bit, which is 0
```
\t\s
```
the capacity is now 7, fit next bit,
```
\t\s\s
```
the capactiy is now 6, fit next bit,
```
\t\s\s\t
```
the capacity is now 2, fit next bit,
```
\t\s\s\t\s
```
all bits were fit within this line, but there are still capacity in this line, in order to fill up the line and maintain its original format, append capacity amount of \s to the prefix.
```
\t\s\s\t\s\s
```
And then add the rest of the line:
```
\t\s\s\t\s\s<div> some text </div>\n
```
to record number of dummy characters was used to fill the end of the line, the number is appended as number of \s before the new line character
```
\t\s\s\t\s\s<div> some text </div>\s\n
```

## Why not encode all bits at the end of the line(infinite capacity)?
It's boring and it defeats the purpose of keeping the message as close to original source code as possible. If all spaces and tabs are encoded at the end of each line, highlighting the text will reveal that there were some alterations to the file thus violated the indistinguishability between encoded cover and original cover.

## Why not use the traditional swapping attributes methods.
Another popular method to do steganography in HTML is by swapping the positions of attributes within a tag, for example:
```
<img src="img_girl.jpg" width="500" height="600">
```
would encode to 
```
<img width="500" src="img_girl.jpg" height="600">
```

given a pre-defined key table:

| tags | primary | secondary |
|------|---------|-----------|
| img  | src     | width     |

Based on this key table, a swap of primary and secondary elements encode the bit 1 into the cover. Decoding is done by comparing the order of attributes with the key table to deduct whether the tag encodes a 0 or 1 bit.

The short side of this approach is that although it provides perfect indetectability, the cost of encoding is too high. Not only does this requires pre-defining a wide range of key tables, each tag/line in the documents has very minimal capacity for encoding long messages, especially consider that AES CBC mode require padded text to 128 bits, the minimum block size. This means that doesn't matter how short a message is, the default requirement for the cover is to have at least 128 possible locations to swap the primary and secondary attributes.


## Notes about Tabulation
The goal of this project is to not only steganographically encode messages into HTML such that the messages are indetectable upon rendering, but also encode messages into HTML such that messages are also indetectable in the source code.

However, the current state of the project cannot fully achieve this effect because of the nature of __tabulation__.

I made a mistake in the beginning of the project assuming that code editors will treat `\t` character literally and render into fixed length of spaces. However, after examine the output and some research, I realized that the `\t` symbolizes an inde ntation to the next [Tab Stop](https://en.wikipedia.org/wiki/Tab_stop). This means that depends on the index of the `\t` character, the length of which may vary. This effect will cause the capacity calculation for each line to be unstable, and sometimes makes the encoded source code appear different(left shifted) than the original source code.

There is a fix to this:

Assuming default tabulation stops is every 4 space, I can calculate the distance between the current `\t` character that I am about to insert and the index of the next tab stop. Then, `distance` amount of spaces are appended after the tab stops to compensate the difference in rendered spaces. When decoding, first scan through the line, base on the index of `\t` and the next tab stop, reverse/remove the appended spaces after the tab stop, and then perform the normal decoding process.

> This fix will reduce the maximum capacity of the document. I will add this fix in the future.

