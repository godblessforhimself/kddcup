#对air数据进行清洗
#将数据整理成day的数据
#先看看平均有效率能有多少
from datetime import datetime,date,timedelta
import time,pickle,os,math
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
min_valid=0.8*24
standard=0
labels=['station','utctime','PM2.5','PM10','NO2','CO','O3','SO2']
def autoload(file):
    f=file.split('.')
    store=f[0]
    if os.path.exists(store):
        with open(store,'rb') as f:
            print('load from %s'%store)
            return pickle.load(f)
    return 0
def autosave(obj,file):
    with open(file,'wb') as f:
        print('save to %s'%file)
        pickle.dump(obj,f)
def time_to_day(times):
    #utc_time转换成元素是'2017-01-01'的list
    ret=[]
    for item in times:
        former=item.split(' ')[0]
        if not former in ret:
            ret.append(former)
    return ret
def wash(data,day,station,l,r):
    #data=[[],0,...[]]
    #data[l] ... data[r] r-l+1
    for j in range(l,r+1):
        start=0
        end=0
        while 1:
            if data[start]==0 or data[start][j]==0:
                if end>=24:
                    break
                if data[start]==0:
                    data[start]=[station,day+' %02d:00:00'%start,0,0,0,0,0,0]
                end=start
                while 1:
                    end+=1
                    if end>=24:
                        break
                    if data[end]!=0 and data[end][j]!=0:
                        break
                    elif data[end]==0:
                        data[end]=[station,day+' %02d:00:00'%end,0,0,0,0,0,0]
                for i in range(start,end):
                    if start>0 and end<24:
                        data[i][j]=(data[end][j]-data[start-1][j])*(i+1-start)/(end-start+1)+data[start-1][j]
                    elif end<24:
                        data[i][j]=data[end][j]
                    elif start>0:
                        data[i][j]=data[start-1][j]
                    else:
                        print('wash error [%s,%s] '%(day,labels[j]))#wash error means:一天中24项都为0
                        #data[i][j]=0
                        break
                        
            else:
                start+=1
                if start>=24:
                    break
def air_to_day(air,day,station):
    day_data=[]
    valid=0
    for hour in range(0,24):
        temp=day+' %02d:00:00'%hour
        if not temp in air:
            day_data.append(0)
        elif not station in air[temp]:
            day_data.append(0)
        else:
            day_data.append(air[temp][station])
            valid+=1
    if valid>min_valid:
        wash(day_data,day,station,2,7)
    else:
        return 0
    return [day_data,valid]
def day_station(air,days,station):
    #form='%Y-%m-%d'
    #start=datetime.strptime(day,form)
    ret=[]
    valid=[]
    index=0
    for day_t in days:
        #day_t=(start+timedelta(days=i)).strftime(form)
        RV=air_to_day(air,day_t,station)
        if RV != 0:
            ret.append(RV[0])
            valid.append(RV[1])
            index+=1
    return ret,valid
def add_to(dst,t,station,data):
    dic=dst[0]
    times=dst[1]
    stations=dst[2]
    if not t in dic:
        dic[t]={station:data}
    else:
        dic[t][station]=data
    if not t in times:
        times.append(t)
    if not station in stations:
        stations.append(station)
def vir(days,filedir):
    for i in range(2,8):
        fig=plt.figure(i)
        savename=''
        for day in days:
            if savename=='':
                dirs=filedir+'/'+labels[i]
                if not os.path.exists(dirs):
                    os.mkdir(dirs)
                savename=dirs+'/'+day[0][1].replace(' ','_').replace(':','_')+'.png'
            to_show=[]
            for hour in range(0,24):
                to_show.append(day[hour][i])
            #This is to average to_show to 1
            
            if standard:
                if sum(to_show)==0:
                    to_show=[1]*24
                to_show=[i*len(to_show)/sum(to_show) for i in to_show]
            #You can comment out the line above to see real data from pictures in /virtualize
            plt.plot(range(0,24),to_show)
        plt.xlabel('hour of the day')
        plt.ylabel('the density of'+labels[i])
        plt.savefig(savename)
        plt.close(i)
def virtualize(datas,filedir):
    #this function create pictures
    if not os.path.exists(filedir):
        os.makedirs(filedir)
        print('dir %s has created!'%filedir)
    t0=time.clock()
    arrays=data_split_n(datas,15)       #important line,the number arg means how many continuous days are there to be in one picture!
    for days in arrays:
        vir(days,filedir)
    print('virtualize finish %f s'%(time.clock()-t0))
    #end of virtualize
def data_split_n(data,n):
    total=len(data)
    l=math.ceil(total/n)
    ret=[]
    for i in range(0,l):
        tmp=[]
        for j in range(0,n):
            if (i*n+j)<total:
                tmp.append(data[i*n+j])
        ret.append(tmp)
    return ret
def get_useful_data(dp,itemlist):
    #labels_index=['station','utctime','PM2.5','PM10','NO2','CO','O3','SO2']
    #             [       0         1       2      3     4    5    6     7 ]
    #get data that doesn't contain zero item
    #input:dp & the list of indexed data you want to use
    #output:dp_new, only contains none zero data in itemlist defined dimensions
    #dp is a list of [airdict, timelist, stationlist]
    
    # '_s' means the source data, '_d' means the destination data.
    air_s=dp[0]
    time_s=dp[1]
    station_s=dp[2]
    dp_new=[{},[],[]]
    out='[ '
    itlist=[]
    for it in itemlist:
        if it>=0 and it<8:
            out+=labels[it]+'  '
            itlist.append(it)
        else:
            print('itemlist %d not in range(0,8)'%(it))
    out+=']'
    print('generating dict of %s'%out)
    t0=time.clock()
    for time_t in time_s:
        if time_t in air_s:
            for station in station_s:
                if station in air_s[time_t]:
                    valid=1
                    data=air_s[time_t][station]
                    tmp_data=[]
                    for i in itlist:
                        if data[i]==0:
                            valid=0
                            break
                        else:
                            tmp_data.append(data[i])
                    if valid!=0:
                        add_to(dp_new,time_t,station,tmp_data)
    print('end of generating dict of %s, time = %f'%(out,time.clock()-t0))
    return dp_new
if __name__=='__main__':
    airp='data/beijing_17_18_aq'
    virdir='./virtualize/actual'
##    washed_data=autoload('data/washed_air_17_18') #for test
##    tmp=get_useful_data(washed_data,[0,1,2])
    
    #standard定义在开头，set则virtualize的数据平均值定为1,reset则显示原始数据
    if standard:
        virdir='./virtualize/standard'
    #原始数据
    airinfo=autoload(airp)
    air=airinfo[0]
    times=airinfo[1]
    stations=airinfo[2]
    days=time_to_day(times)
    washed_data=[{},[],[]]
    #处理过后的数据
    with open('data/valid.txt','w') as f:
        for station in stations:
            data,valid=day_station(air,days,station)
            f.write('station:'+station+'\n\t'+str(valid)+'\n')
            for day in data:
                for hour in day:
                    time_t=hour[1]
                    add_to(washed_data,time_t,station,hour)
            #virtualize(data,virdir+'/'+station) #if you don't want to generate pictures, comment out this line. It costs almost all time.#
    autosave(washed_data,'data/washed_air_17_18')
    tmp=get_useful_data(washed_data,[0,1,2])
    autosave(tmp,'data/pm2.5_17_18')    #a example of store pm2.5 data



    
