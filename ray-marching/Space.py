import math

class EulerAngle:
    def __init__(self, x:float, y:float, z:float):
        self.x = x
        self.y = y
        self.z = z

class Vector3:
    def __init__(self, x:float, y:float, z:float):
        self.x = x
        self.y = y
        self.z = z

    def Magnitude(self) -> float:
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5

    def Normalized(self):
        magnitude = self.Magnitude()
        return Vector3(self.x / magnitude, self.y / magnitude, self.z / magnitude)

    def __mul__(self, other: float):
        return Vector3(self.x * other, self.y * other, self.z * other)
    
    def __add__(self, other: 'Vector3'):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Vector3'):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __truediv__(self, other: float):
        return Vector3(self.x / other, self.y / other, self.z / other)
    
    def __str__(self) -> str:
        return str((self.x, self.y, self.z))

    def Rotated(self, rotation: EulerAngle):
        x = self.x; y = self.y; z = self.z

        # rotation x
        theta = rotation.x / 180 * math.pi
        xNew = x
        yNew = y * math.cos(theta) - z * math.sin(theta)
        zNew = y * math.sin(theta) + z * math.cos(theta)
        x = xNew; y = yNew; z = zNew

        # rotation y
        theta = rotation.y / 180 * math.pi
        xNew = x * math.cos(theta) + z * math.sin(theta)
        yNew = y
        zNew = -x * math.sin(theta) + z * math.cos(theta)
        x = xNew; y = yNew; z = zNew
        # print(x, y, z)

        # rotation z
        theta = rotation.z / 180 * math.pi
        xNew = x * math.cos(theta) - y * math.sin(theta)
        yNew = x * math.sin(theta) + y * math.cos(theta)
        zNew = z
        # print(xNew, yNew, zNew)
        # print(Vector3(1, 2, 3))
        return Vector3(xNew, yNew, zNew)