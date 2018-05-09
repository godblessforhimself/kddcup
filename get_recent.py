import requests,math
from datetime import datetime,date,timedelta
station_beijing='data/beijingairmapping.csv'    #every line is 'name','longtitude','latitude'
grid_beijing='data/Beijing_grid_weather_station.csv' #every line is 'name','latitude','longtitude'
station_london='data/londonairmapping.csv'    #every line is 'name','latitude','longtitude'
grid_london='data/London_grid_weather_station.csv' #every line is 'name','latitude','longtitude'
def name_to_names(station,air_map,grid_map):
    if station in air_map:
        station_pos=air_map[station]
    else:
        print('air_map lost %s station'%station)
        return 0
    latitude=station_pos[0] #纬度 str
    longtitude=station_pos[1]#经度
    lamin=math.floor(10*float(latitude))/10
    lomin=math.floor(10*float(longtitude))/10
    lamax=lamin+0.1
    lomax=lomin+0.1
    lamin=str(round(lamin,1))
    lamax=str(round(lamax,1))
    lomin=str(round(lomin,1))
    lomax=str(round(lomax,1))
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

    if lomax in sub1:
        name1=sub1[lomax]
    else:
        print('lomax:%s not in sub1'%lomax)
    if lomin in sub2:
        name2=sub2[lomin]
    else:
        print('lomin:%s not in sub2'%lomin)
    if lomax in sub2:
        name3=sub1[lomax]
    else:
        print('lomax:%s not in sub2'%lomax)
    name0=grid_map[lamin][lomin]
    name1=grid_map[lamin][lomax]
    name2=grid_map[lamax][lomin]
    name3=grid_map[lamax][lomax]
    return name0,name1,name2,name3,float(latitude),float(longtitude)
def build_dict(text):
    dic={}
    lines=text.replace('\r','').split('\n')
    l=len(lines)
    #'station,time,temperature,pressure,humidity,wind_x,wind_y':
    if lines[0].find('forecast')>=0:
        for i in range(1,l):
            if lines[i]=='':
                continue
            datas=lines[i].split(',')
            station=datas[1]
            time=datas[2]
            wind_speed=float(datas[7])
            wind_direction=float(datas[8])
            x=wind_speed*math.sin(wind_direction/180*math.pi)
            y=-wind_speed*math.cos(wind_direction/180*math.pi)
            data=[float(datas[4]),float(datas[5]),float(datas[6]),x,y]
            if not time in dic:
                dic[time]={station:data}
            else:
                dic[time][station]=data
    else:
        for i in range(1,l):
            if lines[i]=='':
                continue
            datas=lines[i].split(',')
            station=datas[1]
            time=datas[2]
            wind_speed=float(datas[8])
            wind_direction=float(datas[7])
            x=wind_speed*math.sin(wind_direction/180*math.pi)
            y=-wind_speed*math.cos(wind_direction/180*math.pi)
            data=[float(datas[4]),float(datas[5]),float(datas[6]),x,y]
            if not time in dic:
                dic[time]={station:data}
            else:
                dic[time][station]=data
        
    return dic
