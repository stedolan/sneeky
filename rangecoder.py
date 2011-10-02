import random

class RangeCodec(object):
    def __init__(self):
        self.low = 0
        self.high = 255
    def check(self):
        assert self.low < self.high
        assert 0 <= self.low < self.high <= 255
        if hasattr(self, 'val'):
            assert self.low <= self.val <= self.high
    def span(self):
        return self.high - self.low + 1
    def step(self, n):
        step = self.span() / n
        assert step > 0
        return step
    def narrow(self, k, n):
        assert 0 <= k < n
        step = self.step(n)
        self.low += k * step
        if k < n - 1:
            self.high = self.low + step - 1
    def shift(self):
        while self.low & 128 == self.high & 128:
            #self.check()
            b = (self.low & 128) / 128
            self.low = (self.low & ~128) << 1
            self.high = ((self.high & ~128) << 1) | 1
            yield b
        self.check()

class RangeEncoder(RangeCodec):
    def __init__(self, data):
        RangeCodec.__init__(self)
        self.datalength = float(len(data))
        self.data = list(data)
        self.data.reverse()
        self.val = 0
        self.endmarker = False
        for i in range(8):
            self.val = self.val << 1
            self.val |= self.nextbit()

    def nextbit(self):
        if self.data:
            return self.data.pop()
        else:
            if not self.endmarker:
                self.endmarker = True
                return 1
            else:
                return 0

    def finished(self):
        # FIXME
        return self.endmarker and self.val == self.low

    def completion_est(self):
        return 1.0 - (float(len(self.data)) / self.datalength)
        

    def _encode(self, n):
        step = self.step(n)
        k = (self.val - self.low) / step
        if k >= n: k = n-1
        self.narrow(k, n)
        for bit in self.shift():
            self.val = ((self.val & ~128) << 1) | self.nextbit()
        return k

    def encode(self, n):
        if self.span() >= n: return self._encode(n)
        else:
            bit = self._encode(2)
            b = (n+1)/2
            if bit == 0:
                return self.encode(b)
            else:
                return b + self.encode(n-b)
            

class RangeDecoder(RangeCodec):
    def __init__(self):
        RangeCodec.__init__(self)
        self.data = []
    def nextbit(self, b):
        self.data.append(b)
    def _decode(self, k, n):
        self.narrow(k, n)
        for bit in self.shift():
            self.nextbit(bit)

    def decode(self, k, n):
        if self.span() >= n: self._decode(k, n)
        else:
            b = (n+1)/2
            if k < b:
                self._decode(0, 2)
                self.decode(k, b)
            else:
                self._decode(1, 2)
                self.decode(k-b, n-b)

    def finish(self):
        while self.low:
            self.nextbit(1 if self.low & 128 else 0)
            self.low = (self.low & ~128) * 2
        while self.data.pop() == 0:
            pass
        return self.data
        
def testcodec():
    d = [random.randint(0,1) for i in range(100)]
    w = [random.randint(2,40) for i in range(100)]
    enc = RangeEncoder(d)
    dec = RangeDecoder()
    c = [enc.encode(i) for i in w]
    for k,n in zip(c,w):
        print k, n
        dec.decode(k,n)
    d2 = dec.finish()
    print d2
    return d == d2
