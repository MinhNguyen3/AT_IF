def string_to_bytes(string):

    hexdigit = (b'0',b'1',b'2',b'3',b'4',b'5',b'6',b'7',b'8',b'9',b'a',b'b',b'c',b'd',b'e',b'f')

    count = 0
    hex_dict = {}
    for x in hexdigit:
        for y in hexdigit:
            if x == b'5' and y == b'c':
                pass
            else:
                hexnumber = b'\\x' + x + y
                hex_dict[hexnumber] = count.to_bytes(1, byteorder='big')

                hexnumber = b'\\x' + x.upper() + y.upper()
                hex_dict[hexnumber] = count.to_bytes(1, byteorder='big')
            count += 1 
    hex_dict[b"\\x5c"] = b"\x5c"
    hex_dict[b"\\x5C"] = b"\x5c"

    byte_string = bytes(string,'utf-8')

    for x in hex_dict.keys():
        byte_string = byte_string.replace(x,hex_dict[x])

    return byte_string

a = input("Type something: ")
print(string_to_bytes(a))
print(len(string_to_bytes(a)))