def get_recent_weather(hour_n,current_time,city):
    #得到需要预测的时间段以及在那之前一段时间北京伦敦各个站点天气数据的程序
    #current_time-hour_n,current_time+48
    #current_time 2018-04-24-00
    #city='Beijing' or 'London'
    #return [prev_station_weather,future_station_weather]
    #station,time,temperature,pressure,humidity,wind_x,wind_y
    datetime_time=datetime.strptime(current_time, '%Y-%m-%d-%H')
    start_time=(datetime_time-timedelta(hours=hour_n)).strftime('%Y-%m-%d-%H')
    if city=='Beijing':
        ct='bj'
    else:
        ct='ld'
    prev='https://biendata.com/competition/meteorology/'+ct+'_grid/'+start_time+'/'+current_time+'/2k0d1d8'
    future='http://kdd.caiyunapp.com/competition/forecast/'+ct+'/'+current_time+'/2k0d1d8'
    prev_grid=requests.get(prev).text
    future_grid=requests.get(future).text
    prev_grid_dict=build_dict(prev_grid)
    future_grid_dict=build_dict(future_grid)
    with open(current_time.replace('-','_')+'_prev_'+str(hour_n)+'.csv','w') as f:
        f.write(prev_grid)
    with open(current_time.replace('-','_')+'_future_48.csv','w') as f:
        f.write(future_grid)
    #station_name -> station_location -> the nearst four grid location
    #    -> four grid name -> four grid data -> station data
    stations=[]
    name_location={}
    location_grid={}
    if ct=='bj':
        with open(station_beijing,'r') as f:
            for line in f.readlines():
                items=line.split(',')
                name=items[0]
                longtitude=items[1]
                latitude=items[2]
                name_location[name]=[latitude,longtitude]
                stations.append(name)
        with open(grid_beijing,'r') as f:
            for line in f.readlines():
                items=line.split(',')
                name=items[0]
                longtitude=str(float(items[2]))
                latitude=str(float(items[1]))
                if not latitude in location_grid:
                    location_grid[latitude]={longtitude:name}
                else:
                    location_grid[latitude][longtitude]=name
    else:
        with open(station_london,'r') as f:
            for line in f.readlines():
                items=line.split(',')
                name=items[0]
                longtitude=items[2]
                latitude=items[1]
                name_location[name]=[latitude,longtitude]
                stations.append(name)
        with open(grid_london,'r') as f:
            for line in f.readlines():
                items=line.split(',')
                name=items[0]
                longtitude=str(float(items[2]))
                latitude=str(float(items[1]))
                if not latitude in location_grid:
                    location_grid[latitude]={longtitude:name}
                else:
                    location_grid[latitude][longtitude]=name
    prev_ret={}
    future_ret={}
    for i in range(0,hour_n):
        time=(datetime_time-timedelta(hours=hour_n-i)).strftime('%Y-%m-%d %H:%M:%S')
        if time in prev_grid_dict:

            for station in stations:
                n0,n1,n2,n3,la,lo=name_to_names(station,name_location,location_grid)
                station_data=[0,0,0,0,0]
                if n0 in prev_grid_dict[time] and n1 in prev_grid_dict[time] and n2 in prev_grid_dict[time] and n3 in prev_grid_dict[time]:

                    data0=prev_grid_dict[time][n0]
                    data1=prev_grid_dict[time][n1]
                    data2=prev_grid_dict[time][n2]
                    data3=prev_grid_dict[time][n3]
                    la=10*(la-math.floor(10*la)/10)
                    lo=10*(lo-math.floor(10*lo)/10)
                    arg0=la*(1-lo)
                    arg1=la*lo
                    arg2=(1-la)*(1-lo)
                    arg3=(1-la)*lo
                    for j in range(0,5):
                        station_data[j]=arg0*data0[j]+arg1*data1[j]+arg2*data2[j]+arg3*data3[j]
                    if time in prev_ret:
                        prev_ret[time][station]=station_data
                    else:
                        prev_ret[time]={station:station_data}
    for i in range(0,48+1):
        time=(datetime_time+timedelta(hours=i)).strftime('%Y-%m-%d %H:%M:%S')
        if time in future_grid_dict:
            for station in stations:
                n0,n1,n2,n3,la,lo=name_to_names(station,name_location,location_grid)
                station_data=[0,0,0,0,0]
                if n0 in future_grid_dict[time] and n1 in future_grid_dict[time] and n2 in future_grid_dict[time] and n3 in future_grid_dict[time]:
                    
                    data0=future_grid_dict[time][n0]
                    data1=future_grid_dict[time][n1]
                    data2=future_grid_dict[time][n2]
                    data3=future_grid_dict[time][n3]
                    la=10*(la-math.floor(10*la)/10)
                    lo=10*(lo-math.floor(10*lo)/10)
                    arg0=la*(1-lo)
                    arg1=la*lo
                    arg2=(1-la)*(1-lo)
                    arg3=(1-la)*lo
                    
                    for j in range(0,5):
                        station_data[j]=arg0*data0[j]+arg1*data1[j]+arg2*data2[j]+arg3*data3[j]
                    if time in prev_ret:
                        future_ret[time][station]=station_data
                    else:
                        future_ret[time]={station:station_data}
    return [prev_ret,future_ret]



if __name__=='__main__':
    data1=get_recent_weather(24,'2018-05-09-08','Beijing')
    with open('bj.txt','w') as f:
        prev=data1[0]
        future=data1[1]
        f.write('prev:')
        for key in prev:
            f.write(key+'\n')
        f.write(str(prev))
        f.write('\nfuture:')
        for key in future:
            f.write(key+'\n')
        f.write(str(future))
    data2=get_recent_weather(24,'2018-05-09-08','London')
    with open('ld.txt','w') as f:
        prev=data2[0]
        future=data2[1]
        f.write('prev:')
        for key in prev:
            f.write(key+'\n')
        f.write(str(prev))
        f.write('\nfuture:')
        for key in future:
            f.write(key+'\n')
        f.write(str(future))
