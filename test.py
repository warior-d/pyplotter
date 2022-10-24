class HZ():
    def __init__(self, parent):
        self.main = Main

    def test(self):
        self.main.mainTest(self)


class Main:
    def __init__(self):
        self.hz = HZ(self)

    def mainTest(self):
        print("tst\n")

main = Main()

main.mainTest()
main.hz.test()