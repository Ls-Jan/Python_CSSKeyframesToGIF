
from .StructCSS import StructCSS

import numpy as np

__all__=['StructMetaFrame']
class StructMetaFrame:
	'''
		分析具有@keyframes信息的StructCSS中的动画元数据，需通过函数Opt_AnalyseStruct生成StructMetaFrame对象列表。
		matrix为3*3的变换矩阵，对应transform数据。
	'''
	percent:float
	pos:tuple
	opacity:float
	transform:list
	matrix:np.ndarray
	def __init__(self,percent:float,transform:str,position:str,opacity:str) -> None:
		'''
			本构造函数无实际作用。
			需通过函数Opt_AnalyseStruct生成StructMetaFrame对象列表
		'''
		self.percent=percent
		self.pos=[-eval(pix.strip(' ;')[:-2]) for pix in position.split()]
		self.opacity=eval(opacity)
		self.transform=[info.strip()+')' for info in transform.split(')') if info]

		matrix=np.array([[1,0,0],[0,1,0],[0,0,1]],dtype=np.float64)
		for trans in self.transform:
			if('translateX' in trans):
				matrix=self.__translateX(matrix,trans)
			elif('translateY' in trans):
				matrix=self.__translateY(matrix,trans)
			elif('translate' in trans):
				matrix=self.__translate(matrix,trans)
			elif('scale' in trans):
				matrix=self.__scale(matrix,trans)
		self.matrix=matrix
	@classmethod
	def __scale(self,matrix,order):
		scale=order.split('(')[1][:-1]
		scale=[eval(val.strip()) for val in scale.split(',')]
		if(len(scale)==1):
			scale.append(scale[0])
		return matrix.dot(np.array([[scale[0],0,0],[0,scale[1],0],[0,0,1]],dtype=np.float64))
	@classmethod
	def __translate(self,matrix,order):
		pos=order.split('(')[1][:-1]
		pos=pos.split(',')
		x,y=[eval(val.strip()[:-2]) for val in pos]
		return matrix.dot(np.array([[1,0,x],[0,1,y],[0,0,1]],dtype=np.float64))
	@classmethod
	def __translateX(self,matrix,order):
		pos=order.split('(')[1][:-1]
		return self.__translate(matrix,f'translate({pos},0px)')
	@classmethod
	def __translateY(self,matrix,order):
		pos=order.split('(')[1][:-1]
		return self.__translate(matrix,f'translate(0px,{pos})')
	@staticmethod
	def Opt_AnalyseStruct(struct:StructCSS) -> list:
		'''
			分析具有@keyframes信息的StructCSS中的动画元数据，返回StructMetaFrame对象列表。
		'''
		result=[]
		if('@keyframes' in struct.name):
			for stF in struct.sub:
				percent=eval(stF.name[:-1])
				lst=[info.strip() for info in stF.content.split('\n') if ':' in info]
				record={'transform':'','background-position':(0,0),'opacity':1}
				for info in lst:
					for key in record:
						if(key in info):
							record[key]=info.split(':')[1].strip()
							break
				result.append(StructMetaFrame(percent,record['transform'],record['background-position'],record['opacity']))
		return result
