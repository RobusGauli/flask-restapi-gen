
class PrimaryKeyNotFound(Exception):
    '''Exception that is raised when there is no primary key in the Model'''
    def __init__(self, val):
        super().__init__(val)
