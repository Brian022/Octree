import vtk
from random import randint, random 

class Point:
	def __init__(self,x,y,z):
		self.x=x
		self.y=y
		self.z=z
		self.punto=vtk.vtkSphereSource()
		self.punto.SetRadius(0.3)
		self.punto.SetCenter(x,y,z)

		self.puntoMapper=vtk.vtkPolyDataMapper()
		self.puntoMapper.SetInputConnection(self.punto.GetOutputPort())

		self.puntoActor=vtk.vtkActor()
		self.puntoActor.SetMapper(self.puntoMapper)

class Cube:
    def __init__(self,x,y,z,t):
        self.x=x
        self.y=y
        self.z=z
        self.t=t
        self.color=[random()*0.5,random(),random()]
        self.cube=vtk.vtkCubeSource()
        self.cube.SetXLength(self.t*2.0)
        self.cube.SetYLength(self.t*2.0)
        self.cube.SetZLength(self.t*2.0)
        self.cube.SetCenter(self.x,self.y,self.z)

        self.cubeMapper=vtk.vtkPolyDataMapper()
        self.cubeMapper.SetInputConnection(self.cube.GetOutputPort())
        self.cubeMapper.SetResolveCoincidentTopologyToShiftZBuffer()

        self.cubeActor=vtk.vtkActor()
        self.cubeActor.SetMapper(self.cubeMapper)
        self.cubeActor.GetProperty().SetColor(self.color)
        self.cubeActor.GetProperty().SetOpacity(0.4)

    def contains(self, point):
        return point.x<=self.x+self.t and point.x>=self.x-self.t and point.y<=self.y+self.t and point.y>=self.y-self.t and point.z<=self.z+self.t and point.z>=self.z-self.t
    
    def intersects(self,range):
    	if((range.x-range.t>self.x-self.t and range.x-range.t<self.x+self.t) or (range.x-range.t<self.x-self.t and self.x-self.t<range.x+range.t)):
    		if((range.y-range.t>self.y-self.t and range.y-range.t<self.y+self.t) or (range.y-range.t<self.y-self.t and self.y-self.t<range.y+range.t)):
    			return(range.z-range.t>self.z-self.t and range.z-range.t<self.z+self.t) or (range.z-range.t<self.z-self.t and self.z-self.t<range.z+range.t)
    	return False

class Octree:

    def __init__(self,boundary,n):
        self.boundary=boundary
        self.capacity=n
        self.points=[]
        self.divided=False

    def subdivide(self):
        x = self.boundary.x
        y = self.boundary.y
        z = self.boundary.z
        t = self.boundary.t
                
        northwestCube=Cube(x-float(t/2),y-float(t/2),z+float(t/2),float(t/2))
        northeastCube=Cube(x+float(t/2),y-float(t/2),z+float(t/2),float(t/2))
        southwestCube=Cube(x-float(t/2),y+float(t/2),z+float(t/2),float(t/2))
        southeastCube=Cube(x+float(t/2),y+float(t/2),z+float(t/2),float((t)/2))
        
        northwestCubeNeg=Cube(x-float(t/2),y-float(t/2),z-float(t/2),float((t)/2))
        northeastCubeNeg=Cube(x+float(t/2),y-float(t/2),z-float(t/2),float((t)/2))
        southwestCubeNeg=Cube(x-float(t/2),y+float(t/2),z-float(t/2),float((t)/2))
        southeastCubeNeg=Cube(x+float(t/2),y+float(t/2),z-float(t/2),float((t)/2))

        self.northwest=Octree(northwestCube,self.capacity)
        self.northeast=Octree(northeastCube,self.capacity)
        self.southwest=Octree(southwestCube,self.capacity)
        self.southeast=Octree(southeastCube,self.capacity)
        self.northwestNeg=Octree(northwestCubeNeg,self.capacity)
        self.northeastNeg=Octree(northeastCubeNeg,self.capacity)
        self.southwestNeg=Octree(southwestCubeNeg,self.capacity)
        self.southeastNeg=Octree(southeastCubeNeg,self.capacity)
    
        self.divided=True;
        
    def insert(self,point):
    	if(not self.boundary.contains(point)):
    		return False
    	if(len(self.points)<self.capacity and self.divided==False):
    		self.points.append(point)
    		point.puntoActor.GetProperty().SetColor(self.boundary.color)
    		return True
    	if(not self.divided):
    		self.subdivide()
    	if(self.northwest.insert(point)):
    		return True
    	if(self.northeast.insert(point)):
    		return True
    	if(self.southwest.insert(point)):
    		return True
    	if(self.southeast.insert(point)):
    		return True
    	if(self.northwestNeg.insert(point)):
    		return True
    	if(self.northeastNeg.insert(point)):
    		return True
    	if(self.southwestNeg.insert(point)):
    		return True
    	if(self.southeastNeg.insert(point)):
    		return True
    	return False

    def query(self,consulta,found):
    	centro=consulta.cube.GetCenter()
    	consulta.x=centro[0]
    	consulta.y=centro[1]
    	consulta.z=centro[2]
    	tam=consulta.cube.GetXLength()
    	consulta.t=tam/2.0
    	if(self.boundary.intersects(consulta)==False):
    		return
    	for p in self.points:
    		if(consulta.contains(p)):
    			found.append(p)
    	if(self.divided):
    		self.northwest.query(consulta,found)
    		self.northeast.query(consulta,found)
    		self.southwest.query(consulta,found)
    		self.southeast.query(consulta,found)
    		self.northwestNeg.query(consulta,found)
    		self.northeastNeg.query(consulta,found)
    		self.southwestNeg.query(consulta,found)
    		self.southeastNeg.query(consulta,found)

    def show(self,w):
    	w.AddActor(self.boundary.cubeActor)
    	if(self.divided):
    		self.northwest.show(w)
    		self.northeast.show(w)
    		self.southwest.show(w)
    		self.southeast.show(w)
    		self.northwestNeg.show(w)
    		self.northeastNeg.show(w)
    		self.southwestNeg.show(w)
    		self.southeastNeg.show(w)
    
    	for i in self.points:
    		w.AddActor(i.puntoActor)

