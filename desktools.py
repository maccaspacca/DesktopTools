import wx
import wx.html
import wx.lib.agw.hyperlink as hl
import wx.lib.plot as plot
import time
import re
from datetime import datetime
import os
import sys
import ticons
import hashlib
import base64
import pyqrcode
import logging
import requests
import json
import  wx.lib.newevent
import urllib
from io import BytesIO
import webbrowser

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA

global myaddress

def ask(parent, message='', title='', default_value = ''):
    dlg = wx.TextEntryDialog(parent, message, title, default_value)
    dlg.ShowModal()
    result = dlg.GetValue()
    dlg.Destroy()
    return result

# load config
try:
	
	with open('tools.ini') as ini:
		lines = [line.rstrip('\n') for line in ini]
	for line in lines:
		if "host=" in line:
			host = str(line.split('=')[1])
		if "port=" in line:
			port = str(line.split('=')[1])
		if "myaddress=" in line:
			myaddress = str(line.split('=')[1])
		if "limit=" in line:
			x_limit = str(line.split('=')[1])
		if "diffhist=" in line:
			diff_hist = str(line.split('=')[1])
			
	ini.close()

except Exception as e:

	setme = wx.App()
	 
	frame = wx.Frame(None, -1, 'Setup')
	frame.SetSize(0,0,200,50)
	 
	# Create text inputs
	host = ask(frame, message = 'Enter an explorer hostname', title = 'Bismuth Tools Setup', default_value = 'bismuth.online')
	port = ask(frame, message = 'Enter explorer web port', title = 'Bismuth Tools Setup', default_value = '80')
	myaddress = ask(frame, message = 'Enter your Bismuth address', title = 'Bismuth Tools Setup', default_value = '')
	x_limit = ask(frame, message = 'Enter rich and miner list limit', title = 'Bismuth Tools Setup', default_value = '250')
	diff_hist = ask(frame, message = 'Enter number of blocks in diff history', title = 'Bismuth Tools Setup', default_value = '2880')
	frame.Destroy()
	setme.Destroy()
	
	f = open('tools.ini','w')
	f.write('host={}\n'.format(host))
	f.write('port={}\n'.format(port))
	f.write('myaddress={}\n'.format(myaddress))
	f.write('limit={}\n'.format(x_limit))
	f.write('diffhist={}\n'.format(diff_hist))
	f.close()

# load config

logging.basicConfig(level=logging.INFO, 
                    filename='tools.log', # log to this file
                    format='%(asctime)s %(message)s') # include timestamp

logging.info("logging initiated")

try:
	explorer_address = "{}:{}".format(host,port)
except Exception as e:
	explorer_address = "localhost:8080"
	
(UpdateStatusEvent, EVT_UPDATE_STATUSBAR) = wx.lib.newevent.NewEvent()

def get_json_info(param1,param2):

	try:

		r = requests.get('http://{}/api/{}/{}'.format(explorer_address,param1,param2))
		x = r.text
		y = json.loads(x)
		#print(y)
		return y
	
	except requests.exceptions.RequestException as e:
		print(e)
		return False
		
try:
	s_get = get_json_info("toolsaddress","toolsaddress")
	s_addy = s_get[0]['toolsaddress']
except:
	s_addy = "35e17f440d05cead33cd6793e7864df34edec48de56da265babf1f97" # hard coded sponsor address

a_txt = "<table>"
a_txt = a_txt + "<tr><td align='right' bgcolor='#DAF7A6'><b>Version:</b></td><td bgcolor='#D0F7C3'>2.00</td></tr>"
a_txt = a_txt + "<tr><td align='right' bgcolor='#DAF7A6'><b>Copyright:</b></td><td bgcolor='#D0F7C3'>Maccaspacca 2017, Hclivess 2016 to 2017</td></tr>"
a_txt = a_txt + "<tr><td align='right' bgcolor='#DAF7A6'><b>Date Published:</b></td><td bgcolor='#D0F7C3'>3rd December 2017</td></tr>"
a_txt = a_txt + "<tr><td align='right' bgcolor='#DAF7A6'><b>License:</b></td><td bgcolor='#D0F7C3'>GPL-3.0</td></tr>"
a_txt = a_txt + "</table>"

w_txt = "<table>"
w_txt = w_txt + "<tr><td bgcolor='#D0F7C3'>1. Click on a transaction in the list to get more information.</td></tr>"
w_txt = w_txt + "<tr><td bgcolor='#D0F7C3'>2. Information refreshes every 5 minutes.</td></tr>"
w_txt = w_txt + "</table>"

l_txt = "<table>"
l_txt = l_txt + "<tr><td bgcolor='#D0F7C3'>1. Input a block number, wallet address or hash into the text box.</td></tr>"
l_txt = l_txt + "<tr><td bgcolor='#D0F7C3'>2. Press enter or click submit.</td></tr>"
l_txt = l_txt + "<tr><td bgcolor='#D0F7C3'>3. Click on a transaction to see more detail.</td></tr>"
l_txt = l_txt + "</table>"

m_txt = "<table>"
m_txt = m_txt + "<tr><td bgcolor='#D0F7C3'>1. Click on the Richlist tab for a list of the top {} wallets.</td></tr>".format(x_limit)
m_txt = m_txt + "<tr><td bgcolor='#D0F7C3'>2. Click on an entry to see more detail.</td></tr>"
m_txt = m_txt + "<tr><td bgcolor='#D0F7C3'>3. Click 'Refresh List' for an update or wait 10 mins for auto-refresh</td></tr>"
m_txt = m_txt + "</table>"

s_txt = "<table>"
s_txt = s_txt + "<tr><td bgcolor='#D0F7C3'>1. Click on the Miners tab for a list of the top {} miners.</td></tr>".format(x_limit)
s_txt = s_txt + "<tr><td bgcolor='#D0F7C3'>2. Click on an entry to see more detail.</td></tr>"
s_txt = s_txt + "<tr><td bgcolor='#D0F7C3'>3. Click 'Refresh List' for an update or wait 10 mins for auto-refresh</td></tr>"
s_txt = s_txt + "</table>"

