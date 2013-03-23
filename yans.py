#!/usr/bin/python

# yans 0.1
#
# This application finds questions and there recommended answers from yahoo answer service
# 
# licence: GPl3
# author: Unnikrishnan B.
# email: unnikrishnanadoor@gmail.com
# website: http://unnikrishnan.in 
# 

import gtk, glib
import urllib
from xml.dom import minidom

ANSWER_URL = 'http://answers.yahooapis.com/AnswersService/V1/questionSearch?appid=YahooDemo&query=%s'

class YAns(gtk.Window): 
  def __init__(self):
    super(YAns, self).__init__()
    
    self.set_size_request(400, 500)
    self.set_position(gtk.WIN_POS_CENTER)
    
    self.connect("destroy", gtk.main_quit)
    self.set_title("YAns")
    
    textBox = gtk.TextView()
    menuBar = gtk.MenuBar()
    self.statusBar = gtk.Statusbar()
    self.statusBar.get_context_id("yans");
    vbox = gtk.VBox(False, 0)
    
    box1 = gtk.VBox(False, 0)
    box2 = gtk.VBox(False, 0)
    box3 = gtk.VBox(False, 0)
    box4 = gtk.VBox(False, 0)
    
    vbox.pack_start(box1, False, False, 0)
    vbox.pack_start(box2, False, False, 0)
    vbox.pack_start(box3, True, True, 0)
    vbox.pack_start(box4, False, False, 0)
    
    hbox = gtk.HBox(False, 5)
    label = gtk.Label("Search")
    
    self.buf = gtk.EntryBuffer("", -1);
    self.buf.connect("deleted-text", self.buf_on_change, "")
    self.buf.connect("inserted-text", self.buf_on_change)

    entry = gtk.Entry()
    entry.set_buffer(self.buf)
    hbox.pack_start(label, False, False, 0)
    hbox.pack_end(entry, True, True, 0)
    
    agr = gtk.AccelGroup()
    self.add_accel_group(agr)

    filemenu = gtk.Menu()
    filem = gtk.MenuItem("_File")
    filem.set_submenu(filemenu)
    
    exit = gtk.ImageMenuItem(gtk.STOCK_QUIT, agr)
    key, mod = gtk.accelerator_parse("<Control>Q")
    exit.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)
    exit.connect("activate", gtk.main_quit)
    filemenu.append(exit)
    
    
    helpmenu = gtk.Menu()
    helpm = gtk.MenuItem("_Help")
    helpm.set_submenu(helpmenu)
    
    about = gtk.ImageMenuItem(gtk.STOCK_ABOUT, agr)
    key, mod = gtk.accelerator_parse("<Control>Q")
    about.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)
    about.connect("activate", self.about_clicked)
    helpmenu.append(about)
    
    menuBar.append(filem)
    menuBar.append(helpm)
    
    tree = gtk.TreeView()
    
    languages = gtk.TreeViewColumn()
    languages.set_title("Suggestions")
    
    cell = gtk.CellRendererText()

    languages.pack_start(cell, True)
    languages.add_attribute(cell, "text", 0)

    self.treestore = gtk.TreeStore(str)
    tree.append_column(languages)
    tree.set_model(self.treestore)
    
    sw = gtk.ScrolledWindow()
    sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
    sw.add(tree)
    
    box1.pack_start(menuBar, True, False, 0)
    box2.pack_start(hbox, False, False, 0)
    box3.pack_start(sw, True, True, 0)
    box4.pack_start(self.statusBar, True, False, 0)
    
    id = self.statusBar.get_context_id("yans")  
    self.statusBar.push(id, "Done");  
    
    self.add(vbox)
    self.show_all()
    self.connect_after('size-allocate', YAns.resize_wrap, tree, languages, cell)
    
  #for wrappig test in the tree view control.      
  def resize_wrap(window, allocation, treeview, column, cell):
    newWidth = allocation.width
    newWidth -= treeview.style_get_property("horizontal-separator") * 4
    if cell.props.wrap_width == newWidth or newWidth <= 0:
      return
    if newWidth < 400:
      newWidth = 400
    cell.props.wrap_width = newWidth
    column.set_property('min-width', newWidth + 10)
    column.set_property('max-width', newWidth + 10)
    store = treeview.get_model()
    iter = store.get_iter_first()
    while iter and store.iter_is_valid(iter):
      store.row_changed(store.get_path(iter), iter)
      iter = store.iter_next(iter)
      treeview.set_size_request(0,-1)
  #for pulling content from yahoo    
  def request_query(self, question):
    url = ANSWER_URL % question
    dom = minidom.parse(urllib.urlopen(url))
    queries = []
    for node in dom.getElementsByTagNameNS("*", 'Question'):
      queries.append({
        'qst': self.getText(node.getElementsByTagName('Subject')[0].childNodes),
        'ans': self.getText(node.getElementsByTagName('ChosenAnswer')[0].childNodes)
      })
    return queries
    
  def  buf_on_change(self, buffer, position, chars, n_chars):
    if hasattr(self, 'timer'):
      glib.source_remove(self.timer)
    id = self.statusBar.get_context_id("yans")  
    self.statusBar.push(id, "Loading...");  
    self.timer = glib.timeout_add(1000, self.renderText)
    return False

  def renderText(self):
    txt = self.buf.get_text()
    self.treestore.clear()
    for node in self.request_query(txt):
      itr = self.treestore.append(None, [node['qst']]);
      self.treestore.append(itr, [node['ans']])
      
    id = self.statusBar.get_context_id("yans")  
    self.statusBar.push(id, "Done");  
    return False
    
  def getText(self, nodelist):
    rc = []
    for node in nodelist:
      if node.nodeType == node.TEXT_NODE:
        rc.append(node.data)
    return ''.join(rc)
    
  def about_clicked(self, widget):
    about = gtk.AboutDialog()
    about.set_program_name("Yans")
    about.set_version("0.1")
    about.set_copyright("GPLv3")
    about.set_comments("Yahoo answer client")
    about.set_website("http://unnikrishnan.in")
    about.set_logo(gtk.gdk.pixbuf_new_from_file("/usr/share/pixmaps/yans.png"))
    about.run()
    about.destroy()

YAns()
gtk.main()
