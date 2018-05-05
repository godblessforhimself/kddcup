#检查产生的数据是否正确
#把pickle保存的数据输出到csv中
import pickle,os
def autoload(file):
    if os.path.exists(file):
        with open(file,'rb') as f:
            print('load from %s'%file)
            return pickle.load(f)
    else:
        print('file %s not found!'%file)
def run():
    file=input('load data from?')
    data=autoload(file)
    outfile=input('input output file')
    if isinstance(data,dict):
        with open(outfile+'.csv','w') as f:
            for key in data:
                f.write(key+','+data[key]+'\n')
testin='data/drillup_data'
testout='data/drillup_vistualized'
if __name__=='__main__':
    
    file=testin
    data=autoload(file)
    outfile=testout
    if isinstance(data,dict):
        print('it is a dict')
        with open(outfile+'.csv','w') as f:
            for key in data:
                f.write(key+','+data[key]+'\n')
    elif isinstance(data,list):
        with open(outfile+'.csv','w') as f:
            for index,line in enumerate(data):
                f.write('%d:'%index+str(line)+'\n')
