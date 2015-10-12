import hashlib


class Md5Cracker:

    # def __init__(self, tocrack, template, wildcard):
    #     self.tocrack = tocrack
    #     self.template = template
    #     self.wildcard = wildcard

    def start(self, tocrack, template, wildcard):
        print("Hash to crack:", tocrack)

        res = self.md5_crack(tocrack, template, wildcard)

        if res:
            print("cracking " + tocrack + " gave " + res)
        else:
            print("failed to crack " + tocrack, "| template:", template)
        
        return res

    def md5_crack(self, hexhash, template, wildcard):
        "instantiate template and crack all instatiations"
        # first block recursively instantiates template
        i = 0
        found = False
        while i < len(template):
            if template[i] == wildcard:
                found = True
                char = 32  # start with this char ascii
                while char < 126:
                    c = chr(char)
                    if c != wildcard:  # cannot check wildcard!
                        ntemplate = template[:i] + c + template[i+1:]
                        # print("i: "+str(i)+" ntemplate: "+ntemplate)
                        res = self.md5_crack(hexhash, ntemplate, wildcard)
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


# c = Md5Cracker()
# a = c.start("7815696ecbf1c96e6894b779456d330e", "a??", "?")

