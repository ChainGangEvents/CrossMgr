
import os
import GetModelInfo

def RaceNameFromPath( p ):
	raceName = os.path.basename( p )
	raceName = os.path.splitext( raceName )[0]
	while raceName.endswith('-'):
		raceName = raceName[:-1]
	raceName = raceName.replace( '-', ' ' )
	raceName = raceName.replace( ' ', '-', 2 )
	return raceName

class PointStructure( object ):
	def __init__( self, name, pointsStr = '' ):
		self.name = name
		if pointsStr:
			self.setStr( pointsStr )
		else:
			self.setOCAOCup()
		
	def __getitem__( self, rank ):
		return self.pointsForPlace.get( int(rank), 0 )
	
	def __len__( self ):
		return len(self.pointsForRace)
	
	def setUCIWorldTour( self ):
		self.pointsForPlace = { 1:100, 2:80, 3:70, 4:60, 5:50, 6:40, 7:30, 8:20, 9:10, 10:4 }
		
	def setOCAOCup( self ):
		self.pointsForPlace = { 1:25, 2:20, 3:16, 4:13, 5:11, 6:10, 7:9, 8:8, 9:7, 10:6, 11:5, 12:4, 13:3, 14:2, 15:1 }
	
	def getStr( self ):
		return ', '.join( str(points) for points in sorted(self.pointsForPlace.values(), reverse=True) )
		
	def setStr( self, s ):
		s = s.replace( ',', ' ' )
		values = set()
		for v in s.split():
			try:
				values.add( int(v) )
			except:
				continue
		self.pointsForPlace = dict( (i+1, v) for i, v in enumerate(sorted(values, reverse=True)) )
		
	def __repr__( self ):
		return '(%s: %s)' % ( self.name, self.getStr() )

class Race( object ):
	excelLink = None
	
	def __init__( self, fname, pointStructure, excelLink = None ):
		self.fname = fname
		self.pointStructure = pointStructure
		self.excelLink = excelLink
		
	def getRaceName( self ):
		if os.path.splitext(self.fname)[1] == '.cmn':
			return RaceNameFromPath( self.fname )
			
		if self.excelLink:
			return u'{}:{}'.format(	os.path.basename(os.path.splitext(self.fname)[0]),
									self.excelLink.sheetName if self.excelLink.sheetName else '' )
		else:
			return RaceNameFromPath( self.fname )
				
	def getFileName( self ):
		if os.path.splitext(self.fname)[1] == '.cmn' or not self.excelLink:
			return self.fname
		return u'{}:{}'.format( self.fname, self.excelLink.sheetName )
		
class SeriesModel( object ):
	DefaultPointStructureName = 'Example'

	def __init__( self ):
		self.name = '<Series Name>'
		self.races = []
		self.pointStructures = [PointStructure(self.DefaultPointStructureName)]
		self.numPlacesTieBreaker = 5
		self.errors = []
		self.changed = False
	
	def setPoints( self, pointsList ):
		oldPointsList = [(p.name, p.name, p.getStr()) for p in self.pointStructures]
		if oldPointsList == pointsList:
			return
			
		self.changed = True
		
		newPointStructures = []
		oldToNewName = {}
		newPS = {}
		for name, oldName, points in pointsList:
			name = name.strip()
			oldName = oldName.strip()
			points = points.strip()
			if not name or name in newPS:
				continue
			ps = PointStructure( name, points )
			oldToNewName[oldName] = name
			newPS[name] = ps
			newPointStructures.append( ps )
			
		if not newPointStructures:
			newPointStructures = [PointStructure(self.DefaultPointStructureName)]
			
		for r in self.races:
			r.pointStructure = newPS.get( oldToNewName.get(r.pointStructure.name, ''), newPointStructures[0] )
			
		self.pointStructures = newPointStructures
	
	def setRaces( self, raceList ):
		oldRaceList = [(r.fname, r.pointStructure.name) for r in self.races]
		if oldRaceList == raceList:
			return
			
		self.changed = True
		
		newRaces = []
		ps = dict( (p.name, p) for p in self.pointStructures )
		for fname, pname in raceList:
			fname = fname.strip()
			pname = pname.strip()
			if not fname:
				continue
			try:
				p = ps[pname]
			except KeyError:
				continue
			newRaces.append( Race(fname, p) )
			
		self.races = newRaces
	
	def setChanged( self, changed = True ):
		self.changed = changed
	
	def addRace( self, name ):
		self.changed = True
		self.removeRace( name )
		race = Race( name, self.pointStructures[0] )
		self.races.append( race )
		
	def removeRace( self, name ):
		raceCount = len(self.races)
		self.races = [r for r in self.races if r.fname != name]
		if raceCount != len(self.races):
			self.changed = True
	
	def extractAllRaceResults( self ):
		raceResults = []
		oldErrors = self.errors
		self.errors = []
		for r in self.races:
			success, ex, results = GetModelInfo.ExtractRaceResults( r )
			if success:
				raceResults.extend( results )
			else:
				self.errors.append( (r, ex) )
		if oldErrors != self.errors:
			self.changed = True
		return raceResults
			
model = SeriesModel()