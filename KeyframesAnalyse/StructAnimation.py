
from .StructMetaFrame import StructMetaFrame

import cv2
import numpy as np

__all__=['StructMetaFrame']

class StructAnimation:
	'''
		将StructMetaFrame.Opt_AnalyseStruct返回的StructMetaFrame列表数据作进一步处理，
		合成为统一的帧数据(这里的统一同时包括帧大小统一)。
		调用Opt_Merge对多个动画进行进一步的数据统一。
	'''
	class Frame:
		'''
			帧数据，调用Get_Pict直接获取图片数据。
		'''
		percent:float
		matrix:np.ndarray
		pict:np.ndarray
		opacity:float
		def __init__(self,percent:float,pict:np.ndarray,opacity:float,matrix:np.ndarray) -> None:
			self.percent=percent
			self.matrix=matrix
			self.pict=pict
			self.opacity=opacity
		def Opt_UpdateOffset(self,x:float,y:float) -> None:
			'''
				用于调整偏移量以统一图片位置。
				该函数不对外使用
			'''
			self.matrix[0,2]+=x
			self.matrix[1,2]+=y
			# self.matrix=self.matrix.dot(np.array([[1,0,x],[0,1,y],[0,0,1]],dtype=np.float64))
			# self.matrix=self.matrix.dot(np.array([[1,0,x/self.matrix[0][0]],[0,1,y/self.matrix[1][1]],[0,0,1]],dtype=np.float64))
		def Get_Pict(self,size:tuple) -> np.ndarray:
			'''
				获取帧数据
			'''
			pict=cv2.warpAffine(self.pict,self.matrix[:2],[int(val) for val in size])
			pict=pict.astype(np.float64)
			pict[:,:,3]*=self.opacity
			pict=pict.astype(np.uint8)
			return pict
	frameLst:list#Frame列表
	area:list#LTWH
	def __init__(self,StructMetaFrameLst:list,spritePict:np.ndarray,spriteSize:tuple) -> None:
		lstX=[]
		lstY=[]
		diff=4-spritePict.shape[-1]
		if(diff>0):
			channel=cv2.split(spritePict)
			alpha=np.zeros(channel[0].shape,dtype=channel[0].dtype)
			spritePict=cv2.merge(*channel,*[alpha]*diff)
		frameLst=[]
		for frame in StructMetaFrameLst:
			percent=frame.percent
			opacity=frame.opacity
			matrix=frame.matrix
			pos=frame.pos
			pict=spritePict[pos[1]:pos[1]+spriteSize[1],pos[0]:pos[0]+spriteSize[0]]
			frameLst.append(self.Frame(percent,pict,opacity,matrix))
			for pos in ([0,0],[spriteSize[0],0],[0,spriteSize[1]],[spriteSize[0],spriteSize[1]]):
				pos=np.array([*pos,1],dtype=np.float64)
				pos=matrix.dot(pos)
				lstX.append(pos[0])
				lstY.append(pos[1])
		area=[min(lstX),min(lstY),max(lstX),max(lstY)]
		area[2]=area[2]-area[0]+1
		area[3]=area[3]-area[1]+1
		for frame in frameLst:
			# frame.Opt_UpdateOffset(-area[0],-area[1]/2)
			frame.Opt_UpdateOffset(-area[0],-area[1])
		self.frameLst=frameLst
		self.area=area
	def Get_FrameCount(self):
		return len(self.frameLst)
	def Get_Pict(self,index:int):
		return self.frameLst[index].Get_Pict(self.area[2:])
	def Get_Size(self):
		return [int(val) for val in self.area[2:]]
	def Set_Area(self,area:list):
		if(self.area!=list(area)):
			for frame in self.frameLst:
				frame.Opt_UpdateOffset(self.area[0]-area[0],self.area[1]-area[1])
			self.area=area
	@classmethod
	def Opt_Merge(self,*structAnimationLst):
		'''
			调用Opt_Merge对多个动画进行进一步的数据统一，
			该函数会修改所有传入的StructAnimation的内部数据。
		'''
		percent=set()
		lstX=[]
		lstY=[]
		for stA in structAnimationLst:
			percent.union([frame.percent for frame in stA.frameLst])
			area=stA.area
			lstX.append(area[0])
			lstX.append(area[0]+area[2]-1)
			lstY.append(area[1])
			lstY.append(area[1]+area[3]-1)
		area=[min(lstX),min(lstY),max(lstX),max(lstY)]
		area[2]=area[2]-area[0]+1
		area[3]=area[3]-area[1]+1
		count=len(structAnimationLst)
		indices=[0]*count
		for stA in structAnimationLst:
			stA.Set_Area(area)
		for p in sorted(percent):
			for i in range(count):
				stA=structAnimationLst[i]
				index=indices[i]
				frame=stA.frameLst[index]
				if(frame.percent!=p):#插入一帧
					if(index>0):#与前一帧相同数据
						stA.frameLst.insert(0,self.Frame(p,frame.pict,frame.opacity,frame.matrix))
					else:#不应该出现这种情况，但即使出现也无事，直接插空白帧
						stA.frameLst.insert(index-1,self.Frame(p,np.ones((1,1,1,4)*255,dtype=np.int8),0,np.array([[1,0,0],[0,1,0],[0,0,1]],dtype=np.float64)))
				indices[i]+=1
