#!/usr/bin/env python
import mandelbruh
from mandelbruh.object import *
from mandelbruh.fold import *

from mandelbruh.coloring import *
from mandelbruh.geo import *
from mandelbruh.shader import Shader

#----------------------------------------------
#            Fractal objects
#----------------------------------------------
def infinite_spheres():
	obj = Object()
	obj.add(FoldRepeatX(2.0))
	obj.add(FoldRepeatY(2.0))
	obj.add(FoldRepeatZ(2.0))
	obj.add(Sphere(0.5, (1.0, 1.0, 1.0), color=(0.9,0.9,0.5)))
	return obj

def butterweed_hills():
	obj = Object()
	obj.add(OrbitInitZero())
	for _ in range(30):
		obj.add(FoldAbs())
		obj.add(FoldScaleTranslate(1.5, (-1.0,-0.5,-0.2)))
		obj.add(OrbitSum((0.5, 0.03, 0.0)))
		obj.add(FoldRotateX(3.61))
		obj.add(FoldRotateY(2.03))
	obj.add(Sphere(1.0, color='orbit'))
	return obj

def mandelbox():
	obj = Object()
	obj.add(OrbitInitInf())
	for _ in range(16):
		obj.add(FoldBox(1.0))
		obj.add(FoldSphere(0.5, 1.0))
		obj.add(FoldScaleOrigin(2.0))
		obj.add(OrbitMinAbs(1.0))
	obj.add(Box(6.0, color='orbit'))
	return obj

def mausoleum():
	obj = Object()
	obj.add(OrbitInitZero())
	for _ in range(8):
		obj.add(FoldBox(0.34))
		obj.add(FoldMenger())
		obj.add(FoldScaleTranslate(3.28, (-5.27,-0.34,0.0)))
		obj.add(FoldRotateX(math.pi/2))
		obj.add(OrbitMax((0.42,0.38,0.19)))
	obj.add(Box(2.0, color='orbit'))
	return obj

def menger():
	obj = Object()
	for _ in range(8):
		obj.add(FoldAbs())
		obj.add(FoldMenger())
		obj.add(FoldScaleTranslate(3.0, (-2,-2,0)))
		obj.add(FoldPlane((0,0,-1), -1))
	obj.add(Box(2.0, color=(.2,.5,1)))
	return obj

def tree_planet():
	obj = Object()
	obj.add(OrbitInitInf())
	for _ in range(30):
		obj.add(FoldRotateY(0.44))
		obj.add(FoldAbs())
		obj.add(FoldMenger())
		obj.add(OrbitMinAbs((0.24,2.28,7.6)))
		obj.add(FoldScaleTranslate(1.3, (-2,-4.8,0)))
		obj.add(FoldPlane((0,0,-1), 0))
	obj.add(Box(4.8, color='orbit'))
	return obj

def sierpinski_tetrahedron():
	obj = Object()
	obj.add(OrbitInitZero())
	for _ in range(9):
		obj.add(FoldSierpinski())
		obj.add(FoldScaleTranslate(2, -1))
	obj.add(Tetrahedron(color=(0.8,0.8,0.5)))
	return obj

def snow_stadium():
	obj = Object()
	obj.add(OrbitInitInf())
	for _ in range(30):
		obj.add(FoldRotateY(3.33))
		obj.add(FoldSierpinski())
		obj.add(FoldRotateX(0.15))
		obj.add(FoldMenger())
		obj.add(FoldScaleTranslate(1.57, (-6.61, -4.0, -2.42)))
		obj.add(OrbitMinAbs(1.0))
	obj.add(Box(4.8, color='orbit'))
	return obj

def test_fractal():
	obj = Object()
	obj.add(OrbitInitInf())
	for _ in range(20):
		obj.add(FoldSierpinski())
		obj.add(FoldMenger())
		obj.add(FoldRotateY(math.pi/2))
		obj.add(FoldAbs())
		obj.add(FoldRotateZ('0'))
		obj.add(FoldScaleTranslate(1.89, (-7.10, 0.396, -6.29)))
		obj.add(OrbitMinAbs((1,1,1)))
	obj.add(Box(6.0, color='orbit'))
	return obj