import requests
from bs4 import BeautifulSoup as bs
import time
class cars:
    def __init__(self):
        self.carids=[]
        self.cartypes=[]
        self.merchans=[]
        self.accomodates=[]
        self.taskid=[]
        self.stationid=[]
    def pushMerchan(self,merchan,quantity):
        arr=[merchan,quantity]
        self.merchans[-1].append(arr)
    def pushCar(self,cid,accomodate,ctype,tid):
        self.carids.append(cid)
        self.accomodates.append(accomodate)
        self.cartypes.append(ctype)
        self.taskid.append(tid)
    def show(self):
        print(self.carids)
        print(self.merchans)
        print(self.taskid)
        print(self.accomodates)
        print(self.cartypes)
    def assignStation(self,station):
        self.stationid.append(station)

#ipp="http://192.168.39.243:3000"
ipp="https://finalproj-446307.de.r.appspot.com/"

def concatUrl(string):
    return ipp+"?"+string
def takeTask(car):
    url=concatUrl("command=takeTask")
    res=requests.get(url)
    if (res.text=="no task remain"):
        return "no remaining task"
    if (res.text=="no rows can be operated"):
        return "no remaining car"
    
    
    content=res.text.split("\n")
    taskType=content[0].split(':')[1]
    taskid=content[1].split(':')[1]
    merchanids=content[2].split(':')[1].split(',')
    carid=content[3].split(':')[1]
    quantitys=content[4].split(':')[1].split(',')
    url=concatUrl("command=assignPS&taskid="+str(taskid))
    res=requests.get(url)
    if(res.text=="no remaining station"):
       return "no remaining station"
    car.assignStation(res.text.split(':')[1])
    #print(taskType)
    #print(taskid)
    #print(merchanids)
    #print(carid)
    #print(quantitys)
    car.pushCar(carid,0,0,taskid)
    car.merchans.append([])
    
    for i in range(0,len(merchanids)):    
        car.pushMerchan(merchanids[i],quantitys[i])
        url=concatUrl("command=taskDecided&taskID="+str(taskid)+"&carID="+str(carid)+"&taskType="+str(taskType)+"&quantity="+str(quantitys[i])+"&merchanID="+str(merchanids[i]))
        print(url)
        requests.get(url)

    return "success"
    
def launchMerchan(car,cid):
    cid=str(cid)
    print(car.carids)
    print(cid)
    print(type(car.carids[0]))
    print(type(cid))
    selectCarIndex=afind(car.carids,cid)
    print(selectCarIndex)
    i = car.merchans[selectCarIndex][0]
    print("OP  : ",len(car.merchans))
    url=concatUrl("command=startTransferring&carID="+str(car.carids[selectCarIndex])+"&taskID="+str(car.taskid[selectCarIndex])+"&merchanID="+str(i[0])+"&quantity="+str(i[1]))
    time.sleep(0.1)
    print(url)
    requests.get(url)
    car.merchans[selectCarIndex].pop(0)
def afind(arr,ele):
    for i in range(0,len(arr)):
        if str(arr[i])==str(ele):
            return i
    return -1
def carArrive(car,cid):
    url=concatUrl("command=transferArrive&carID="+str(cid))
    print(url)
    requests.get(url)
    index=afind(car.carids,cid)
    car.carids.pop(index)
    car.cartypes.pop(index)
    car.accomodates.pop(index)
    car.merchans.pop(index)
def MTrans(merchanid):
    url=concatUrl("command=merchanInfoTrans&merchanid="+str(merchanid))
    res=requests.get(url).text
    name=res.split(";")[0].split(":")[1]
    x=res.split(";")[1].split(":")[1]
    y=res.split(";")[2].split(":")[1]
    z=res.split(";")[3].split(":")[1]
    w=res.split(";")[4].split(":")[1]
    arr=[name,x,y,z,w]
    return arr
