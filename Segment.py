class Segment:
	def __init__(self, name, features, symbol = None):
		self.name = name
		self.features = features
		if symbol:
			self.symbol = symbol
		else:
			self.symbol = name
			
	def __repr__(self):
		return self.name	#use symbol?
		
	def __str__(self):
		return self.name	