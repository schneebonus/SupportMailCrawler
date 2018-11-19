class TLDCheck():
    tld_endings = set()

    def init(self):
        tld_file = open("utils/tld.csv", "r")
        tld_line = (tld_file.read()).split("\n")
        for line in tld_line[1:-1]:
            split_line = line.split(",")
            self.tld_endings.add(split_line[0].replace(".", ""))

    def is_valid_tld(self, email):
        split = email.split(".")
        tld = split[-1]
        return tld in self.tld_endings
