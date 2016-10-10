class Correlation:
    def __init__(self):
        items = []

    def addElementContour(self, con1, li):
        if len(li[-1]) >0:
            if li[-1][0] == "new":
                li[len(li) -2].append(con1)
                print "warning added to new array"
        else:
            li[len(li) -1].append(con1)
        return li