t_txt = "<table>"
t_txt = t_txt + "<tr><td bgcolor='#D0F7C3'>To sponsor and have your weblink and logo appear on the main page,</td></tr>"
t_txt = t_txt + "<tr><td bgcolor='#D0F7C3'>send at least 1 Bismuth to: {}</td></tr>".format(s_addy)
t_txt = t_txt + "<tr><td bgcolor='#D0F7C3'>The current rate is 14400 blocks per Bismuth sent</td></tr>"
t_txt = t_txt + "<tr><td bgcolor='#D0F7C3'>When you send your payment include the openfield text: sponsor=your_url</td></tr>"
t_txt = t_txt + "<tr><td bgcolor='#D0F7C3'>When desktop tools is opened it will choose a valid sponsor at random</td></tr>"
t_txt = t_txt + "<tr><td bgcolor='#D0F7C3'>Then it will read the Opengraph properties: title, url, image and site_name to display its information</td></tr>"
t_txt = t_txt + "<tr><td bgcolor='#D0F7C3'>Please make sure your site has Opengraph information in it's header</td></tr>"
t_txt = t_txt + "<tr><td bgcolor='#D0F7C3'>See http://ogp.me/ for more information on Opengraph</td></tr>"
t_txt = t_txt + "</table>"

def updatestatus(newstatus,newplace):
	evt = UpdateStatusEvent(msg = newstatus, st_id = int(newplace))
	wx.PostEvent(statusbar,evt)
	
def test(testString):

	if (re.search('[abcdef]',testString)):
		if len(testString) == 56:
			test_result = "adhash"
		else:
			test_result = None
	elif testString.isdigit() == True:
		test_result = "block"
		if testString == "0":
			test_result = None
	else:
		test_result = None
		
	return test_result
	
if not get_json_info("stats","circulation"):
	
	setme = wx.App()
	wx.MessageBox("Unable to connect to the explorer at {}".format(explorer_address), "Not Connected !!", wx.OK|wx.ICON_INFORMATION)
	setme.Destroy()
	sys.exit("connection error")
	
def bgetvars(myaddress):
	
	m_info = get_json_info("address","{}".format(myaddress))

	global addressis
	addressis = "<table>"
	addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Address:</b></td><td bgcolor='#D0F7C3'>{}</td></tr>".format(str(m_info['address']))
	addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Balance:</b></td><td bgcolor='#D0F7C3'>{}</td></tr>".format(str(m_info['balance']))
	addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Credits:</b></td><td bgcolor='#D0F7C3'>{}</td></tr>".format(str(m_info['credits']))
	addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Rewards:</b></td><td bgcolor='#D0F7C3'>{}</td></tr>".format(str(m_info['rewards']))
	addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Debits:</b></td><td bgcolor='#D0F7C3'>{}</td></tr>".format(str(m_info['debits']))
	addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Fees:</b></td><td bgcolor='#D0F7C3'>{}</td></tr>".format(str(m_info['fees']))
	addressis = addressis + "</table>"
	
	return True
	
def tgetvars(myblock,myamount,mytitle):

	m_info = get_json_info("transaction","{}={}".format(myblock,myamount))

	global transis
	transis = []
	tempsis = "<table>"
	tempsis = tempsis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Block:</b></td><td bgcolor='#D0F7C3'>" + str(m_info['block']) + "</td></tr>"
	tempsis = tempsis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Timestamp:</b></td><td bgcolor='#D0F7C3'>" + str(time.strftime("%d/%m/%Y at %H:%M:%S", time.localtime(float(m_info['timestamp'])))) + "</td></tr>"
	tempsis = tempsis + "<tr><td align='right' bgcolor='#DAF7A6'><b>From:</b></td><td bgcolor='#D0F7C3'>" + str(m_info['from']) + "</td></tr>"
	tempsis = tempsis + "<tr><td align='right' bgcolor='#DAF7A6'><b>To:</b></td><td bgcolor='#D0F7C3'>" + str(m_info['to']) + "</td></tr>"
	tempsis = tempsis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Amount:</b></td><td bgcolor='#D0F7C3'>" + str(m_info['amount']) + "</td></tr>"
	tempsis = tempsis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Block Hash:</b></td><td bgcolor='#D0F7C3'>" + str(m_info['hash']) + "</td></tr>"
	tempsis = tempsis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Fee:</b></td><td bgcolor='#D0F7C3'>" + str(m_info['fee']) + "</td></tr>"
	tempsis = tempsis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Reward:</b></td><td bgcolor='#D0F7C3'>" + str(m_info['reward']) + "</td></tr>"
	if float(m_info['reward']) != 0:
		tempsis = tempsis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Nonce:</b></td><td bgcolor='#D0F7C3'>" + str(m_info['openfield']) + "</td></tr>"
	tempsis = tempsis + "</table>"
	
	transis.append(tempsis)
	transis.append(mytitle)
	
	return True

	
