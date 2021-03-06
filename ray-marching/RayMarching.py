from graphviz import render
import numpy as np
import math
import copy
import numpy as np
import matplotlib.pyplot as plt
import random
import os
import time
from PIL import Image
from Objects import *
import os
from concurrent import futures
# from abc import ABC, abstractmethod

class RayMarchResult:
    def __init__(self, collided:bool, hitObj:Object, travelDist:float, stepsTaken:int, minStepSize:float):
        self.collided = collided
        self.hitObj = hitObj
        self.travelDist = travelDist
        self.stepsTaken = stepsTaken
        self.minStepSize = minStepSize

# class RenderParameters:
#     def __init__(self, ambientOcclusion:float):
#         self.ambientOcclusion = ambientOcclusion # lower is more

class LightingEngine:
    def __init__(self, ambientOcclusionLevel: float, glowLevel: float, fogDistance: float):
        self.ambOccLvl = ambientOcclusionLevel # lower is more
        self.glowLvl = glowLevel # higher is more
        self.fogDistance = fogDistance # where fog completely takes over

    def ApplyLightingEffects(self, currentColor: np.array, marchResult: RayMarchResult) -> np.array:
        currentColor = self.ApplyAmbientOcclusion(currentColor, marchResult.stepsTaken)
        # currentColor = self.ApplyGlow(currentColor, marchResult.minStepSize)
        currentColor = self.ApplyFog(currentColor, marchResult.travelDist)
        return currentColor

    def ApplyFog(self, currentColor: np.array, marchDistance: float) -> np.array:
        fogPercentage = min(self.fogDistance, marchDistance) / self.fogDistance
        return fogPercentage*np.array([0,0,0]) + (1-fogPercentage)*currentColor

    def ApplyAmbientOcclusion(self, currentColor:np.array, marchSteps:int) -> np.array:
        AOPercentage = min(marchSteps, self.ambOccLvl) / self.ambOccLvl
        return AOPercentage*np.array([0,0,0]) + (1-AOPercentage)*currentColor

    def ApplyGlow(self, currentColor:np.array, minStepSize):
        glowPercentage = (1 - (min(minStepSize, self.glowLvl) / self.glowLvl))/4
        return glowPercentage*np.array([100, 255, 100]) + (1-glowPercentage)*currentColor

class RenderSettings:
    # screenSize: how many units the screen should be
    # screenDist: how many units away the screen should be from the camera
    # TODO: these 2 things control fov?
    # renderDist: how long ray march should continue on for before stopping
    def __init__(self, horizPixels:int, vertPixels:int, horizScreenSize:float, vertScreenSize:float, screenDist:float, cameraPos:Vector3, cameraRot:EulerAngle, renderDist:float, collideDistThresh:float, useMultithreading:bool):
        self.horizPixels = horizPixels
        self.vertPixels = vertPixels
        self.horizScreenSize = horizScreenSize
        self.vertScreenSize = vertScreenSize
        self.screenDist = screenDist
        self.cameraPos = cameraPos
        self.cameraRot = cameraRot
        self.renderDist = renderDist
        self.collideDistThresh = collideDistThresh
        self.useMultithreading = useMultithreading

