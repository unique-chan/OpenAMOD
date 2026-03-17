class Script:
    def __init__(self, init_comment=''):
        self.script = [init_comment]

    def add(self, *codes):
        for code in codes:
            code = code.strip()
            if code[-1] == ';':
                code = code[:-1]
            self.script.append(code + ';')

    def add_no_col_end(self, *codes):
        for code in codes:
            code = code.strip()
            self.script.append(code)

    def get_script(self):
        return ' \n'.join(self.script)