class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(1,1)):
        wx.html.HtmlWindow.__init__(self,parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
      
class AboutBoxR(wx.Dialog):
	def __init__(self):
		wx.Dialog.__init__(self, None, -1, "Richlist | Address Details",
			style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|
				wx.TAB_TRAVERSAL)
		hwin = HtmlWindow(self, -1, size=(560,260))
		aboutText = '<p style="color:#08750A";>{}</p>'.format(addressis)
		hwin.SetPage(aboutText)
		btn = hwin.FindWindowById(wx.ID_OK)
		irep = hwin.GetInternalRepresentation()
		hwin.SetSize((irep.GetWidth()+40, irep.GetHeight()+10))
		self.SetClientSize(hwin.GetSize())
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

#---------------------------------------------------------------------------

class AboutBoxT(wx.Dialog):
	def __init__(self):
		wx.Dialog.__init__(self, None, -1, transis[1],
			style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|
				wx.TAB_TRAVERSAL)
		hwin = HtmlWindow(self, -1, size=(560,260))
		aboutText = '<p style="color:#08750A";>{}</p>'.format(transis[0])
		hwin.SetPage(aboutText)
		btn = hwin.FindWindowById(wx.ID_OK)
		irep = hwin.GetInternalRepresentation()
		hwin.SetSize((irep.GetWidth()+40, irep.GetHeight()+10))
		self.SetClientSize(hwin.GetSize())
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

class AboutBox(wx.Dialog):
	def __init__(self):
		wx.Dialog.__init__(self, None, -1, thistitle,
			style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|
				wx.TAB_TRAVERSAL)
		hwin = HtmlWindow(self, -1, size=(500,300))
		if thisid == 101:
			aboutText = '<p style="color:#08750A">{}</p>'.format(w_txt)
		elif thisid == 102:
			aboutText = '<p style="color:#08750A">{}</p>'.format(a_txt)
		elif thisid == 103:
			aboutText = '<p style="color:#08750A">{}</p>'.format(l_txt)
		elif thisid == 104:
			aboutText = '<p style="color:#08750A">{}</p>'.format(m_txt)
		elif thisid == 105:
			aboutText = '<p style="color:#08750A">{}</p>'.format(s_txt)
		elif thisid == 106:
			aboutText = '<p style="color:#08750A">{}</p>'.format(t_txt)
		hwin.SetPage(aboutText)
		irep = hwin.GetInternalRepresentation()
		hwin.SetSize((irep.GetWidth()+10, irep.GetHeight()+10))
		self.SetClientSize(hwin.GetSize())
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

class PlotCanvasExample(plot.PlotCanvas):
	def __init__(self, parent, id, size):
		''' Initialization routine for the this panel.'''
		plot.PlotCanvas.__init__(self, parent, id, style=wx.BORDER_NONE, size=(1000,700))
		
		diff_raw = get_json_info("diffhist",diff_hist)
		diff_b = diff_raw[0]
		diff_d = diff_raw[1]
		
		max_d = max(diff_d)
		min_d = min(diff_d)
		d_inc = (max_d - min_d)/len(diff_b)
		d_min = min_d - (d_inc * 10)
		d_max = max_d + (d_inc * 10)
		b_min = diff_b[0] - 1
		b_max = diff_b[-1] + 1
	
		self.data = list(zip(diff_b,diff_d))

		line = plot.PolyLine(self.data, legend='', colour='red', width=1)
		gc = plot.PlotGraphics([line], 'Difficulty History (last {} blocks)'.format(str(diff_hist)), 'Block Height', 'Difficulty')
		self.Draw(gc, xAxis=(b_min,b_max), yAxis=(d_min,d_max))

class MyGraph(wx.Frame):
	def __init__(self, parent, id ,size):
		wx.Frame.__init__(self, parent, id, title="Bismuth Difficulty (Tools Desktop Edition)", pos=(50,50), size=(1000,700))
		
		loc = ticons.bismuthicon.GetIcon()
		self.SetIcon(loc)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.canvas = PlotCanvasExample(self, 0, size)
		sizer.Add(self.canvas, 1, wx.EXPAND, 0)
		self.SetSizer(sizer)
		self.Layout()

#----------------------------------------------------------------------------

class PageOne(wx.Window):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, style = wx.NO_BORDER)

		box1 = wx.BoxSizer(wx.VERTICAL)
		
		topbox1 = wx.BoxSizer(wx.HORIZONTAL) # logo
		
		t = wx.StaticText(self, -1, "Welcome to Bismuth Tools")
		self.SetBackgroundColour("#FFFFFF")
		t.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		t.SetForegroundColour("#444995")
		t.SetSize(t.GetBestSize())
		topbox1.Add(t, 0, wx.ALL|wx.CENTER, 10)
				
		logo = ticons.bismuthlogo.GetBitmap()
		self.image1 = wx.StaticBitmap(self, -1, logo)
		topbox1.Add(self.image1, 0, wx.ALL|wx.RIGHT, 10)
		
		box1.Add(topbox1, 0, wx.ALL|wx.CENTER, 10)
		
		i = wx.StaticText(self, -1, "Please choose your tool from the tabs above")
		i.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
		i.SetForegroundColour("#444995")
		i.SetSize(i.GetBestSize())
		box1.Add(i, 0, wx.ALL|wx.CENTER, 5)

		ins1 = wx.StaticText(self, -1, "Use the menu bar above for tools and sponsorship help")
		ins1.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
		ins1.SetForegroundColour("#444995")
		ins1.SetSize(ins1.GetBestSize())
		box1.Add(ins1, 0, wx.ALL|wx.CENTER, 5)

		ins2 = wx.StaticText(self, -1, "Click anywhere in the statusbar below for diffculty information")
		ins2.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
		ins2.SetForegroundColour("#444995")
		ins2.SetSize(ins2.GetBestSize())
		box1.Add(ins2, 0, wx.ALL|wx.CENTER, 5)
		
		try:
			#s_get = get_json_info("toolsaddress","toolsaddress")
			#s_addy = s_get[0]['toolsaddress']
			s = get_json_info("getsponsor",s_addy)
		except:
			s = [{'image': 'https://i1.wp.com/bismuth.cz/wp-content/uploads/2017/03/cropped-mesh2-2.png', 'description': 'In the truly free world, there are no limits', 'sitename': 'Bismuth', 'title': 'Bismuth', 'url': 'http://bismuth.cz/'}]
			# hard code default sponsor
		if not s:
			pass

		else:
		
			s_title = s[0]['title']
			s_desc = s[0]['description']
			self.s_url = s[0]['url']
			s_image = s[0]['image']
			s_sitename = s[0]['sitename']
			
			s = wx.StaticText(self, -1, "")
			s.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
			s.SetForegroundColour("#444995")
			s.SetSize(s.GetBestSize())
			box1.Add(s, 0, wx.ALL|wx.CENTER, 40)

			v = wx.StaticText(self, -1, "Sponsored by:")
			v.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
			v.SetForegroundColour("#444995")
			v.SetSize(v.GetBestSize())
			box1.Add(v, 0, wx.ALL|wx.CENTER, 10)
			
			t = wx.StaticText(self, -1, s_title)
			t.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
			t.SetForegroundColour(wx.BLACK)
			t.SetSize(t.GetBestSize())
			t.Bind(wx.EVT_LEFT_DOWN, self.onClick)
			box1.Add(t, 0, wx.ALL|wx.CENTER, 10)

			buf = urllib.request.urlopen(s_image).read()
			sbuf = BytesIO(buf)
			Image = wx.Image(sbuf)
			Image = Image.Scale(100, 100, wx.IMAGE_QUALITY_HIGH)
			Image = Image.ConvertToBitmap()
			im = wx.StaticBitmap(self, -1, Image)
			im.Bind(wx.EVT_LEFT_DOWN, self.onClick)
			box1.Add(im, 0, wx.EXPAND|wx.ALL|wx.CENTER, 5)
			
			u = wx.StaticText(self, -1, s_desc[:60])
			u.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
			u.SetForegroundColour(wx.BLACK)
			u.SetSize(u.GetBestSize())
			u.Bind(wx.EVT_LEFT_DOWN, self.onClick)
			box1.Add(u, 0, wx.ALL|wx.CENTER, 10)

		self.SetSizer(box1)
		self.Layout()
		
	def onClick(self, event):
		""""""
		webbrowser.open(self.s_url)
		
