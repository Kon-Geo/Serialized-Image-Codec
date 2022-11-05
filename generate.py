from cv2 import imwrite
from numpy import uint8
from numpy.random import randint
imwrite('random.png', randint(255, size=(2000, 2000, 3), dtype=uint8))