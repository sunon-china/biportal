

'''
@Author Feng ZHAO
@Date 2018/07/02
@Purpose Cron jobs 

ChangeLog
2018/07/02 Feng ZHAO Initial Draft
2018/07/02 Feng ZHAO Class PXB & Utils  debug comand = /usr/local/python/bin/python3 /www/python/biportal/manage.py crontab run 9da3a107c107d7271341ba543a223a78
2018/07/04 Feng ZHAO Using Django model to get queryset 
2018/07/10 Feng ZHAO Synchronize root company 
2018/07/11 Feng ZHAO Synchronize organizations
2018/07/12 Feng ZHAO Synchronize students 
2018/07/18 Dong CHEN add class Maycur class CxOracle
'''

class Pxb():

    #Construction function
    def __init__(self):
        from mdm.models import Company 
        from mdm.models import Department 
        from mdm.models import Employee 
        from mdm.models import Job_Data 

        self.company = Company
        self.department = Department
        self.employee = Employee 
        self.jobData = Job_Data 
        self.utils = Utils()


    #Main function for post company, org, employee to 91PXB
    def main(self):
        accessTokenUrl = 'http://www.91pxb.com/api/AccessToken/Get'
        synchronizeRootCompanyUrl = 'http://www.91pxb.com/api/Companies/SynchronizeRootCompany' 
        synchronizeOrganizationsUrl = 'http://www.91pxb.com/api/Companies/SynchronizeOrganizations'
        synchronizeStudentsUrl = 'http://www.91pxb.com/api/Employees/SynchronizeStudents'

        auth = {'appId': 'hHvKkSxRt113b690', 'appSecret': '98F2709A98B91FD3BEEFB32697DD144971246D0A'}
        header = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}


        accessToken = self.getAccessToken(accessTokenUrl, auth, header)
        if (accessToken['err'] == 0):
            header['ACCESS-TOKEN'] = accessToken['data']

            #Synchronize root company
            rootCompany = self.getRootCompany()
            company = {}
            company['code'] = rootCompany[0]['code']
            company['organization_name'] = rootCompany[0]['name']
            updateReturn = self.synchronizeRootCompany(synchronizeRootCompanyUrl, company, header)
            if (updateReturn['err'] == 0):
                print(str(updateReturn['err']) + ' ' +str(updateReturn['data']))
            else:
                print(str(updateReturn['err']) + ' ' + updateReturn['data'])

          
            #Synchronize organization
            departments = self.getDepartments()
            organizations = []
            for d in departments:
                if (d['parent_dept_key__code'] == ''):
                    #parent_code = rootCompany[0]['code']
                    #For test use
                    parentCode = 'A0001' 
                else:
                    parentCode = d['parent_dept_key__code']
                organizations.append({
                    'code': d['code'],
                    'organization_name': d['name'],
                    'parent_code': parentCode
                })
            #print(organizations)
            updateReturn = self.synchronizeOrganizations(synchronizeOrganizationsUrl, organizations, header)
            if (updateReturn['err'] == 0):
                print(str(updateReturn['err']) + ' ' +str(updateReturn['data']))
            else:
                print(str(updateReturn['err']) + ' ' + updateReturn['data'])

            
            #Synchronize student 
            employees = self.getEmployees()
            '''
            updateReturn = self.synchronizeStudents(synchronizeStudentsUrl, employees, header)
            if (updateReturn['err'] == 0):
                print(str(updateReturn['err']) + ' ' +str(updateReturn['data']))
            else:
                print(str(updateReturn['err']) + ' ' + updateReturn['data'])
            '''

        #Get access token error
        else:
            print(str(accessToken['err']) + ' ' + accessToken['data'])
        

    #Get 91PXB access token    
    def getAccessToken(self, url, post, header):
        return self.utils.apiCall(url, post, header)

    #Post company to 91PXB
    def synchronizeRootCompany(self, url, post, header):
        return self.utils.apiCall(url, post, header)

    #Get company from MDM db
    def getRootCompany(self):
        companies = self.company.objects.filter(status = 2, effective_flag = 0, parent_company_key = '').values('code', 'name')
        return companies


    def getDepartments(self):
        departments = self.department.objects.filter(status = 2, effective_flag = 0).values('code', 'name', 'parent_dept_key__code')
        #print(departments.query)
        return departments

    def synchronizeOrganizations(self, url, post, header):
        return self.utils.apiCall(url, post, header)

    def getEmployees(self):
        employees = self.jobData.objects.filter(effective_flag = 0, empl_key__effective_flag = 0, dept_key__effective_flag = 0, pos_key__effective_flag = 0).values('empl_key__code', 'empl_key__name', 'empl__sex', 'empl__mobile', 'dept_key__name', 'pos_key__name')
        print(employees.query)
        #employees = [{'code': '000001', 'chinese_name': '赵峰', 'employee_id': '000001', 'default_code': '04007', 'organization_codes': ['04007']}]
        print(employees)
        return employees

    def synchronizeStudents(self, url, post, header):
        return self.utils.apiCall(url, post, header)