class PageTwo(wx.Window):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, style = wx.NO_BORDER)
		
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.update, self.timer)
		
		self.SetBackgroundColour("#FFFFFF")
		
		if not os.path.exists('pubkey.der'):
			self.myaddress = myaddress
			self.my_state = 'Not running in Bismuth Folder'
			self.my_color = wx.BLUE
		else:
			# import keys
			if not os.path.exists('privkey_encrypted.der'):
				with open('privkey.der') as priv:
					key = RSA.importKey(priv.read())
				private_key_readable = str(key.exportKey())
				priv.close()
				#public_key = key.publickey()
				encrypted = 0
				unlocked = 1
				self.my_state = "Not Encrypted"
				self.my_color = wx.RED
			else:
				encrypted = 1
				unlocked = 0
				self.my_state = "Encrypted"
				self.my_color = wx.GREEN
			
			#public_key_readable = str(key.publickey().exportKey())
			with open('pubkey.der') as publ:
				public_key_readable = publ.read()
			publ.close()
			
			if (len(public_key_readable)) != 271 and (len(public_key_readable)) != 799:
				raise ValueError("Invalid public key length: {}".format(len(public_key_readable)))

			public_key_hashed = base64.b64encode(public_key_readable.encode("utf-8")).decode("utf-8")
			self.myaddress = hashlib.sha224(public_key_readable.encode("utf-8")).hexdigest()
			#print(self.myaddress)

		if not os.path.exists('address_qr.png'):
			address_qr = pyqrcode.create(self.myaddress)
			address_qr.png('address_qr.png')
		
		self.box1 = wx.BoxSizer(wx.VERTICAL)
		
		self.topbox1 = wx.BoxSizer(wx.HORIZONTAL) # logo and top text
		self.tbleft1 = wx.BoxSizer(wx.VERTICAL) # top text
		
		self.s = wx.StaticText(self, -1, "Wallet Address ({})".format(self.my_state))
		self.s.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
		self.s.SetForegroundColour(self.my_color)
		self.s.SetSize(self.s.GetBestSize())
		self.tbleft1.Add(self.s, 0, wx.ALL|wx.CENTER, 5)
	
		self.t = wx.StaticText(self, -1, self.myaddress)
		self.t.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
		self.t.SetForegroundColour("#444995")
		self.t.SetSize(self.t.GetBestSize())
		self.tbleft1.Add(self.t, 0, wx.ALL|wx.CENTER, 5)

		self.b = wx.StaticText(self, -1, "") # current balance
		self.b.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
		self.b.SetForegroundColour("#444995")
		self.b.SetSize(self.b.GetBestSize())
		self.tbleft1.Add(self.b, 0, wx.ALL|wx.CENTER, 5)
		
		self.d = wx.StaticText(self, -1, "") # wallet summary
		self.d.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
		self.d.SetForegroundColour("#444995")
		self.d.SetSize(self.d.GetBestSize())
		self.tbleft1.Add(self.d, 0, wx.ALL|wx.CENTER, 5)
	
		self.topbox1.Add(self.tbleft1, 0, wx.ALL|wx.CENTER, 10)
				
		self.myimage = wx.Image('address_qr.png', wx.BITMAP_TYPE_ANY)
		self.myimage = self.myimage.Scale(120,120)
		self.image1 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(self.myimage))
		self.topbox1.Add(self.image1, 0, wx.ALL|wx.RIGHT, 10)
		
		self.box1.Add(self.topbox1, 0, wx.ALL|wx.CENTER, 10)
		
		self.w_text4 = wx.StaticText(self, -1, "") # list title
		self.w_text4.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
		self.w_text4.SetForegroundColour("#08750A")
		self.w_text4.SetSize(self.w_text4.GetBestSize())
		self.box1.Add(self.w_text4, 0, wx.ALL|wx.CENTER, 5)
		
		self.list_ctrl1 = wx.ListCtrl(self, size=(675,600),
						 style=wx.LC_REPORT
						 |wx.BORDER_SUNKEN
						 )

		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnAbout, self.list_ctrl1)
		self.list_ctrl1.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
		self.list_ctrl1.InsertColumn(0, 'Block', wx.LIST_FORMAT_LEFT)
		self.list_ctrl1.InsertColumn(1, 'Date', wx.LIST_FORMAT_LEFT)
		self.list_ctrl1.InsertColumn(2, 'To', wx.LIST_FORMAT_LEFT)
		self.list_ctrl1.InsertColumn(3, 'From', wx.LIST_FORMAT_LEFT)
		self.list_ctrl1.InsertColumn(4, 'Amount', wx.LIST_FORMAT_LEFT)
		self.list_ctrl1.InsertColumn(5, 'Reward', wx.LIST_FORMAT_LEFT)
		
		self.list_ctrl1.SetColumnWidth(0, 0)
		self.list_ctrl1.SetColumnWidth(1, 100)
		self.list_ctrl1.SetColumnWidth(2, 175)
		self.list_ctrl1.SetColumnWidth(3, 175)
		self.list_ctrl1.SetColumnWidth(4, 100)
		self.list_ctrl1.SetColumnWidth(5, 100)
	
		self.box1.Add(self.list_ctrl1, 0, wx.ALL|wx.CENTER, 10)

		self.SetSizer(self.box1)
		self.Layout()
		self.timer.Start(1 * 1000)
		
	def OnAbout(self, event):
		l_event = event.GetIndex()
		l_item1 = self.list_ctrl1.GetItem(l_event, 0)
		l_item2 = self.list_ctrl1.GetItem(l_event, 4)
		getblock = l_item1.GetText()
		getamount = l_item2.GetText()
		gettitle = "Wallet Information | Transaction Details"

		if tgetvars(getblock,getamount,gettitle):
			dlg = AboutBoxT()
			dlg.ShowModal()
			dlg.Destroy()
	
	def update(self, event):
		global latest

		self.timer.Stop()
		
		c = get_json_info("stats","circulation")
		b = get_json_info("stats","latestblock")
		
		try:
			circ = '%.2f' % float(c['circulation'])
		except:
			circ = 'error check connection'
		
		try:
			latest = str(b['height'])
			last_diff = str(b['difficulty'])
		except:
			latest = 'error check connection'

		statusbar.SetStatusText('Current circulation: {} BIS'.format(circ), 0)
		statusbar.SetStatusText('Current block height: {}'.format(latest), 1)
		statusbar.SetStatusText('Last difficulty: {}'.format(last_diff), 2)
		
		#print("Updating")
		y = get_json_info("address",self.myaddress)
		#print(y)
		
		try:
			self.balance = '%.8f' % float(y['balance'])
			self.credits = '%.8f' % float(y['credits'])
			self.debits = '%.8f' % float(y['debits'])
			self.rewards = '%.8f' % float(y['rewards'])
			self.fees = '%.8f' % float(y['fees'])
			#print('Balance: {}\nCredits: {}\nDebits: {}\nRewards: {}\nFees: {}'.format(self.balance,self.credits,self.debits,self.rewards,self.fees))
		except:
			self.balance = "0"
			self.credits = "0"
			self.debits = "0"
			self.rewards = "0"
			self.fees = "0"
			self.error = y['error']
			#print(self.error)
			
		det1 = "Credits: {} | Debits: {} | Rewards: {} | Fees: {}".format(self.credits,self.debits,self.rewards,self.fees)
		
		t = get_json_info("getlimit","{}=20".format(self.myaddress))
		#print(len(t))
		
		if len(t) == 1:
			mybacon = []
			#print("No bacon")
		else:
			nt = len(t)
			if nt < 21:
				mt = nt
			else:
				mt = 21
			mybacon = [t[i] for i in range(1,mt)]
			#print(mybacon[0]['amount'])
		
		t = None
		
		self.b.SetLabel("Current Balance: {} BIS".format(self.balance))
		self.d.SetLabel(det1)

		self.list_ctrl1.DeleteAllItems()
		
		if not mybacon:
			self.w_text4.SetLabel("No transactions found for this address")
			self.w_text4.SetForegroundColour(wx.RED)
		else:
			self.w_text4.SetLabel("Latest Transactions")
			self.w_text4.SetForegroundColour("#08750A")
			for i in range(mt-1):
				if i % 2 == 0:
					color_cell = "#FFFFFF"
				else:
					color_cell = "#E8E8E8"
				index = i
				in_time = datetime.fromtimestamp(float(mybacon[i]['timestamp'])).strftime('%Y-%m-%d %H:%M:%S')
				self.list_ctrl1.InsertItem(index, str(mybacon[i]['block']))
				self.list_ctrl1.SetItem(index, 1, in_time) # mybacon[i]['timestamp'])
				self.list_ctrl1.SetItem(index, 2, mybacon[i]['to'])
				self.list_ctrl1.SetItem(index, 3, mybacon[i]['from'])
				self.list_ctrl1.SetItem(index, 4, mybacon[i]['amount'])
				self.list_ctrl1.SetItem(index, 5, mybacon[i]['reward'])
				self.list_ctrl1.SetItemBackgroundColour(item=index, col=color_cell)
				self.list_ctrl1.SetItemData(index,index)

		self.SetSizer(self.box1)
		self.Layout()
		self.timer.Start(300 * 1000)
		#print("Updated")
		
