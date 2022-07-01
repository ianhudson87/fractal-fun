from abc import abstractclassmethod, abstractmethod
import numpy as np
import math
import copy
import numpy as np
import matplotlib.pyplot as plt
import random
# from abc import ABC, abstractmethod

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

    def __mul__(self, other):
        return Vector3(self.x * other, self.y * other, self.z * other)
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def Rotated(self, rotation:EulerAngle):
        x = self.x; y = self.y; z = self.z

        # rotation x
        theta = rotation.x
        xNew = x
        yNew = y * math.cos(theta) - z * math.sin(theta)
        zNew = y * math.sin(theta) + z * math.cos(theta)
        x = xNew; y = yNew; z = zNew

        # rotation y
        theta = rotation.y
        xNew = x * math.cos(theta) + z * math.sin(theta)
        yNew = y
        zNew = -x * math.sin(theta) + z * math.cos(theta)
        x = xNew; y = yNew; z = zNew

        # rotation z
        theta = rotation.z
        xNew = x * math.cos(theta) - y * math.sin(theta)
        yNew = x * math.sin(theta) + y * math.cos(theta)
        zNew = z
        return Vector3(xNew, yNew, zNew)
        
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

class RayMarchResult:
    def __init__(self, collided:bool, hitObj:Object, travelDist:float, stepsTaken:int):
        self.collided = collided
        self.hitObj = hitObj
        self.travelDist = travelDist
        self.stepsTaken = stepsTaken

# class RenderParameters:
#     def __init__(self, ambientOcclusion:float):
#         self.ambientOcclusion = ambientOcclusion # lower is more

class LightingEngine:
    def __init__(self, ambientOcclusionLevel:float):
        self.ambOccLvl = ambientOcclusionLevel # lower is more

    def ApplyAmbientOcclusion(self, currentColor:np.array, marchSteps:int) -> np.array:
        AOPercentage = min(marchSteps, self.ambOccLvl) / self.ambOccLvl
        return AOPercentage*np.array([0,0,0]) + (1-AOPercentage)*currentColor

class RayMarchRenderer:
    def __init__(self, lightingEngine:LightingEngine):
        self.objects = []
        self.lightEng = lightingEngine

    def Render(self):
        imgData = self.GetImageData(192*2, 108*2, horizScreenSize=1.9, vertScreenSize=1, screenDist=1, cameraPos=Vector3(0,0,0), cameraRot=EulerAngle(0,0,0), renderDist=100, positionModulo=5)
        plt.imshow(imgData)
        plt.show()

    def AddObject(self, object:Object):
        self.objects.append(object)

    def GetImageData(self, horizPixels:int, vertPixels:int, horizScreenSize:float, vertScreenSize:float, screenDist:float, cameraPos:Vector3, cameraRot:EulerAngle, renderDist:float, positionModulo:float) -> np.array:
        # screenSize: how many units the screen should be
        # screenDist: how many units away the screen should be from the camera
        # TODO: these 2 things control fov?
        # renderDist: how long ray march should continue on for before stopping

        imgData = np.zeros((vertPixels, horizPixels, 3), dtype=np.uint8)
        
        for row in range(vertPixels):
            if row%10==0:
                print("row" + str(row) + " out of " + str(vertPixels))
            for col in range(horizPixels):
                # get the vector at which we need to travel to head to this pixel from the cameraPos
                screenPercentHoriz = col / horizPixels # what percentage of the way we are along the screen
                screenPercentVert = row / vertPixels
                screenCenterHorizDiff = (screenPercentHoriz - 0.5) * horizScreenSize # horizontal units we are away from the center of the screen. Assuming orientation wrt the plane of the screen (ie no rotation)
                screenCenterVertDiff = (screenPercentVert - 0.5) * vertScreenSize
                screenCenterVectorDiff = Vector3(0, -screenCenterHorizDiff, -screenCenterVertDiff)
                pixelInSpace = (cameraPos + (Vector3(1,0,0)*screenDist) + screenCenterVectorDiff).Rotated(cameraRot) # where the pixel is in space. Assuming camera points towards (1, 0, 0) by default

                # do ray march from camera in the direction towards the pixel
                directionFromCameraToPixel = (pixelInSpace - cameraPos).Normalized() # this is the direction from the camera to the pixel on the screen
                rayMarchResult = self.DoRayMarch(cameraPos, directionFromCameraToPixel, renderDist, 0.01, positionModulo)

                # color the pixel based on the results of the ray march
                imgData[row, col] = self.GetPixelColor(rayMarchResult, renderDist)
        return imgData

    def DoRayMarch(self, startPos:Vector3, direction:Vector3, maxDist:float, collideDistThresh:float, posMod:float) -> RayMarchResult:
        direction = direction.Normalized()
        currentPos = copy.copy(startPos)
        distTraveled = 0
        stepsTaken = 0
        while(distTraveled < maxDist):
            stepsTaken += 1
            if posMod is not None:
                residualPos = Vector3(currentPos.x % posMod, currentPos.y % posMod, currentPos.z % posMod)
            else:
                residualPos = currentPos
            # calculate min distance to an object from (interpreted) current position
            distanceEstimates = [obj.DistanceEstimator(residualPos) for obj in self.objects]
            minDistance = min(distanceEstimates)

            if minDistance < collideDistThresh:
                # collided with an object
                collidedObjIdx = np.argmin(distanceEstimates)
                collidedObj = self.objects[collidedObjIdx]
                return RayMarchResult(collided=True, hitObj=collidedObj, travelDist=distTraveled, stepsTaken=stepsTaken)
            
            else:
                # haven't collided with anything. Travel the min distance (safe distance to not collide)
                currentPos += direction * minDistance
                distTraveled += minDistance
        # went max distance and didn't hit anything
        return RayMarchResult(collided=False, hitObj=None, travelDist=distTraveled, stepsTaken=stepsTaken)

    def GetPixelColor(self, marchResult:RayMarchResult, renderDist:float):
        if not marchResult.collided:
            return np.array([0,0,0])

        np.random.seed(marchResult.hitObj.id + (int)(marchResult.travelDist /5))
        currentColor = np.random.rand((3))*255
        currentColor = self.lightEng.ApplyAmbientOcclusion(currentColor, marchResult.stepsTaken)
        # fogPercentage = hitInfo.travelDist / renderDist # how much of color should be fog
        # fogPercentage = min(marchResult.stepsTaken, 50) / 50
        # objColor = np.array([100, 100, 255])
        # np.random.seed(marchResult.hitObj.id + (int)(marchResult.travelDist /5))
        # objColor = np.random.rand((3))*255
        # fogColor = np.array([20, 0, 30])
        return currentColor


le = LightingEngine(ambientOcclusionLevel=30)
rmr = RayMarchRenderer(lightingEngine=le)
rmr.AddObject(Sphere(center=Vector3(2.5,2.5,2.5), radius=0.5))
rmr.Render()