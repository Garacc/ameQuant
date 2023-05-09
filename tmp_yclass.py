import pandas as pd

class yClass:
    def __init__(self, data, info):
        self.data = data
        self.info = info

    def __repr__(self):
        return f"yClass({self.data}, {self.info})"