#---------------------------------------------------------------------------------------------------------------

class PageThree(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		
		l_text1 = wx.StaticText(self, -1, "Bismuth Ledger Query Tool")
		l_text1.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		l_text1.SetSize(l_text1.GetBestSize())
		
		l_text2 = wx.StaticText(self, -1, "Query the explorer for a List of Transactions")
		l_text2.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
		l_text2.SetSize(l_text2.GetBestSize())
		
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)

		l_text3 = wx.StaticText(self, -1, "Enter a Block Number, Hash or Address:")
		l_text3.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
		l_text3.SetSize(l_text3.GetBestSize())

		self.lt1 = wx.TextCtrl(self, size=(350, -1), style=wx.TE_PROCESS_ENTER)
		self.lt1.Bind(wx.EVT_TEXT_ENTER, self.OnSubmit)
		self.lt1.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
		
		hbox2.Add(l_text3, 0, wx.ALL|wx.RIGHT, 2)
		hbox2.Add(self.lt1, 0, wx.ALL|wx.LEFT, 2)
		
		hbox3 = wx.BoxSizer(wx.HORIZONTAL)

		l_text4 = wx.StaticText(self, -1, "             Click Submit to List Transactions")
		l_text4.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
		l_text4.SetSize(l_text4.GetBestSize())

		l_submit = wx.Button(self, wx.ID_APPLY, "Submit Query")
		l_submit.Bind(wx.EVT_BUTTON, self.OnSubmit)
		
		hbox3.Add(l_text4, 0, wx.ALL|wx.RIGHT, 2)
		hbox3.Add(l_submit, 0, wx.ALL|wx.LEFT, 2)
	
		hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		
		self.l_text6 = wx.StaticText(self, -1, "")
		self.l_text6.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
		self.l_text6.SetForegroundColour("#08750A")		
		self.l_text6.SetSize(self.l_text6.GetBestSize())
		
		self.l_text7 = wx.StaticText(self, -1, "")
		self.l_text7.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
		self.l_text7.SetForegroundColour("#08750A")		
		self.l_text7.Bind(wx.EVT_LEFT_DOWN, self.OnLeft)
		self.l_text7.SetSize(self.l_text7.GetBestSize())
		
		self.l_text8 = wx.StaticText(self, -1, "")
		self.l_text8.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
		self.l_text8.SetForegroundColour("#08750A")		
		self.l_text8.Bind(wx.EVT_LEFT_DOWN, self.OnRight)
		self.l_text8.SetSize(self.l_text8.GetBestSize())

		hbox4.Add(self.l_text7, 0, wx.ALL|wx.LEFT, 2)
		hbox4.Add(self.l_text6, 0, wx.ALL|wx.RIGHT, 2)
		hbox4.Add(self.l_text8, 0, wx.ALL|wx.CENTER, 2)		

		self.index = 0

		self.list_ctrl = wx.ListCtrl(self, size=(-1,425),
						 style=wx.LC_REPORT
						 |wx.BORDER_SUNKEN
						 )
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnAbout, self.list_ctrl)
		self.list_ctrl.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
		self.list_ctrl.InsertColumn(0, 'Block Number')
		self.list_ctrl.InsertColumn(1, 'To')
		self.list_ctrl.InsertColumn(2, 'Amount')
		self.list_ctrl.InsertColumn(3, 'Reward')
		
		self.list_ctrl.SetColumnWidth(0, -2)
		self.list_ctrl.SetColumnWidth(1, -1)
		self.list_ctrl.SetColumnWidth(2, -2)
		self.list_ctrl.SetColumnWidth(3, -2)
		
		self.box2 = wx.BoxSizer(wx.VERTICAL)
		self.box2.Add(l_text1, 0, wx.ALL|wx.CENTER, 2)
		self.box2.Add(l_text2, 0, wx.ALL|wx.CENTER, 2)
		self.box2.Add(hbox2, 0, wx.ALL|wx.LEFT, 2)
		self.box2.Add(hbox3, 0, wx.ALL|wx.LEFT, 2)
		self.box2.Add(hbox4, 0, wx.ALL|wx.CENTER, 2)
		self.box2.Add(self.list_ctrl, 0, wx.ALL|wx.EXPAND, 2)
		
		self.SetSizer(self.box2)
		
	def OnSubmit(self, event):
	
		myquery = str(self.lt1.GetValue())

		if not myquery: #Nonetype handling - simply replace with "0"
			myquery = "0"
		if not myquery.isalnum():
			myquery = "0"
			#print "has dodgy characters but now fixed"
		my_type = test(myquery)
		
		if not my_type:
			self.l_text6.SetForegroundColour(wx.RED)
			self.l_text6.SetLabel("Error !!! Maybe you entered bad data or nothing at all?")
			self.box2.Layout()

		elif my_type == "adhash":
			d = get_json_info('getall',myquery)
			
			try:
				dodo = d[0]
				d_ad = True
			except:
				d = get_json_info('hash',myquery)
				
			if d_ad:
			
				y = get_json_info("address",myquery)
								
				try:
					self.balance = '%.8f' % float(y['balance'])
					self.credits = '%.8f' % float(y['credits'])
					self.debits = '%.8f' % float(y['debits'])
					self.rewards = '%.8f' % float(y['rewards'])
					self.fees = '%.8f' % float(y['fees'])
				except:
					self.balance = "0"
					self.credits = "0"
					self.debits = "0"
					self.rewards = "0"
					self.fees = "0"
					self.error = y['error']
					#print(self.error)
					
				det1 = "Balance: {} | Credits: {} | Debits: {} | Rewards: {} | Fees: {}".format(self.balance,self.credits,self.debits,self.rewards,self.fees)
				self.cleantxt()
				self.l_text6.SetLabel(det1)
				self.lt1.SetValue("")
	
		elif my_type == "block":
		
			d = get_json_info('block',myquery)
			self.l_text6.SetForegroundColour("#08750A")
			self.cleantxt()
			self.l_text6.SetLabel(myquery)
			self.l_text7.SetLabel("<< Previous ")
			self.l_text7.SetToolTip(wx.ToolTip("Go to block {}".format(str(int(myquery) - 1))))

			if (int(myquery) + 1) < (int(latest) + 1):
				self.l_text8.SetLabel("    Next >>")
				self.l_text8.SetToolTip(wx.ToolTip("Go to block {}".format(str(int(myquery) + 1))))
			
		mt = len(d)
		mybacon = [d[i] for i in range(1,mt)]
		self.list_ctrl.DeleteAllItems()
		
		for i in range(mt-1):
			if i % 2 == 0:
				color_cell = "#FFFFFF"
			else:
				color_cell = "#E8E8E8"
			index = i
			self.list_ctrl.InsertItem(index, str(mybacon[i]['block']))
			self.list_ctrl.SetItem(index, 1, mybacon[i]['to'])
			self.list_ctrl.SetItem(index, 2, mybacon[i]['amount'])
			self.list_ctrl.SetItem(index, 3, mybacon[i]['reward'])
			self.list_ctrl.SetItemBackgroundColour(item=index, col=color_cell)
			self.list_ctrl.SetItemData(index,index)
			
		self.list_ctrl.SetColumnWidth(0, -2)
		self.list_ctrl.SetColumnWidth(1, -1)
		self.list_ctrl.SetColumnWidth(2, -2)
		self.list_ctrl.SetColumnWidth(3, -2)
		self.Layout()
	
	def OnLeft(self, event):
		currblock = str(self.lt1.GetValue())
		if currblock.isdigit():
			currblock = int(currblock)
			prevblock = currblock - 1
			self.lt1.SetValue(str(prevblock))
			self.l_text7.SetLabel("<< Previous ")
			self.l_text7.SetToolTip(wx.ToolTip("Go to block {}".format(str(int(prevblock) - 1))))
			self.OnSubmit(wx.EVT_BUTTON)
		else:
			pass

	def OnRight(self, event):
		currblock = str(self.lt1.GetValue())
		if currblock.isdigit():
			currblock = int(currblock)
			nextblock = currblock + 1
			self.lt1.SetValue(str(nextblock))
			self.l_text8.SetLabel("    Next >>")
			self.l_text8.SetToolTip(wx.ToolTip("Go to block {}".format(str(int(nextblock) + 1))))
			self.OnSubmit(wx.EVT_BUTTON)
		else:
			pass
		
	def OnAbout(self, event):
		l_event = event.GetIndex()
		l_item1 = self.list_ctrl.GetItem(l_event, 0)
		l_item2 = self.list_ctrl.GetItem(l_event, 2)
		getblock = l_item1.GetText()
		getamount = l_item2.GetText()
		gettitle = "Transaction Details"

		if tgetvars(getblock,getamount,gettitle):
			dlg = AboutBoxT()
			dlg.ShowModal()
			dlg.Destroy()
			
	def cleantxt(self):
		self.l_text7.SetLabel("")
		self.l_text7.SetToolTip(wx.ToolTip(""))
		self.l_text8.SetLabel("")
		self.l_text8.SetToolTip(wx.ToolTip(""))
		
