class Terminal:
    def __init__(self,name,pid,vid):
        self.name = name
        self.pid = pid
        self.vid = vid

    def to_dict(self):
        return {
            'name': self.name,
            'pid': self.pid,
            'vid': self.vid,
        }