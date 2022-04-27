import huffman
import sys


if __name__ == '__main__':
    option = sys.argv[1]

    if option == '-e' or option == '--encode':
        huffman.encode(sys.argv[2])
    elif option == '-d' or option == '--decode':
        try:
            huffman.decode(sys.argv[2])
        except NameError:
            print("Not a .hf file. Please use a .hf file.")
    elif option == '--help' or option == '-h':
        print('''
To compress one file, just enter

    python main.py -e filename
or
    python main.py --encode filename

To uncompress one file, enter

    python main.py -d filename
or
    python main.py --decode filename

To read guidance again, enter

    python main.py -h
or
    python main.py --help
''')