#--------------------------------------------------------------------------------

class PageFour(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		self.timer2 = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.OnRefresh, self.timer2)
		
		m_text1 = wx.StaticText(self, -1, "Bismuth Top {} Richlist".format(x_limit))
		m_text1.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		m_text1.SetSize(m_text1.GetBestSize())

		m_text2 = wx.StaticText(self, -1, "Hint: Click on an address to see more detail")
		m_text2.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
		m_text2.SetSize(m_text2.GetBestSize())
		
		self.l_refresh = wx.Button(self, wx.ID_APPLY, "Refresh List")
		self.l_refresh.Bind(wx.EVT_BUTTON, self.OnRefresh)

		self.index = 0

		self.list_ctrl = wx.ListCtrl(self, size=(-1,425),
						 style=wx.LC_REPORT
						 |wx.BORDER_SUNKEN
						 )
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnAbout, self.list_ctrl)
		self.list_ctrl.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
		self.list_ctrl.InsertColumn(0, 'Haddress')
		self.list_ctrl.InsertColumn(1, 'Rank')
		self.list_ctrl.InsertColumn(2, 'Address')
		self.list_ctrl.InsertColumn(3, 'Balance')
	
		self.list_ctrl.SetColumnWidth(0, 0)
		self.list_ctrl.SetColumnWidth(1, -2)
		self.list_ctrl.SetColumnWidth(2, -2)
		self.list_ctrl.SetColumnWidth(3, -2)
		
		box3 = wx.BoxSizer(wx.VERTICAL)
		box3.Add(m_text1, 0, wx.ALL|wx.CENTER, 5)
		box3.Add(m_text2, 0, wx.ALL|wx.CENTER, 5)
		box3.Add(self.l_refresh, 0, wx.ALL|wx.CENTER, 5)
		box3.Add(self.list_ctrl, 0, wx.ALL|wx.EXPAND, 5)

		self.SetSizer(box3)
		self.MyRichest()

		self.timer2.Start(600 * 1000)
		
	def MyRichest(self):

		d = get_json_info('richlist',x_limit)
		#print(d[0])

		mt = len(d)
		mybacon = [d[i] for i in range(mt)]
		self.list_ctrl.DeleteAllItems()
		
		for i in range(mt):
			if i % 2 == 0:
				color_cell = "#FFFFFF"
			else:
				color_cell = "#E8E8E8"
			index = i
			self.list_ctrl.InsertItem(index, str(mybacon[i]['address']))
			self.list_ctrl.SetItem(index, 1, mybacon[i]['rank'])
			if mybacon[i]['alias'] == "":
				self.list_ctrl.SetItem(index, 2, mybacon[i]['address'])
			else:
				self.list_ctrl.SetItem(index, 2, mybacon[i]['alias'])
			self.list_ctrl.SetItem(index, 3, mybacon[i]['balance'])
			self.list_ctrl.SetItemBackgroundColour(item=index, col=color_cell)
			self.list_ctrl.SetItemData(index,index)
			
		self.list_ctrl.SetColumnWidth(0, 0)
		self.list_ctrl.SetColumnWidth(1, -2)
		self.list_ctrl.SetColumnWidth(2, -2)
		self.list_ctrl.SetColumnWidth(3, -2)
		self.Layout()


	def OnAbout(self, event):
		SelectedRow = event.GetText()
		getaddress = str(SelectedRow)
		if bgetvars(getaddress):
			dlg = AboutBoxR()
			dlg.ShowModal()
			dlg.Destroy()

	def OnRefresh(self, event):
		self.timer2.Stop()
		logging.info("Richlist: Refresh requested")
		self.list_ctrl.DeleteAllItems()
		self.MyRichest()
		self.list_ctrl.Refresh()
		self.timer2.Start(600 * 1000)
		
