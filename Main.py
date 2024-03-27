
import bs4
import os

from KeyframesAnalyse import *		

from PyQt5.QtWidgets import QApplication,QLabel
from PyQt5.QtGui import QPixmap,QPainter
from PyQt5.QtCore import QTimer,Qt
from XJ.Widgets.XJQ_PictCarousel import XJQ_PictCarousel
from XJ.Functions.CV2ToQPixmap import CV2ToQPixmap
from XJ.Functions.CV2LoadPict import CV2LoadPict

class MainTool:
	'''
		执行顺序：
			__init__ -> Opt_Load -> Opt_Start -> Get_Frames/Opt_Scale/Opt_Save
		以上行为均是单向操作且行为不可撤回，Opt_Load可多次执行，在执行完毕后调用Opt_Start进行图片生成
	'''
	def __init__(self,htmlPath:str) -> None:
		'''
			初始化，加载html文本，分析其中的css数据
		'''
		with open(htmlPath,encoding='utf-8') as f:
			html=f.read()
		soup=bs4.BeautifulSoup(html,'html.parser')
		css=soup.style.string
		# target=soup.find(id='capture')
		self.__lstSTC=StructCSS.Opt_AnalyseCSS(css)
		self.__lstSTA=[]
		self.__lstFrames=[]
	def Opt_Load(self,keyframesName:str,spritePict:str,spriteSize:tuple):
		'''
			加载指定名称的动画以及相关联的图片信息。
			该函数有顺序性(如果多个动画重叠那自然是越新加入的越在上方)，可多次调用
		'''
		spritePict=CV2LoadPict(spritePict)
		for stC in self.__lstSTC:
			if(f'@keyframes {keyframesName}' in stC.name):
				rstFrm=StructMetaFrame.Opt_AnalyseStruct(stC)
				rstAnm=StructAnimation(rstFrm,spritePict,spriteSize)
				self.__lstSTA.append(rstAnm)
				return True
		return False
	def Opt_Start(self):
		'''
			在使用Opt_Load添加完指定的动画后便开始进行图片生成。
			该函数不可多次调用。

			由于cv2那孱弱的图片叠加功能，我移步于Qt的QPainter进行图片操作，
			因此需要先创建QApplication才能调用本函数。
		'''
		StructAnimation.Opt_Merge(*self.__lstSTA)
		stA=self.__lstSTA[0]
		size=stA.Get_Size()
		for i in range(stA.Get_FrameCount()):
			frame=QPixmap(*size)
			frame.fill(Qt.GlobalColor.transparent)
			ptr=QPainter(frame)
			for rstAnm in self.__lstSTA:
				pix=CV2ToQPixmap(rstAnm.Get_Pict(i))
				ptr.drawPixmap(0,0,pix)
			ptr.end()
			self.__lstFrames.append(frame)
	def Opt_Scale(self,scaleX:float=1.0,scaleY:float=1.0):
		'''
			对生成的图片数据进行缩放，
			操作没啥用但还是放着
		'''
		for i in self.__lstFrames:
			pict=self.__lstFrames[i]
			self.__lstFrames[i]=pict.scaled(pict.width()*scaleX,pict.height()*scaleY)
	def Opt_Save(self,dirPath:str):
		'''
			将图片数据导出为{index}.png
		'''
		if(os.path.exists(dirPath)==False):
			os.makedirs(dirPath)
		for i in range(len(self.__lstFrames)):
			self.__lstFrames[i].save(f'dirPath/{i}.png')
	def Get_Frames(self)->list:
		'''
			获取图片数据，为QPixmap列表
		'''
		return self.__lstFrames



if __name__=='__main__':
	htmlPath='./手动处理后的网站，需提取其中的目标动画/LostSoul.html'
	spritePath='./手动处理后的网站，需提取其中的目标动画/LostSoulSprite.png'
	spriteSize=[32,32]
	# classNameLst=['lost_soul_anm_Death1','lost_soul_anm_Death0']
	classNameLst=['lost_soul_anm_FloatDown1','lost_soul_anm_FloatDown0']



	app=QApplication([])

	mt=MainTool(htmlPath)
	for name in classNameLst:
		mt.Opt_Load(name,spritePath,spriteSize)
	mt.Opt_Start()
	pc=XJQ_PictCarousel()
	pc.Set_Frames(mt.Get_Frames())
	pc.resize(400,400)
	pc.Opt_Play()
	pc.show()

	app.exec()



