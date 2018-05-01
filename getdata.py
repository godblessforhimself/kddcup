import requests,csv,datetime,time
url = 'https://biendata.com/competition/meteorology/bj/2018-04-01-0/2018-04-01-23/2k0d1d8'
airquality = 'data/beijing_17_18_aq.csv'
meo_grid='data/Beijing_historical_meo_grid.csv'
meteorology_grid = 'https://biendata.com/competition/meteorology/bj_grid/2018-04-03-0/2018-04-03-23/2k0d1d8'

def air_data(raw):
    #format: station,time,hour,pm25,pm10,no2,co,o3,so2
    #raw='aotizhongxin_aq,2017-01-01 14:00:00,453.0,467.0,156.0,7.2,3.0,9.0'
    #return ['aotizhongxin_aq', 0, 14.0, 453.0, 467.0, 156.0, 7.2, 3.0, 9.0]
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
    datas=raw.split(',')
    station=datas[0]
    time=datas[1]
    def to_float(s):
        if s==''or s=='\n':
            return 0
        return float(s)
    pm25=to_float(datas[2])
    pm10=to_float(datas[3])
    no2=to_float(datas[4])
    co=to_float(datas[5])
    o3=to_float(datas[6])
    so2=to_float(datas[7])
    return [station,deltatime(time),gethour(time),pm25,pm10,no2,co,o3,so2]
def read_air(file):
    air=[]
    #对每行调用get_data 并且插值0的数据
    with open(file, 'r') as f:
        for index,row in enumerate(f.readlines()):
            if index == 0:
                continue
            data=air_data(row)
            air.append(data)
    #process
    for index,data in enumerate(air):
        for con in data:
            if con == 0:
                print(index,end='')
                print(':'+str(data))
                break
    return ret

def read_meo(file):
    #[Name=[],longiti=[],lati=[],time=[],temp=[],pressure=[],humidity=[],wind_dir=[],wind_speed=[]]
    result=[]
    station_num=651
    def deltatime(time):
        #计算time-start的天数差
        d=datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        start=datetime.datetime(2017,1,1)
        delta=d-start
        return delta.days
    def gethour(time):
        #获取time中的小时
        hours=time.split(' ')[1]
        hour=hours.split(':')[0]
        return float(hour)
    with open(file,'r')as f:
        name=[]
        longitude=[]
        latitude=[]
        utc_time=[]
        temperature=[]
        pressure=[]
        humidity=[]
        wind_direction=[]
        wind_speed=[]
        for index,row in enumerate(f.readlines()):
            if index == 0:
                continue
            attrs=row.split(',')
            if len(attrs) < 9:
                print('len < 9:' + row)
                exit(0)
                return 0
            name.append(attrs[0])
            def to_float(s):
                if s==''or s=='\n':
                    return 0
                return float(s)
            longitude.append(to_float(attrs[1]))
            latitude.append(to_float(attrs[2]))
            utc_time.append(attrs[3])
            temperature.append(to_float(attrs[4]))
            pressure.append(to_float(attrs[5]))
            humidity.append(to_float(attrs[6]))
            wind_direction.append(to_float(attrs[7]))
            wind_speed.append(to_float(attrs[8]))
            if index%station_num==0:
                result.append([name,longitude,latitude,utc_time,temperature,pressure,humidity,wind_direction,wind_speed])
                name=[]
                longitude=[]
                latitude=[]
                utc_time=[]
                temperature=[]
                pressure=[]
                humidity=[]
                wind_direction=[]
                wind_speed=[]
            if len(result)%1000==0 and index%station_num==0:
                print(len(result))
    print('result len=%d'%len(result))
    return result
if __name__ == '__main__':
    #lis=read_air(airquality)
    tst=read_meo(meo_grid)
