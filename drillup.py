#
# Beijing_historical_meo_grid.csv 时间[2017-1-1:2018-3-27] 地点[grid 0:650]
# air
# air格式：
# stationId,utc_time,PM2.5,PM10,NO2,CO,O3,SO2
# weather格式：
# stationName,longitude,latitude,utc_time,temperature,pressure,humidity,wind_direction,wind_speed
weather_file='data/Beijing_historical_meo_grid.csv'
air_file='data/beijing_17_18_aq.csv'
station_mapping_file='data/beijingairmapping.csv'
grid_mapping_file='data/Beijing_grid_weather_station.csv'
from datetime import datetime,date,timedelta
import time,pickle,os,math
def autoload(file):
    f=file.split('.')
    store=f[0]
    if os.path.exists(store):
        with open(store,'rb') as f:
            print('load from %s'%store)
            return pickle.load(f)
    return 0
def autosave(obj,file):
    f=file.split('.')
    store=f[0]
    with open(store,'wb') as f:
        print('save to %s'%store)
        pickle.dump(obj,f)
        
def query(weather,air,time,stationlist):
    #从weather和air中查询time,返回按stationlist顺序
    #返回[air at time, weather at time]
    #若缺失越界返回0
    #保证weather air dict中每一项都是有效的
    timeformat='%Y-%m-%d %H:%M:%S'
    start=datetime.strptime(time,timeformat)
    airlist=[]
    weatherlist=[]
    def findNear(air,start,station):
        n=1
        while 1:
            before=(start-timedelta(hours=n)).strftime(timeformat)
            after=(start+timedelta(hours=n)).strftime(timeformat)
            if before in air:
                if station in air[before]:
                    return air[before][station]
            if after in air:
                if station in air[after]:
                    return air[after][station]
            n+=1
            if n > 4096:
                print('n=%d,what happens? %s'%(n,station))
                return 0
        
    if time in weather and time in air:
        
        for station in stationlist:
            if station in air[time]:
                airlist.append(air[time][station])
            else:
                tmp=findNear(air,start,station)
                if tmp==0:
                    return 0
                airlist.append(tmp)
            if station in weather[time]:
                weatherlist.append(weather[time][station])
            else:
                tmp=findNear(weather,start,station)
                if tmp==0:
                    return 0
                weatherlist.append(tmp)
    return [airlist,weatherlist]
def deltatime(time):
    #计算时间差
    d=datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    start=datetime.datetime(2017,1,1)
    delta=d-start
    return delta.days
def gethour(time):
    #获取时间中的小时
    hours=time.split(' ')[1]
    hour=hours.split(':')[0]
    return float(hour)    
def to_float(s):
    if s==''or s=='\n':
            return 0
    return float(s)
def air_dict(file):
    #stationId,utc_time,PM2.5,PM10,NO2,CO,O3,SO2
    dp=autoload(file)
    if dp:
        return dp
    air={}
    timelist=[]
    stationlist=[]
    total_line=0
    valid_line=0
    total_time=0
    total_station=0
    with open(file,'r') as f:
        for index,line in enumerate(f.readlines()):
        
            total_line+=1
                            
            if index != 0:
                datas=line.split(',')
                station=datas[0]
                time=datas[1]
                pm25=to_float(datas[2])
                pm10=to_float(datas[3])
                no2=to_float(datas[4])
                co=to_float(datas[5])
                o3=to_float(datas[6])
                so2=to_float(datas[7])
                if pm25==0 and pm10==0 and no2==0:
                    continue
                valid_line+=1
                data=[station,time,pm25,pm10,no2,co,o3,so2]
                if time not in timelist:
                    timelist.append(time)
                if station not in stationlist:
                    stationlist.append(station)
                if time in air:
                    subdict=air[time]
                    if len(subdict) > total_station:
                        total_station = len(subdict)
                    subdict[station]=data
                else:
                    air[time]={station:data}
                    total_time+=1
    print("file has %d lines(%d valid), time has %d count, ranging from %s to %s, station num is %d" % (total_line,valid_line, total_time, timelist[0], timelist[-1], total_station))
    depressed=[air, timelist, stationlist]
    autosave(depressed,file)
    return depressed