#--------------------------------------------------------------------------------

class PageFive(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		self.timer2 = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.OnRefresh, self.timer2)
		
		m_text1 = wx.StaticText(self, -1, "Bismuth Miner Statistics: Top {}".format(x_limit))
		m_text1.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		m_text1.SetSize(m_text1.GetBestSize())

		m_text2 = wx.StaticText(self, -1, "Hint: Click on an address to see more detail")
		m_text2.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
		m_text2.SetSize(m_text2.GetBestSize())
		
		self.l_refresh = wx.Button(self, wx.ID_APPLY, "Refresh List")
		self.l_refresh.Bind(wx.EVT_BUTTON, self.OnRefresh)

		self.index = 0

		self.list_ctrl = wx.ListCtrl(self, size=(-1,425),
						 style=wx.LC_REPORT
						 |wx.BORDER_SUNKEN
						 )
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnAbout, self.list_ctrl)
		self.list_ctrl.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
		self.list_ctrl.InsertColumn(0, 'Haddress')
		self.list_ctrl.InsertColumn(1, 'Rank')
		self.list_ctrl.InsertColumn(2, 'Miner')
		self.list_ctrl.InsertColumn(3, 'Blocks Found')
	
		self.list_ctrl.SetColumnWidth(0, 0)
		self.list_ctrl.SetColumnWidth(1, -2)
		self.list_ctrl.SetColumnWidth(2, -2)
		self.list_ctrl.SetColumnWidth(3, -2)
		
		box3 = wx.BoxSizer(wx.VERTICAL)
		box3.Add(m_text1, 0, wx.ALL|wx.CENTER, 5)
		box3.Add(m_text2, 0, wx.ALL|wx.CENTER, 5)
		box3.Add(self.l_refresh, 0, wx.ALL|wx.CENTER, 5)
		box3.Add(self.list_ctrl, 0, wx.ALL|wx.EXPAND, 5)

		self.SetSizer(box3)
		self.MyMiners()

		self.timer2.Start(600 * 1000)
		
	def MyMiners(self):

		d = get_json_info('miners',x_limit)
		#print(d[0])

		mt = len(d)
		mybacon = [d[i] for i in range(mt)]
		self.list_ctrl.DeleteAllItems()
		
		for i in range(mt):
			if i % 2 == 0:
				color_cell = "#FFFFFF"
			else:
				color_cell = "#E8E8E8"
			index = i
			self.list_ctrl.InsertItem(index, str(mybacon[i]['address']))
			self.list_ctrl.SetItem(index, 1, mybacon[i]['rank'])
			if mybacon[i]['alias'] == "":
				self.list_ctrl.SetItem(index, 2, mybacon[i]['address'])
			else:
				self.list_ctrl.SetItem(index, 2, mybacon[i]['alias'])
			self.list_ctrl.SetItem(index, 3, mybacon[i]['blocks'])
			self.list_ctrl.SetItemBackgroundColour(item=index, col=color_cell)
			self.list_ctrl.SetItemData(index,index)
			
		self.list_ctrl.SetColumnWidth(0, 0)
		self.list_ctrl.SetColumnWidth(1, -2)
		self.list_ctrl.SetColumnWidth(2, -2)
		self.list_ctrl.SetColumnWidth(3, -2)
		self.Layout()


	def OnAbout(self, event):
		SelectedRow = event.GetText()
		getaddress = str(SelectedRow)
		if bgetvars(getaddress):
			dlg = AboutBoxR()
			dlg.ShowModal()
			dlg.Destroy()

	def OnRefresh(self, event):
		self.timer2.Stop()
		logging.info("Miners: Refresh requested")
		self.list_ctrl.DeleteAllItems()
		self.MyMiners()
		self.list_ctrl.Refresh()
		self.timer2.Start(600 * 1000)

