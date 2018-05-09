#
# Beijing_historical_meo_grid.csv 时间[2017-1-1:2018-3-27] 地点[grid 0:650]
# air
# air格式：
# stationId,utc_time,PM2.5,PM10,NO2,CO,O3,SO2
# weather格式：
# stationName,longitude,latitude,utc_time,temperature,pressure,humidity,wind_direction,wind_speed
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
def air_dict(file,tp):
    #stationId,utc_time,PM2.5,PM10,NO2,CO,O3,SO2
    #id,time,station id,pm2.5,pm10
    dp=autoload(file)
    if dp:
        return dp
    air={}
    timelist=[]
    stationlist=[]
    with open(file,'r') as f:
        for index,line in enumerate(f.readlines()):              
            if index != 0:
                datas=line.split(',')
                if tp==1:
                    station=datas[0]
                    time=datas[1]
                    pm25=to_float(datas[2])
                    pm10=to_float(datas[3])
                    o3=to_float(datas[6])
                else:
                    station=datas[2]
                    ori=datas[1].replace('/','-')
                    tt=ori.split(' ')
                    hour=int(tt[1].split(':')[0])
                    time=tt[0]+' %02d:00:00'%hour
                    pm25=to_float(datas[3])
                    pm10=to_float(datas[4])
                
                if pm25==0 and pm10==0:
                    continue
                if tp==1:
                    data=[station,time,pm25,pm10,o3]
                else:
                    data=[station,time,pm25,pm10]
                if time not in timelist:
                    timelist.append(time)
                if station not in stationlist:
                    stationlist.append(station)
                if time in air:
                    subdict=air[time]
                    subdict[station]=data
                else:
                    air[time]={station:data}
    print("time has %d count, ranging from %s to %s, station num is %d" % (len(timelist), timelist[0], timelist[-1], len(stationlist)))
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
                if len(datas)<=8:
                    wind_speed=0
                else:
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
    airstation={}
    for time in grid_dict:
        if not time in airstation:
            airstation[time]={}
        for station in stationlist:
            n0,n1,n2,n3,la,lo=name_to_names(station,air_map,grid_map)
            temp=[station]
            if time in grid_dict:
                sts=grid_dict[time]
            else:
                continue
            if n0 in sts and n1 in sts and n2 in sts and n3 in sts:
                temp+=average(grid_dict[time][n0],grid_dict[time][n1],grid_dict[time][n2],grid_dict[time][n3],la,lo)
                airstation[time][station]=temp
                
    autosave(airstation,'data/weather_of_air_station.***')
    return airstation
def get_air_station_mapping(file):
    namelist=[]
    mapping={}
    with open(file,'r') as f:
        if file=='data/London_AirQuality_Stations.csv':
            for line in f.readlines():
                words=line.split(',')
                if words[2]!='TRUE':
                    continue
                name=words[0]
                la=float(words[4])
                lo=float(words[5])
                if not name in namelist:
                    namelist.append(name)
                if not name in mapping:
                    mapping[name]=[la,lo]
            return namelist,mapping
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
weather_file_1='data/Beijing_historical_meo_grid.csv'
weather_file_2='data/London_historical_meo_grid.csv'
air_file_1='data/beijing_17_18_aq.csv'
air_file_2='data/London_historical_aqi_forecast_stations_20180331.csv'
station_mapping_file_1='data/beijingairmapping.csv'
station_mapping_file_2='data/London_AirQuality_Stations.csv'
grid_mapping_file_1='data/Beijing_grid_weather_station.csv'
grid_mapping_file_2='data/London_grid_weather_station.csv'
if __name__=='__main__':
    t0=time.clock()
    dp_1=air_dict(air_file_1,1)
    air_1=dp_1[0]
    timelist_1=dp_1[1]
    stationlist_1=dp_1[2]
    weather_1=weather_dict(weather_file_1)
    stationlist_1,air_station_map_1=get_air_station_mapping(station_mapping_file_1)
    grid_dict_map_1=get_grid_mapping(grid_mapping_file_1)
    #weather_of_airstation_1=chazhi(stationlist_1,weather_1,air_station_map_1,grid_dict_map_1)
    feed_data_1=[]
    cnt=0
    t1=time.clock()
    print('start use %f seconds'%(t1-t0))
    t0=t1
    
##    for time_t in timelist_1:
##        data=query(weather_of_airstation_1,air_1,time_t,stationlist_1)
##        if data != 0:
##            feed_data_1.append(data)
##            cnt+=1
##            if cnt%1000==0:
##                t1=time.clock()
##                print('add %d item in feed_data, use %f seconds'%(cnt,t1-t0))
##                t0=t1
##    #you can use autosave below
##    autosave(feed_data_1,'data/beijing_data.csv')

    t0=time.clock()
    dp_2=air_dict(air_file_2,2)
    air_2=dp_2[0]
    timelist_2=dp_2[1]
    stationlist_2=dp_2[2]
    weather_2=weather_dict(weather_file_2)
    stationlist_2,air_station_map_2=get_air_station_mapping(station_mapping_file_2)
    grid_dict_map_2=get_grid_mapping(grid_mapping_file_2)
    weather_of_airstation_2=chazhi(stationlist_2,weather_2,air_station_map_2,grid_dict_map_2)
    feed_data_2=[]
    cnt=0
    t1=time.clock()
    print('start use %f seconds'%(t1-t0))
    t0=t1
    
    for time_t in timelist_2:
        data=query(weather_of_airstation_2,air_2,time_t,stationlist_2)
        if data != 0:
            feed_data_2.append(data)
            cnt+=1
            if cnt%1000==0:
                t1=time.clock()
                print('add %d item in feed_data_2, use %f seconds'%(cnt,t1-t0))
                t0=t1
    #you can use autosave below
    autosave(feed_data_2,'data/london_data.csv')