boundary=Cube(0,0,0,10)
octree=Octree(boundary,4)
consulta=Cube(0,0,0,2.5)
consulta.cubeActor.GetProperty().SetColor(0,255,0)
consulta.cubeActor.GetProperty().SetOpacity(0.4)

for i in range(30):
	x=randint(-9,9)
	y=randint(-9,9)
	z=randint(-9,9)
	print(x,y,z)
	m=Point(x,y,z)
	octree.insert(m)

render=vtk.vtkRenderer()
render.SetUseDepthPeeling(1)
render.SetBackground(1,1,1)
render.AddActor(consulta.cubeActor)
renWin=vtk.vtkRenderWindow()
renWin.OpenGLInit()
renWin.AddRenderer(render)
renWin.SetWindowName("OcTree")
renWin.SetSize(500,500)
renWin.SetAlphaBitPlanes(1)
interactorRender=vtk.vtkRenderWindowInteractor()
interactorRender.SetRenderWindow(renWin)

pointss=[]
def KeyPress(obj,event):
    global pointss
    key=obj.GetKeySym()
    
    for p in pointss:
        p.punto.SetRadius(0.3)
        interactorRender.Render()
    pointss=[]
    if(key=="8"):
        posi=consulta.cube.GetCenter()
        posin=[posi[0],posi[1]+1.0,posi[2]]
        consulta.cube.SetCenter(posin)
        octree.query(consulta,pointss)
        interactorRender.Render()
        #print(posi)
    elif(key=="5"):
        posi=consulta.cube.GetCenter()
        posin=[posi[0],posi[1]-1.0,posi[2]]
        consulta.cube.SetCenter(posin)
        octree.query(consulta,pointss)
        interactorRender.Render()
    elif(key=="4"):
        posi=consulta.cube.GetCenter()
        posin=[posi[0]-1.0,posi[1],posi[2]]
        consulta.cube.SetCenter(posin)
        octree.query(consulta,pointss)
        interactorRender.Render()
    elif(key=="6"):
        posi=consulta.cube.GetCenter()
        posin=[posi[0]+1.0,posi[1],posi[2]]
        consulta.cube.SetCenter(posin)
        interactorRender.Render()
    elif(key=="7"):
        posi=consulta.cube.GetCenter()
        posin=[posi[0],posi[1],posi[2]-1.0]
        consulta.cube.SetCenter(posin)
        octree.query(consulta,pointss)
        interactorRender.Render()
    elif(key=="9"):
        posi=consulta.cube.GetCenter()
        posin=[posi[0],posi[1],posi[2]+1.0]
        consulta.cube.SetCenter(posin)
        octree.query(consulta,pointss)
        interactorRender.Render()
    elif(key=="plus"):
        x=consulta.cube.GetXLength()
        y=consulta.cube.GetYLength()
        z=consulta.cube.GetZLength()
        consulta.cube.SetXLength(x+1)
        consulta.cube.SetYLength(y+1)
        consulta.cube.SetZLength(z+1)
        octree.query(consulta,pointss)
        interactorRender.Render()
    elif(key=="minus"):
        x=consulta.cube.GetXLength()
        y=consulta.cube.GetYLength()
        z=consulta.cube.GetZLength()
        consulta.cube.SetXLength(x-1)
        consulta.cube.SetYLength(y-1)
        consulta.cube.SetZLength(z-1)
        octree.query(consulta,pointss)
        interactorRender.Render()
    elif(key=="1"):
        x=float(input("X:"))
        y=float(input("Y:"))
        z=float(input("Z:"))
        m=Point(x,y,z)
        octree.insert(m)
        octree.show(render)
        octree.query(consulta,pointss)
        interactorRender.Render()
    elif(key=="2"):
        x=randint(-9,9)
        y=randint(-9,9)
        z=randint(-9,9)
        m=Point(x,y,z)
        octree.insert(m)
        octree.show(render)
        octree.query(consulta,pointss)
        interactorRender.Render()

    for p in pointss:
        p.punto.SetRadius(1)
        p.puntoActor.GetProperty().SetColor(0,0,0)
        interactorRender.Render()
        
interactorRender.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

interactorRender.AddObserver("KeyPressEvent", KeyPress)
interactorRender.Initialize()
octree.show(render)
interactorRender.Start()