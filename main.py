from MainWindow import *

__appname__ = "NablaPy"
data  = RadarData
controller = RadarController
mainwindow = MainWindow(__appname__,data,controller)
mainwindow.window.mainloop()