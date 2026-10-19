"""Read geosite.dat / geoip.dat (protobuf, Xray-core common/geodata: GeoSiteList / GeoIPList,
entry = field 1; inside an entry: code = field 1, items = field 2) without extra dependencies."""


def _varint(b, i):
    x = s = 0
    while True:
        c = b[i]; i += 1
        x |= (c & 0x7F) << s; s += 7
        if c < 0x80:
            return x, i


def _fields(b):
    i = 0
    while i < len(b):
        k, i = _varint(b, i)
        f, w = k >> 3, k & 7
        if w == 0:
            v, i = _varint(b, i)
        elif w == 2:
            n, i = _varint(b, i); v = b[i:i + n]; i += n
        else:
            raise ValueError(f"unexpected wire type {w}")
        yield f, v


def entries(path):
    """{CODE: number of items} for every entry of the file."""
    out = {}
    for _, entry in _fields(open(path, "rb").read()):
        code, n = None, 0
        for f, v in _fields(entry):
            if f == 1:
                code = v.decode()
            elif f == 2:
                n += 1
        out[code.upper()] = n
    return out
