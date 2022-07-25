import json
import struct
import sys
from tqdm import tqdm


def _write_byte(data, fp):
  while len(data) >= 8:
    int_val = int(data[:8], base=2)
    fp.write(struct.pack("B", int_val))
    data = data[8:]

  return data


def _byte_to_bit(data: bytes):
  data = int.from_bytes(data, "little")
  res = bin(data)[2:]

  if len(res) < 8:
    res = "0" * (8 - len(res)) + res

  return res


def encode(path: str):
  """Encode given file by Huffman code."""
  with open(path, "r") as f:
    # Count the frequency of each symbol appearing in the file
    print(f"\nRead {path}...")
    sym_freq = {}
    s = f.read(1)
    while s != "":
      if s not in sym_freq:
        sym_freq[s] = 1
      else:
        sym_freq[s] += 1
      s = f.read(1)

    # Construct Huffman tree
    size = len(sym_freq)
    length = 2 * size
    sym = [""] * size + list(sym_freq.keys())
    freq = [0] * size + list(sym_freq.values())
    parent = [0] * length
    left = parent.copy()
    right = parent.copy()

    # Build Huffman tree
    for i in range(size - 1, 0, -1):
      min1 = min2 = sys.maxsize
      i1 = i2 = 0

      for j in range(i + 1, length):
        if parent[j] == 0:
          if freq[j] < min1:
            min2 = min1
            min1 = freq[j]
            i2 = i1
            i1 = j
          elif freq[j] < min2:
            min2 = freq[j]
            i2 = j

      freq[i] = min1 + min2
      left[i] = i1
      right[i] = i2
      parent[i1] = i
      parent[i2] = i

    # Get Huffman code
    symbol = [""] * size
    code = [""] * size

    for i in range(size, length):
      symbol[i - size] = sym[i]
      prt = parent[i]
      child = i

      while prt:
        if left[prt] == child:
          code[i - size] = "0" + code[i - size]
        else:
          code[i - size] = "1" + code[i - size]

        child = prt
        prt = parent[prt]

    hfcode = dict(zip(symbol, code))

    # Store codebook
    hfcode["filelen"] = sum(sym_freq.values())
    hfcode["filetype"] = path.split(".")[1]
    codebook = json.dumps(hfcode, separators=(",", ":")).encode("utf-8")

    with open(path.split(".")[0] + ".hf", "wb") as handle:
      handle.write(struct.pack("i", len(codebook)))
      handle.write(codebook)

      # Encode
      print("Encoding...")
      with tqdm(total=f.tell(), unit_scale=True) as pbar:
        f.seek(0)
        s = f.read(1)
        data = ""
        while s != "":
          pbar.update(1)
          hfc = hfcode[s]
          data = data + hfc
          data = _write_byte(data, handle)
          s = f.read(1)

        while len(data) > 0 and len(data) < 8:
          data += "0" * (8 - len(data))
        if len(data) == 8:
          handle.write(struct.pack("B", int(data, base=2)))

  print(f"File {path} has been encoded successfully!\n")


def decode(path: str):
  """Decode given .hf file."""
  # Report error if file type is not .hf
  if path.split(".")[-1] != "hf":
    raise NameError("Unsupported file type.")

  with open(path, "rb") as to_be_decoded:
    # Get length of codebook
    cb_len_bytes = to_be_decoded.read(4)
    cb_len = int.from_bytes(cb_len_bytes, "little")

    # Get codebook
    cb_json = to_be_decoded.read(cb_len).decode()
    codebook = json.loads(cb_json)
    file_len = codebook.pop("filelen")
    filetype = codebook.pop("filetype")
    codebook = dict([(value, key) for key, value in codebook.items()])

    # Decode
    print("\nDecoding...")
    with tqdm(total=file_len, unit_scale=True) as pbar:
      with open(path[:-3] + "_unzipped." + filetype, "w") as decoded:
        buffer = _byte_to_bit(to_be_decoded.read(1))
        decode_num = 0
        i = 1

        while decode_num < file_len:
          if i > len(buffer):
            buffer += _byte_to_bit(to_be_decoded.read(1))

          s = buffer[:i]
          if s not in codebook:
            i += 1
            continue

          decoded.write(codebook[s])
          decode_num += 1
          pbar.update(1)
          buffer = buffer[i:]
          i = 1

  print(f"File {path} has been decoded successfully!\n")


if __name__ == "__main__":
  encode("note.md")
  decode("note.hf")
