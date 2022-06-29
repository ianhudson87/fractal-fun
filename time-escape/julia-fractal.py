from cmath import cos, sin
from time import time
from xml.etree.ElementTree import PI
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from ComplexCoord import ComplexCoord
import math
import imageio
import time

# timeSteps: number of iterations the transformation is performed on each pixel
# magnitudeThreshold: after all transforms are performed on a pixel, what magnitude must is be below to be drawn
def DrawFractal(horizontalRange, verticalRange, horizontalPixelsPerUnit, verticalPixelsPerUnit, timeSteps, magnitudeThreshold, constant):
    # create matrix
    horizontalPixels = (int)(horizontalPixelsPerUnit * horizontalRange)
    verticalPixels = (int)(verticalPixelsPerUnit * verticalRange)
    data = np.zeros( (verticalPixels,horizontalPixels,3), dtype=np.uint8 )

    print(np.shape(data))

    # go through each pixel and perform the transformation
    for r in range(0, verticalPixels):
        if r%10 == 0:
            print("row" + str(r) + " out of " + str(verticalPixels))
        for c in range(0, horizontalPixels):
            ptc = PixelToCoord(r, c, horizontalRange, verticalRange, horizontalPixels, verticalPixels)
            complexCoord = ComplexCoord(ptc[0], ptc[1])

            try:
                diverges = False
                for i in range(timeSteps):
                    if i == timeSteps - 1:
                        # keep track of divergence speed
                        prevComplexCoord = complexCoord
                    complexCoord = complexCoord * complexCoord + constant

                    if complexCoord.Magnitude() > magnitudeThreshold:
                        # pixel diverges
                        diverges = True
                        break

                # transformations have been done and pixel doesn't diverge
                if diverges:
                    data[r, c] = [0, 0, 0]
                else:
                    # print(complexCoord, prevComplexCoord)
                    speed = (complexCoord - prevComplexCoord).Magnitude()
                    # print(speed)
                    red = max(255 - speed*200, 0)
                    blue = max(255 - speed*200, 0)
                    green = max(255 - speed*200, 0)
                    data[r,c] = [red, blue, green]
            except OverflowError as err:
                data[r, c] = [0, 0, 0]
    return data
    # plt.imshow(data)
    # plt.show()

def PixelToCoord(pixelRow, pixelCol, horizontalRange, verticalRange, horizontalPixels, verticalPixels):
    # find where the pixel is relative to the entire image
    yNormed = -((pixelRow / verticalPixels)*2 - 1)
    xNormed = (pixelCol / horizontalPixels)*2 - 1

    return (xNormed * horizontalRange, yNormed * verticalRange)

# DrawFractal(horizontalRange=1,verticalRange=1.2,
#             horizontalPixelsPerUnit=10000, verticalPixelsPerUnit=10000,
#             timeSteps=30, magnitudeThreshold=3,
#             constant=ComplexCoord(0.2, 0.3))




def ConstantAroundCircle(radiansPerMove):
    gifWriter = imageio.get_writer('./output/juliaCircle1.gif', mode='I')

    currentRadians = 0

    while currentRadians < 2 * math.pi:
        currentCircleCoord = ComplexCoord(math.cos(currentRadians), math.sin(currentRadians))
        # print(currentCircleCoord)
        data = DrawFractal(horizontalRange=1.2,verticalRange=1,
            horizontalPixelsPerUnit=500, verticalPixelsPerUnit=500,
            timeSteps=20, magnitudeThreshold=3,
            constant=currentCircleCoord)

        gifWriter.append_data(data)

        currentRadians += radiansPerMove

    gifWriter.close()

# ConstantAroundCircle(math.pi/50)

data = DrawFractal(
    horizontalRange=1,verticalRange=1.2,
    horizontalPixelsPerUnit=200, verticalPixelsPerUnit=200,
    timeSteps=100, magnitudeThreshold=2,
    constant=ComplexCoord(0.25, -0.0005))
image = Image.fromarray(data)
image.save("./output/" + (str)((int)(time.time())) + ".tiff")
plt.imshow(data)
plt.show()

