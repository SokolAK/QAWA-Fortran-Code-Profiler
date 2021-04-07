class Subroutine():
    def __init__(self, file, name, signature, signature_lines, args, declarations_lines):
        self.file = file
        self.name = name
        self.signature = signature
        self.signature_lines = signature_lines
        self.args = args
        self.declarations_lines = declarations_lines

    def __str__(self):
        return f"{self.file:20s} {self.name:20s}"
