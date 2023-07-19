"""common function."""
from time import time
from datetime import datetime,date,timedelta
import jwt


errorCode={
        '0000':'Success',
        '1001':'Invalid Parameter',
		'1002':'Network Error',
		'1003':'Authorization Error',
		'10031':'Token Type Error',
		'1004':'Token Error',
		'1005':'DB Connection Error',
		'1006':'DB Empty Result Error',
		'1007':'Missing Parameter',	
		'1008':'Login Error',
		'1009':'Login Account or Password Error',		
		'2001':'Insert data failed',
		'2002':'Update data failed',
		'2003':'Delete data failed',
		'2004':'Query data failed',
		'2005':'Duplicate data failed',
		'3000':'Upload file success',
		'3001':'Upload file failed',
		'3002':'Duplicate file name',
		'3003':'Unknown file format',
		'3004':'Unknown file name',
		'3005':'Unknown Error',
		'3006':'Check File Success',
		'3007':'Check DB File Count Error',
		'3008':'Check Folder File Count Error',
		'3009':'Check Device SN Error',
		'3010':'Device is already in use',
		'3011':'Device Mapping Error',
		'4001':'Time out'
		}

def getTime():
    t=time()
    today = (int(round(t*1000)))
    return today

def msgresult(success,message,code,result,token):
    msg={"status":success,"message":message,"code":code,"result":result,"token":token}
    return msg

def checkJWT(getToken):
    defaultToken="compal021222725"
    try:
        if getToken is None:
            newMsg=msgresult(False,str(errorCode['1003']),'1003',"","")   
            return newMsg
        token_type, access_token = getToken.split(' ')
        if token_type != 'Bearer' or token_type is None:
        # 驗證token_type是否為Bearer
            newMsg=msgresult(False,str(errorCode['10031']),'10031',token_type,"") 
            return newMsg
        if access_token is not None:
            if access_token==defaultToken:
                newMsg=msgresult(True,str(errorCode['0000']),'0000',"","")   
                return newMsg
            else:    
                payload=jwt.decode(access_token,"compalapi0619",algorithms="HS256")  
                # print(payload)

                newMsg=msgresult(True,str(errorCode['0000']),'0000',"",payload)   
                return newMsg
    except jwt.ExpiredSignatureError:
        newMsg=msgresult(False,'Token Signature expired.','1004',"","") 
        return newMsg
    except jwt.InvalidTokenError:
        newMsg=msgresult(False,'Invalid Token.' ,'1004',"","") 
        return  newMsg