def weather_dict(file):
    #stationName,longitude,latitude,utc_time,temperature,pressure,humidity,wind_direction,wind_speed
    weather=autoload(file)
    if weather:
        return weather
    weather={}
    timelist=[]
    stationlist=[]
    total_line=0
    with open(file,'r') as f:
        t0=time.clock()
        for index,line in enumerate(f.readlines()):
            if index > total_line:
                total_line=index
            if index != 0:
                datas=line.split(',')
                station=datas[0]
                longitude=to_float(datas[1])
                latitude=to_float(datas[2])
                time_t=datas[3]
                temperature=to_float(datas[4])
                pressure=to_float(datas[5])
                humidity=to_float(datas[6])
                wind_direction=to_float(datas[7])
                wind_speed=to_float(datas[8])
                data=[station,longitude,latitude,time_t,temperature,pressure,humidity,wind_direction,wind_speed]
                if time_t not in timelist:
                    timelist.append(time_t)
                if station not in stationlist:
                    stationlist.append(station)
                if time_t in weather:
                    subdict=weather[time_t]
                    subdict[station]=data
                else:
                    weather[time_t]={station:data}
                if index%100000==0:
                    t1=time.clock()
                    print('current line = %d, time pass %f' %(index,t1-t0))
                    t0=t1
    print("file has %d lines, time has %d count, ranging from %s to %s, station num is %d" % (total_line, len(timelist), timelist[0], timelist[-1], len(stationlist)))
    autosave(weather,file)
    return weather#,timelist,stationlist
def name_to_names(station,air_map,grid_map):
    if station in air_map:
        station_pos=air_map[station]
    else:
        print('air_map lost %s station'%station)
        return 0
    latitude=station_pos[0] #纬度
    longtitude=station_pos[1]#经度
    lamin=math.floor(10*latitude)/10
    lomin=math.floor(10*longtitude)/10
    lamax=lamin+0.1
    lomax=lomin+0.1
    lamin=str(round(lamin,1))
    lamax=str(round(lamax,1))
    lomin=str(round(lomin,1))
    lomax=str(round(lomax,1))
    if lomax=='116.39999999999999':
        print(longtitude)
        input()
    sub1={}
    sub2={}
    name0=''
    name1=''
    name2=''
    name3=''
    if lamin in grid_map:
        sub1=grid_map[lamin]
    else:
        print('lamin:%s not in grid_map'%lamin)
    if lamax in grid_map:
        sub2=grid_map[lamax]
    else:
        print('lamax:%s not in grid_map'%lamax)
    if lomin in sub1:
        name0=sub1[lomin]
    else:
        print('lomin:%s not in sub1'%lomin)
        print(sub1)
    if lomax in sub1:
        name1=sub1[lomax]
    else:
        print('lomax:%s not in sub1'%lomax)
        print(sub1)
    if lomin in sub2:
        name2=sub2[lomin]
    else:
        print('lomin:%s not in sub2'%lomin)
        print(sub2)
    if lomax in sub2:
        name3=sub1[lomax]
    else:
        print('lomax:%s not in sub2'%lomax)
        print(sub2)
    name0=grid_map[lamin][lomin]
    name1=grid_map[lamin][lomax]
    name2=grid_map[lamax][lomin]
    name3=grid_map[lamax][lomax]
    return name0,name1,name2,name3,latitude,longtitude
