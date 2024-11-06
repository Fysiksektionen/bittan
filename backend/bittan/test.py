
class Ko:
    def __init__(self, s):
        self.s = s

    def change(self, s):
        self.s = s

    def __str__(self):
        return self.s

s1 = Ko("Hej")
s2 = Ko("San")


l1 = [s1, s2]
l2 = [s2, s1]


l1[0] = Ko("boom")



# l1[0].change("boom")

print(l1[0], l1[1])
print(l2[0], l2[1])
