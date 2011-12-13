from Crypto.Cipher import AES

class Cipher(object):
    def __init__(self, key_request):
        self._create_key (key_request)
        self._algorithm = AES.new(self.key, AES.MODE_ECB)

    def _create_key(self, request ):
        self._key = ""
        i = 1
        while len(self._key) < 32:
            self._key += request[i]
            i += 1

    def _pad (self, string):
        bit_divisibility = len(string) % 16
        while bit_divisibility != 0:
            string += " "
            bit_divisibility = len(string %16)
        return string
    def _trim (self, string):
        temp = string
        while string[len(temp)-1] == " ":
            temp = string[:len(temp)-2]
        return temp

    def encrypt (self, string):
        return self._algorithm.encrypt( self._pad(string) )

    def decrypt (self, string):
        return self._trim ( self._algorithm.decrypt(string) )
