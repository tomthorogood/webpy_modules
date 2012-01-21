from Crypto.Cipher import AES
import binascii

class Cipher(object):
    def __init__(self, key_request):
        self._create_key (key_request)
        self._algorithm = AES.new(self._key, AES.MODE_ECB)

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
            bit_divisibility = len(string) %16
        return string
    def _trim (self, string):
        temp = string
        while string[len(temp)-1] == " ":
            temp = string[:len(temp)-1]
        return temp.split(" ")[0]

    def encrypt (self, plaintext):
        ciphertext = self._algorithm.encrypt( self._pad(plaintext) )
        return ciphertext

    def decrypt (self, ciphertext):
         return self._trim ( self._algorithm.decrypt(ciphertext) )
