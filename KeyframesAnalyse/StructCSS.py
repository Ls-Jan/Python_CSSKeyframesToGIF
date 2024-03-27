

__all__=['StructCSS']

class StructCSS:
	'''
		分析CSS数据，需通过函数Opt_AnalyseCSS生成StructCSS对象列表。
		形如XXX{aaa:{...},bbb:{...}}的样式表数据将被转化为：
		name=XXX,
		content='{aaa:{...},bbb:{...}}',
		sub=[StructCSS('aaa'),StructCSS('bbb')]。

		sub列表存储着花括号嵌套数据(当然，已经处理为StructCSS对象)。
	'''
	name:str
	content:str
	sub:list
	def __init__(self,name:str) -> None:
		'''
			本构造函数无实际作用。
			需通过函数Opt_AnalyseCSS生成StructCSS对象列表
		'''
		self.name=name.strip()
		self.content=''
		self.sub=[]
	def __str__(self) -> str:
		return f'{self.__class__.__name__}{{{self.name},{[str(st) for st in self.sub]}}}'
	@staticmethod
	def Opt_AnalyseCSS(css)->list:
		'''
			分析CSS数据并返回StructCSS对象列表
		'''
		stack=[]
		result=[]
		name=''
		for char in css:
			if(char=='{'):
				st=StructCSS(name)
				if(len(stack)==0):
					result.append(st)
				for stk in stack:
					stk.sub.append(st)
				stack.append(st)
				name=''
			elif(char=='}'):
				st=stack.pop()
				st.content+=char
				name=''
			else:
				name+=char
			for st in stack:
				st.content+=char
		return result
		