import hashlib


class Md5Cracker:

    def __init__(self, tocrack, template, wildcard):
        self.tocrack = tocrack
        self.template = template
        self.wildcard = wildcard

    def start(self):
        print("Hash to crack:", self.tocrack)

        res = self.md5_crack(self.tocrack, self.template)

        if res:
            print("cracking " + self.tocrack + " gave " + res)
        else:
            print("failed to crack " + self.tocrack)

    def md5_crack(self, hexhash, template):
        "instantiate template and crack all instatiations"
        # first block recursively instantiates template
        i = 0
        found = False
        while i < len(template):
            if template[i] == self.wildcard:
                found = True
                char = 32  # start with this char ascii
                while char < 126:
                    c = chr(char)
                    if c != self.wildcard:  # cannot check wildcard!
                        ntemplate = template[:i] + c + template[i+1:]
                        print("i: "+str(i)+" ntemplate: "+ntemplate)
                        res = self.md5_crack(hexhash, ntemplate)
                        if res:  # stop immediately if cracked
                            return res
                    char += 1
            i += 1
            # instantiation loop done
        if not found:
            # no wildcards found in template: crack
            m = hashlib.md5()
            m.update(template.encode())
            hash = m.hexdigest()
            #print("template: "+template+" hash: "+hash)
            if hash==hexhash:
                return template  # cracked!
        # template contains wildcards
        return None
