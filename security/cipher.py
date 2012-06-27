from Crypto.Cipher import AES

class Cipher(object):
    """
    An easy to work with object based on the PyCrypto Cipher module.
    """
    def __init__(self, key_request):
        """
        The key_request is the string that will do both the encrypting and decrypting of data.
        """
        self._create_key (key_request)
        self._algorithm = AES.new(self._key, AES.MODE_ECB)

    def _create_key(self, request ):
        """
        Generates a 32 character strng from the passed argument. Does not return it.
        """
        self._key = ""
        i = 1
        while len(self._key) < 32:
            self._key += request[i]
            i += 1

    def _pad (self, string):
        """
        Adds whitespace to a string so that it meets the requirements for encrypting.
        """
        bit_divisibility = len(string) % 16
        while bit_divisibility != 0:
            string += " "
            bit_divisibility = len(string) %16
        return string

    def _trim (self, string):
        """
        Trims whitespace from a decrypted string.
        """
        try:
            temp = string
            while string[len(temp)-1] == " ":
                temp = string[:len(temp)-1]
            return temp.split(" ")[0]
        except TypeError:
            return string

    def encrypt (self, plaintext):
        """
        Encrypts!
        Takes any string as an argument.
        Must be decrpyted using the same string that was used to encrypt it.
        """
        ciphertext = self._algorithm.encrypt( self._pad(plaintext) )
        return ciphertext

    def decrypt (self, ciphertext):
        """
        Decrypts! Takes an encrypted binary string as an argument.
        Must be decrypted using the same string as a key that was used to encrypt it.
        """
        return self._trim ( self._algorithm.decrypt(ciphertext) )