def average(n0,n1,n2,n3,la,lo):
    #utc_time,temperature,pressure,humidity,wind_direction,wind_speed
    la=10*(la-math.floor(10*la)/10)
    lo=10*(lo-math.floor(10*lo)/10)
    arg0=la*(1-lo)
    arg1=la*lo
    arg2=(1-la)*(1-lo)
    arg3=(1-la)*lo
    time=n0[3]
    #修复
    temperature=arg0*n0[4]+arg1*n1[4]+arg2*n2[4]+arg3*n3[4]
    pressure=arg0*n0[5]+arg1*n1[5]+arg2*n2[5]+arg3*n3[5]
    humidity=arg0*n0[6]+arg1*n1[6]+arg2*n2[6]+arg3*n3[6]
    wind_direction=arg0*n0[7]+arg1*n1[7]+arg2*n2[7]+arg3*n3[7]
    wind_speed=arg0*n0[8]+arg1*n1[8]+arg2*n2[8]+arg3*n3[8]
    #third 替换两项：风速和风向
    if wind_direction < 0 or wind_direction > 360:
        print('weather wind_direction is %f'%wind_direction)
        print('arg[%f,%f,%f,%f] [%f,%f,%f,%f]'%(arg0,arg1,arg2,arg3,n0[7],n1[7],n2[7],n3[7]))
        input()
    east_west=wind_speed*math.sin(wind_direction/180*math.pi)
    south_north=-wind_speed*math.cos(wind_direction/180*math.pi)
    return [time,temperature,pressure,humidity,east_west,south_north]

def chazhi(stationlist,grid_dict,air_map,grid_map):
    # input: air station, grid's air dict, air station [name,(x,y)]mapping, grid point [name,(x,y)]mapping,
    # output: station's air dict
    #airstation=autoload('data/weather_of_air_station.***')
    if airstation!=0:
        return airstation
    airstation={}
    
    for time in grid_dict:
        if not time in airstation:
            airstation[time]={}
        for station in stationlist:
            n0,n1,n2,n3,la,lo=name_to_names(station,air_map,grid_map)
            temp=[station]
            temp+=average(grid_dict[time][n0],grid_dict[time][n1],grid_dict[time][n2],grid_dict[time][n3],la,lo)
            airstation[time][station]=temp
    autosave(airstation,'data/weather_of_air_station.***')
    return airstation
def get_air_station_mapping(file):
    namelist=[]
    mapping={}
    with open(file,'r') as f:
        for it in f.readlines():
            i=it.split(',')
            station=i[0]
            latitude=float(i[2])
            longtitude=float(i[1])
            if station not in namelist:
                namelist.append(station)
            if station not in mapping:
                mapping[station]=[latitude,longtitude]
    return namelist,mapping
def get_grid_mapping(file):
    mapping={}
    with open(file,'r') as f:
        for line in f.readlines():
            data=line.split(',')
            name=data[0]
            latitude=str(round(float(data[1]),1))
            longtitude=str(round(float(data[2]),1))
            if latitude not in mapping:
                mapping[latitude]={longtitude:name}
            else:
                mapping[latitude][longtitude]=name

    return mapping
if __name__=='__main__':
    t0=time.clock()
    dp=air_dict(air_file)
    air=dp[0]
    timelist=dp[1]
    stationlist=dp[2]
    weather=weather_dict(weather_file)
    stationlist,air_station_map=get_air_station_mapping(station_mapping_file)
    grid_dict_map=get_grid_mapping(grid_mapping_file)
    air_weather_dict=chazhi(stationlist,weather,air_station_map,grid_dict_map)
    feed_data=[]
    cnt=0
    t1=time.clock()
    print('start use %f seconds'%(t1-t0))
    t0=t1
    
    for time_t in timelist:
        data=query(air_weather_dict,air,time_t,stationlist)
        if data != 0:
            feed_data.append(data)
            cnt+=1
            if cnt%1000==0:
                t1=time.clock()
                print('add %d item in feed_data, use %f seconds'%(cnt,t1-t0))
                t0=t1
    #you can use autosave below
    autosave(feed_data,'data/drillup_data.csv')
            
