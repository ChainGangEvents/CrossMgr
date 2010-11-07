import Model
import datetime
import wx
import os
import re
import sys
import wx.grid		as gridlib
try:
	from win32com.shell import shell, shellcon
except ImportError:
	pass

try:
	import winsound
	def PlayConfirmSound():
		# winsound.PlaySound( "*", winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.MB_ICONASTERISK )
		pass
except ImportError:
	def PlayConfirmSound():
		pass

def MessageOK( parent, message, title = '', iconMask = 0):
	dlg = wx.MessageDialog(parent, message, title, wx.OK | iconMask)
	dlg.ShowModal()
	dlg.Destroy()
	return True
	
def MessageOKCancel( parent, message, title = '', iconMask = 0):
	dlg = wx.MessageDialog(parent, message, title, wx.OK | wx.CANCEL | iconMask )
	response = dlg.ShowModal()
	dlg.Destroy()
	return True if response == wx.ID_OK else False
	
def SetValue( st, value ):
	if st.GetValue() != value:
		st.SetValue( value )

def SetLabel( st, label ):
	if st.GetLabel() != label:
		st.SetLabel( label )

def MakeGridReadOnly( grid ):
	attr = gridlib.GridCellAttr()
	attr.SetReadOnly()
	for c in xrange(grid.GetNumberCols()):
		grid.SetColAttr( c, attr )

def SwapGridRows( grid, r, rTarget ):
	if r != rTarget and 0 <= r < grid.GetNumberRows() and 0 <= rTarget < grid.GetNumberRows():
		for c in xrange(grid.GetNumberCols()):
			vSave = grid.GetCellValue( rTarget, c )
			grid.SetCellValue( rTarget, c, grid.GetCellValue(r,c) )
			grid.SetCellValue( r, c, vSave )
		
def AdjustGridSize( grid, rowsRequired = None, colsRequired = None ):
	# print 'AdjustGridSize: rowsRequired=', rowsRequired, ' colsRequired=', colsRequired

	if rowsRequired is not None:
		rowsRequired = int(rowsRequired)
		d = grid.GetNumberRows() - rowsRequired
		if d > 0:
			grid.DeleteRows( rowsRequired, d )
		elif d < 0:
			grid.AppendRows( -d )

	if colsRequired is not None:
		colsRequired = int(colsRequired)
		d = grid.GetNumberCols() - colsRequired
		if d > 0:
			grid.DeleteCols( colsRequired, d )
		elif d < 0:
			grid.AppendCols( -d )

def formatTime( secs ):
	if secs is None:
		secs = 0
	secs = int(secs + 0.5)
	hours = int(secs / (60*60));
	minutes = int( (secs / 60) % 60 )
	secs = secs % 60
	if hours > 0:
		return "%d:%02d:%02d" % (hours, minutes, secs)
	else:
		return "%02d:%02d" % (minutes, secs)

def formatDate( date ):
	y, m, d = date.split('-')
	d = datetime.date( int(y,10), int(m,10), int(d,10) )
	return d.strftime( '%B %d, %Y' )
		
def StrToSeconds( str = '' ):
	secs = 0
	for f in str.split(':'):
		secs = secs * 60 + int(f, 10)
	return secs
	
def SecondsToStr( secs = 0 ):
	secs = int(secs+0.5)
	return '%02d:%02d:%02d' % (secs / (60*60), (secs / 60)%60, secs % 60)

def SecondsToMMSS( secs = 0 ):
	secs - int(secs+0.5)
	return '%02d:%02d' % ((secs / 60)%60, secs % 60)
	
def getHomeDir():
	try:
		homedir = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
		homedir = os.path.join( homedir, 'CrossMgr' )
		if not os.path.exists(homedir):
			os.mkdir( homedir )
	except:
		homedir = os.path.expanduser('~')
	return homedir

#------------------------------------------------------------------------
try:
	dirName = os.path.dirname(os.path.abspath(__file__))
except:
	dirName = os.path.dirname(os.path.abspath(sys.argv[0]))

if os.path.basename(dirName) == 'library.zip':
	dirName = os.path.dirname(dirName)
imageFolder = os.path.join(dirName, 'images')

def getDirName():		return dirName
def getImageFolder():	return imageFolder
#------------------------------------------------------------------------

reSpace = re.compile(r'\s')
def approximateMatch( s1, s2 ):
	s1 = reSpace.sub( '', s1 ).lower()
	s2 = reSpace.sub( '', s2 ).lower()
	if s1.startswith(s2) or s2.startswith(s1):
		return 1.1
	return len(set(s1) & set(s2)) / float(len(s1) + len(s2))
	
#------------------------------------------------------------------------
mainWin = None
def setMainWin( mw ):
	global mainWin
	mainWin = mw
	
def getMainWin():
	return mainWin

def refresh():
	if mainWin is not None:
		mainWin.refresh()

def refreshForecastHistory():
	if mainWin is not None:
		mainWin.forecastHistory.refresh()

def writeRace():
	if mainWin is not None:
		mainWin.writeRace()
	
def isMainWin():
	return mainWin is not None