#-----------------------------------------------------------------------

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title="Bismuth Tools", pos=(50,50), size=(700,720))
		
		loc = ticons.bismuthicon.GetIcon()
		self.SetIcon(loc)

		menubar = wx.MenuBar()

		m_file = wx.Menu()
		
		m_exit = m_file.Append(wx.ID_EXIT, '&Quit', 'Quit application')
		m_file.Append(2, '&Diff Window', 'Open Difficulty Window')
		
		menubar.Append(m_file, '&Actions')
		
		help = wx.Menu()
		
		help.Append(101, '&Wallet Info', 'Wallet Information')
		help.Append(103, '&Ledger Query', 'Ledger Query Help')
		help.Append(104, '&Richlist', 'Richlist Help')
		help.Append(105, '&Miners', 'Miners Help')
		help.Append(106, '&Sponsors', 'Sponsorship Help')
		help.Append(102, '&About', 'About this Program')
		
		menubar.Append(help, '&Help')

		self.SetMenuBar(menubar)
		
		self.Bind(wx.EVT_MENU, self.OnAbout, id=101)
		self.Bind(wx.EVT_MENU, self.OnAbout, id=103)
		self.Bind(wx.EVT_MENU, self.OnAbout, id=104)
		self.Bind(wx.EVT_MENU, self.OnAbout, id=102)
		self.Bind(wx.EVT_MENU, self.OnAbout, id=105)
		self.Bind(wx.EVT_MENU, self.OnAbout, id=106)
		self.Bind(wx.EVT_MENU, self.OnClick, id=2)
		self.Bind(wx.EVT_MENU, self.OnQuit, m_exit)
		
		global statusbar
		statusbar = self.CreateStatusBar()
		statusbar.SetFieldsCount(3)
		statusbar.SetStatusWidths([-1, -1, -1])
		statusbar.SetStatusText('', 0)
		statusbar.SetStatusText('', 1)
		statusbar.SetStatusText('', 2)
		
		# Here we create a panel and a notebook on the panel
		p = wx.Panel(self)
		self.nb = wx.Notebook(p)
		
		# create the page windows as children of the notebook
		page1 = PageOne(self.nb)
		page2 = PageTwo(self.nb)
		page3 = PageThree(self.nb)
		page4 = PageFour(self.nb)
		page5 = PageFive(self.nb)
				
		# add the pages to the notebook with the label to show on the tab
		self.nb.AddPage(page1, "Home")
		self.nb.AddPage(page2, "Wallet Info")
		self.nb.AddPage(page3, "Ledger Query")
		self.nb.AddPage(page4, "Richlist")
		self.nb.AddPage(page5, "Miners")

		# finally, put the notebook in a sizer for the panel to manage
		# the layout
		sizer = wx.BoxSizer()
		sizer.Add(self.nb, 1, wx.EXPAND)
		self.CentreOnParent(wx.BOTH)
		p.SetSizer(sizer)

		statusbar.Bind(EVT_UPDATE_STATUSBAR, self.OnStatus)
		statusbar.Bind(wx.EVT_LEFT_DOWN, self.OnClick)

	def OnAbout(self, event):
		global thistitle
		global thisid
		thisid = event.Id
		if thisid == 101:
			thistitle = "Wallet Information Help"
		elif thisid == 102:
			thistitle = "About Bismuth Tools"
		elif thisid == 103:
			thistitle = "Ledger Query Help"
		elif thisid == 104:
			thistitle = "Richlist Help"
		elif thisid == 105:
			thistitle = "Miners Help"
		elif thisid == 106:
			thistitle = "Sponsorship Help"
		dlg = AboutBox()
		dlg.ShowModal()
		dlg.Destroy()

	def updateStatus(self, msg):
		mystatus = msg
		statusbar.SetStatusText(mystatus, 2)

	def OnStatus(self, evt):
		statusbar.SetStatusText(evt.msg, evt.st_id)		


	def OnQuit(self, event):
		logging.info("App: Quit")
		self.Close()
		
	def OnClick(self, event):
		mygraph = MyGraph(None, -1,  size=(1000,700))
		mygraph.Show()
		
if __name__ == "__main__":

	app = wx.App()
	MainFrame().Show()
	app.MainLoop()