def printMessage(prefix):
    def handler(x):
        ws,path,msg = [x.get(key) for key in ['ws','path','msg']]
        print(prefix,msg);
    return handler
