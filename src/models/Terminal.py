class Terminal:
    def __init__(self,guid,code,name,groupid):
        self.guid = guid
        self.code = code
        self.name = name
        self.groupid = groupid

    def to_dict(self):
        return {
            'guid': self.guid,
            'code': self.code,
            'name': self.name,
            'GroupId': self.groupid
        }