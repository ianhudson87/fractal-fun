class ComplexCoord:

    def __init__(self, real, img):
        self.real = real
        self.img = img

    def __add__(self, other):
        return ComplexCoord(self.real + other.real, self.img + other.img)

    def __sub__(self, other):
        return ComplexCoord(self.real - other.real, self.img - other.img)

    def __mul__(self, other):
        realPart = self.real * other.real - self.img * other.img
        imaginaryPart = self.real * other.img + self.img * other.real
        return ComplexCoord(realPart, imaginaryPart)

    def Magnitude(self):
        return (self.real**2 + self.img**2)**0.5

    def __str__(self) -> str:
        return str((self.real, self.img))
