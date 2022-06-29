import numpy as np

class Vector3:
    def __init__(self, x:float, y:float, z:float):
        self.x = x
        self.y = y
        self.z = z

    def Normalized(self):
        magnitude = (self.x**2 + self.y**2 + self.z**2) ** 0.5
        return Vector3(self.x / magnitude, self.y / magnitude, self.z / magnitude)

    def __mul__(self, other):
        return Vector3(self.x * other, self.y * other, self.z * other)
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

class Object:
    def __init__(self, center:Vector3):
        self.center = center

class Sphere(Object):
    def __init__(self, center:Vector3, radius:float):
        super(Sphere, self).__init__(center=center)


class RayMarching:
    def __init__(self):
        self.objects = []

    def AddObject(self, object:Object):
        self.objects.append(object)

    def GetImageData(self, horizPixels:int, vertPixels:int, horizScreenSize:float, vertScreenSize:float, screenDist:float, cameraPos:Vector3, cameraDir:Vector3) -> np.array:
        for row in range(vertPixels):
            for col in range(horizPixels):
                pixelInSpace = cameraPos + (cameraDir.Normalized() * screenDist) # where the pixel is in space


    def DoRayMarch(self):
        return np.zeros((1,1))

    def DistanceEstimator():
        pass

rm = RayMarching()
s = Sphere(center=Vector3(0,0,0), radius=1)
rm.AddObject(s)