class RayMarchRenderer:
    def __init__(self, lightingEngine: LightingEngine, renderSettings: RenderSettings, outFolder:str):
        self.objects = []
        self.lightEng = lightingEngine
        self.settings = renderSettings
        self.outFolder = outFolder

    def Render(self):
        if(self.settings.useMultithreading):
            imgData = self.GetImageDataMultithreaded()
        else:
            imgData = self.GetImageData()
        image = Image.fromarray(imgData)
        image.save(os.path.join(self.outFolder, (str)((int)(time.time())) + ".tiff"))
        plt.imshow(imgData)
        plt.show()

    def AddObject(self, object:Object):
        self.objects.append(object)

    def GetImageData(self) -> np.array:
        s = self.settings
        imgData = np.zeros((s.vertPixels, s.horizPixels, 3), dtype=np.uint8)
        
        for row in range(s.vertPixels):
            if row%10==0:
                print("row" + str(row) + " out of " + str(s.vertPixels))
            for col in range(s.horizPixels):
                imgData[row, col] = self.CalculatePixelData(row, col)[0]
        return imgData

    def GetImageDataMultithreaded(self) -> np.array:
        s = self.settings
        imgData = np.zeros((s.vertPixels, s.horizPixels, 3), dtype=np.uint8)

        with futures.ProcessPoolExecutor() as pool:
            for color, row, col in pool.map(self.CalculatePixelData, [row for row in range(s.vertPixels) for col in range(s.horizPixels)], [col for row in range(s.vertPixels) for col in range(s.horizPixels)]):
                imgData[row, col] = color
                # print("row,col", row, col)
        # collect all the parameters needed for function calls
        # allArgs = [(imgData, row, col) for row in range(s.vertPixels) for col in range(s.horizPixels)]
        
        # self.pool.map(self.PopulatePixelDataWrapped, allArgs)
        print(imgData)
        return imgData

    def CalculatePixelData(self, row: int, col: int):
        s = self.settings
        # get the vector at which we need to travel to head to this pixel from the cameraPos
        screenPercentHoriz = col / s.horizPixels # what percentage of the way we are along the screen
        screenPercentVert = row / s.vertPixels
        screenCenterHorizDiff = (screenPercentHoriz - 0.5) * s.horizScreenSize # horizontal units we are away from the center of the screen. Assuming orientation wrt the plane of the screen (ie no rotation)
        screenCenterVertDiff = (screenPercentVert - 0.5) * s.vertScreenSize
        screenCenterVectorDiff = Vector3(0, -screenCenterHorizDiff, -screenCenterVertDiff).Rotated(s.cameraRot)
        pixelInSpace = (s.cameraPos + (Vector3(1,0,0).Rotated(s.cameraRot)*s.screenDist) + screenCenterVectorDiff) # where the pixel is in space. Assuming camera points towards (1, 0, 0) by default

        # do ray march from camera in the direction towards the pixel
        directionFromCameraToPixel = (pixelInSpace - s.cameraPos).Normalized() # this is the direction from the camera to the pixel on the screen
        rayMarchResult = self.DoRayMarch(s.cameraPos, directionFromCameraToPixel, s.renderDist, s.collideDistThresh)

        # color the pixel based on the results of the ray march
        return self.GetPixelColor(rayMarchResult, s.renderDist), row, col

    def DoRayMarch(self, startPos:Vector3, direction:Vector3, maxDist:float, collideDistThresh:float) -> RayMarchResult:
        # print("new ray march")
        direction = direction.Normalized()
        currentPos = copy.copy(startPos)
        distTraveled = 0
        stepsTaken = 0
        minStepSize = 9e9 # smallest step size taken in the ray march
        while(distTraveled < maxDist):
            stepsTaken += 1
            distanceEstimates = [obj.DistanceEstimator(currentPos) for obj in self.objects]
            if len(distanceEstimates) > 0:
                travelDistance = min(distanceEstimates) # distance that we can safely travel
            else:
                travelDistance = 9e9
            
            minStepSize = min(minStepSize, travelDistance) # keep track of min step size during this ray march

            if travelDistance < collideDistThresh:
                # collided with an object
                # print("hit")
                collidedObjIdx = np.argmin(distanceEstimates)
                collidedObj = self.objects[collidedObjIdx]
                return RayMarchResult(collided=True, hitObj=collidedObj, travelDist=distTraveled, stepsTaken=stepsTaken, minStepSize=minStepSize)
            
            else:
                # haven't collided with anything. Travel the min distance (safe distance to not collide)
                currentPos += direction * travelDistance
                distTraveled += travelDistance
        # print("minstepsize from ray march", minStepSize)
        # went max distance and didn't hit anything
        return RayMarchResult(collided=False, hitObj=None, travelDist=distTraveled, stepsTaken=stepsTaken, minStepSize=minStepSize)

    def GetPixelColor(self, marchResult:RayMarchResult, renderDist:float):
        if not marchResult.collided:
            return np.array([0,0,0])

        np.random.seed(marchResult.hitObj.id + (int)(marchResult.travelDist /5))
        # currentColor = np.random.rand((3))*255
        currentColor = np.array([30, 200, 30])
        currentColor = self.lightEng.ApplyLightingEffects(currentColor, marchResult)
        return currentColor

if __name__ == '__main__':  
    le = LightingEngine(ambientOcclusionLevel=50, glowLevel=1e-20, fogDistance=8)
    rs = RenderSettings(horizPixels=70*2, vertPixels=100*2, horizScreenSize=0.7, vertScreenSize=1, screenDist=1,
                        cameraPos=Vector3(3, -1.5, 1.3), cameraRot=EulerAngle(0,15,138),
                        renderDist=8, collideDistThresh=1e-3,
                        useMultithreading=False)
    rmr = RayMarchRenderer(lightingEngine=le, renderSettings=rs, outFolder="./output")
    # rmr.AddObject(Sphere(center=Vector3(0,0,0), radius=0.5))
    # rmr.AddObject(InfiniteSpheres(center=Vector3(2.5,2.5,2.5), radius=0.5, modulus=5))
    # rmr.AddObject(SierpinskiTetrahedron(Vector3(1,1,1), Vector3(-1,-1,1), Vector3(1,-1,-1), Vector3(-1,1,-1), 8))
    rmr.AddObject(SierpinskiTetrahedron(Vector3(1,1/(math.sqrt(3)),math.sqrt(3)), Vector3(1,math.sqrt(3),0), Vector3(2,0,0), Vector3(0,0,0), 10))
    rmr.Render()