class Maycur():

    def __init__(self):
        self.utils = Utils()
        self.cxoracle = CxOracle('cbs','sunon$2018','172.16.59.182',1521,'sunon')
        
    #从每刻获取数据存入CBS中间表
    def main(self):
        import time
        import cx_Oracle
        
        accessTokenUrl = 'https://uat.maycur.com/api/openapi/auth/login'
        PaymentUrl = 'https://uat.maycur.com/api/openapi/paymenttransaction/list'
        appCode = 'UI180315SUNO100'
        secret = 'Lqecp6GGSajUxnNTMEeA966bxVXym6UzjTp26zccMMRBgBrAX4m4s9anpfuJkVkz'
        timestamp = str(int(time.time()*1000))
        #加密
        res = self.getSh256(secret +':'+ appCode +':'+ timestamp)
        auth = {'appCode': appCode,'timestamp':timestamp, 'secret': res}
        header = {'content-type':'application/json'}
    
        accessToken = self.getAccessToken(accessTokenUrl, auth, header)

        if (accessToken['code'] == 'ACK'):
            sql = "select max(cast(erp_payment_id as int )) as seq from authorization_to_payment"
            mm = self.cxoracle.Query(sql)
            sequence = mm[0][0]
            if sequence == None:
                sequence = -1
            data = accessToken.get('data')
            header['entCode'] = data.get('entCode')
            header['tokenId'] = data.get('tokenId')
            data = {"timestamp": timestamp, "data": {"sequence": sequence}}
            
            result = self.getPayment(PaymentUrl, data, header)
            if (result['code'] == 'ACK'):

                Paymentdata = result.get('data')
                Paymentlist = []

                for i in range(0, len(Paymentdata)):

                    dict = Paymentdata[i]
                    sequence = dict['sequence']
                    payeeBankCode = dict['payeeBankCode']
                    payeeBankCardNO = dict['payeeBankCardNO']
                    paidAmount = dict['paidAmount']
                    if payeeBankCode == None or payeeBankCardNO == None:
                        continue
                    CHECK_CODE = self.getCheckcode(sequence,'Available',payeeBankCardNO,paidAmount)
                    list = (sequence,'Available','202','2',payeeBankCardNO,payeeBankCode,paidAmount,'报销',0,CHECK_CODE)
                    Paymentlist.append(list)
                insertsql = "insert into authorization_to_payment(ERP_PAYMENT_ID, RECORD_STATUS,PAYMENT_TYPE_ID,PAYMENT_METHOD_TYPE_ID,DEPOSIT_ACCOUNTS,DEPOSIT_BANK_TYPE,AMOUNT,PURPOSE,VERSION,CHECK_CODE)VALUES(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10)"
                self.cxoracle.Insert(insertsql,Paymentlist)
            else:
                print("请求失败")
            print("######################################################")
        else:
            print(accessToken['responseCode'] + accessToken['errorMessage'])
        

    def postMaycur(self):
        pass


    def getAccessToken(self, url, post, header):
        return self.utils.apiCall(url, post, header)

    def getPayment(self, url, data, header):
        return self.utils.apiCall(url, data, header)

    #获取check_code
    def getCheckcode(self,sequence,record_status,deposit_accounts,amount):
        #str = code+record_status+deposit_accounts+str(amount)
        s = 0
        for i in str(sequence)+record_status+deposit_accounts+str(amount):
            s = s +ord(i)
        s = s + 39*6
        CHECK_CODE = ((s % 999) * (s % 2184)) % 9999
        return CHECK_CODE

    def getSh256(self,res):
        return self.utils.Sha256(res)


class Utils():
    
    #Using python urllib to get or post 
    def apiCall(self, url, post, header):
        import urllib.request
        import urllib.parse
        post = self.json(post, 'encode')
        post = bytes(post,'utf8')
        request = urllib.request.Request(url, post, header)
        result = urllib.request.urlopen(request).read()
        return self.json(result, 'decode')
    
    #Json dumps and loads
    def json(self, data, jsonType):
        import json
        if (jsonType == 'encode'):
            return json.dumps(data)
        elif (jsonType == 'decode'):
            return json.loads(data)
        else:
            return False

    #SHA256加密
    def Sha256(self,res):
        import hashlib
        sha256 = hashlib.sha256()
        sha256.update(res.encode('utf-8'))
        result = sha256.hexdigest()
        return result

import cx_Oracle
class CxOracle():


    def __init__(self ,user, pwd,host,port,service_name ):
        self._user = user
        self._pwd = pwd
        self._tns = cx_Oracle.makedsn(host,port,service_name)
        self._conn = None
        self._ReConnect()
    def _ReConnect(self ):
        if not self._conn :
            self._conn = cx_Oracle.connect (self._user, self._pwd,self._tns)
        else:
            pass
    def __del__(self ):
        if self. _conn:
            self ._conn. close()
            self ._conn = None
    def _NewCursor(self ):
        cur = self. _conn.cursor ()
        if cur:
            return cur
        else:
            print ("#Error# Get New Cursor Failed.")
        return None
    def _DelCursor(self , cur):
        if cur:
            cur .close()
    def Query(self , sql):
        rt = []
        cur = self. _NewCursor()
        if not cur:
            return rt
        cur .execute(sql)
        rt = cur.fetchall()
        self ._DelCursor(cur)
        return rt
  # 更新
    def Exec(self ,sql):
        rt = None
        cur = self. _NewCursor()
        if not cur:
            return rt
        rt = cur. execute(sql )
        self._conn.commit()
        self ._DelCursor(cur)
        return rt 
    #批量插入
    def Insert(self ,sql,param):
        rt = None
        cur = self. _NewCursor()
        if not cur:
            return rt
        rt = cur. executemany(sql,param)
        self._conn.commit()
        self ._DelCursor(cur)
        return rt

'''
def pxb():
    pxb = Pxb()
    pxb.main()
'''
def maycur():
    maycur = Maycur()
    maycur.main()


