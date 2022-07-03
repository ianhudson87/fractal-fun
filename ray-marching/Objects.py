from abc import abstractclassmethod, abstractmethod
from Space import *

class Object:
    objCount = 0

    def __init__(self, center:Vector3):
        Object.objCount += 1
        self.id = Object.objCount
        self.center = center

    @abstractmethod
    def DistanceEstimator(self, fromPos:Vector3) -> float:
        pass

class Sphere(Object):
    def __init__(self, center:Vector3, radius:float):
        super(Sphere, self).__init__(center=center)
        self.radius = radius

    def DistanceEstimator(self, fromPos:Vector3) -> float:
        return (fromPos - self.center).Magnitude() - self.radius

class InfiniteSpheres(Object):
    def __init__(self, center:Vector3, radius:float, modulus:float):
        super(InfiniteSpheres, self).__init__(center=center)
        self.radius = radius
        self.modulus = modulus

    def DistanceEstimator(self, fromPos:Vector3) -> float:
        residualPos = Vector3(fromPos.x % self.modulus, fromPos.y % self.modulus, fromPos.z % self.modulus)
        return (residualPos - self.center).Magnitude() - self.radius

class SierpinskiTetrahedron(Object):
    def __init__(self, vertex1:Vector3, vertex2:Vector3, vertex3:Vector3, vertex4:Vector3, iterations:int):
        self.v1 = vertex1
        self.v2 = vertex2
        self.v3 = vertex3
        self.v4 = vertex4
        self.vertices = [self.v1, self.v2, self.v3, self.v4]
        self.iterations = iterations
        super().__init__(center=(vertex1 + vertex2 + vertex3 + vertex4) / 4)
    
    def DistanceEstimator(self, fromPos: Vector3) -> float:
        # originalPos = fromPos
        # print("get estimate")
        # print(fromPos)
        for _ in range(self.iterations):
            # get closest vertex
            closestVertexDist = 9e9
            closestVertex = None
            for vertex in self.vertices:
                if (fromPos - vertex).Magnitude() < closestVertexDist:
                    closestVertexDist = (fromPos - vertex).Magnitude()
                    closestVertex = vertex
            # closest vertex found
            fromPos = fromPos*2 - closestVertex # has the effect of scaling the shape down by 2 centered at the closest vertex, but leaves the fromPos where it is. (need to divide distances by 2 also, which is done at the end)
            # print(fromPos)
        # print(fromPos.Magnitude() * math.pow(2, -self.iterations))
        return ((fromPos).Magnitude()-2) * math.pow(2, -self.iterations)


