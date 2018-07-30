

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
        
    def main(self):
        import time
        timeStamp = str(int(time.time()*1000))
        header = self.getHeader(timeStamp)
        self.getPaymentall(timeStamp,header)        #获取每刻已导出支付流水至cbs中间表

        #self.getPaymentfailed(timeStamp,header)
        self.postPaymentstatus(header)              #回写支付状态给每刻

    #回写每刻支付成功或支付失败状态
    def postPaymentstatus(self,header):
        import time
 
        postMaycurUrl = 'https://uat.maycur.com/api/openapi/paymenttransaction/update'
   
        cbsData = self.getStatus1()
        #print(cbsData)

        if cbsData == [] :
            print("暂无数据需要回写每刻")
        else:
            for i in range(0, len(cbsData)):
                dataList = []
                paymentAccounts = cbsData[i][2]
                if paymentAccounts == None:
                    continue
                recordStatus = cbsData[i][1]
                PayDate = cbsData[i][3]
                errorMsg = cbsData[i][4]
                sequence = cbsData[i][5]
                erpPaymentId = cbsData[i][0]
                if recordStatus != 'Success':
                    recordStatus = 'PAY_FAIL'
                timeArray = time.strptime(PayDate, "%Y-%m-%d %H:%M:%S")
                #支付时间的时间戳:
                timeStamp = int(time.mktime(timeArray)*1000)
                list = ({"sequence":sequence,"paidDate":timeStamp,"payerBankAccount":paymentAccounts,"status":recordStatus,"errorMsg":errorMsg})
                #更新CBS中间表erp_comment1字段为"2"

                dataList.append(list)
                #当前时间的时间戳CBS_EXPORT_FAILED
                nowtimeStamp = int(time.time()*1000)
                data = {"timeStamp": nowtimeStamp, "data": dataList}
                result = self.postPayment(postMaycurUrl, data, header)
                if result['code'] == 'NACK':
                    continue
                self.updatePaymentFlag(erpPaymentId,'2')
                #print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')

    #post已导出状态给每刻
    def postExportstatus(self,timeStamp,header):

        postMaycurUrl = 'https://uat.maycur.com/api/openapi/paymenttransaction/update'
        #获取每刻回写到CBS的流水数据
        cbsData = self.getStatus0()
        dataList = []
        if cbsData == [] :
            print("无新增数据")
        else:
            for i in range(0, len(cbsData)):
                sequence = cbsData[i][5]          #流水号
                erp_payment_id = cbsData[i][0]    #唯一编号
                list = ({"sequence":sequence,"status":'CBS_EXPORTED'})
                dataList.append(list)
                self.updatePaymentFlag(erp_payment_id,'1')
            data = {"timestamp": timeStamp, "data": dataList}
            result = self.postPayment(postMaycurUrl, data, header)



    #获取带code、tokenid的header
    def getHeader(self,timeStamp):
        accessTokenUrl = 'https://uat.maycur.com/api/openapi/auth/login'
        #PaymentUrl = 'https://uat.maycur.com/api/openapi/paymenttransaction/list'
        appCode = 'UI180315SUNO100'
        secret = 'Lqecp6GGSajUxnNTMEeA966bxVXym6UzjTp26zccMMRBgBrAX4m4s9anpfuJkVkz'
        #加密
        res = self.getSh256(secret +':'+ appCode +':'+ timeStamp)
        auth = {'appCode': appCode,'timestamp':timeStamp, 'secret': res}
        header = {'content-type':'application/json'}
        accessToken = self.getAccessToken(accessTokenUrl, auth, header)
        if (accessToken['code'] == 'ACK'):
            data = accessToken.get('data')
            header['entCode'] = data.get('entCode')
            header['tokenId'] = data.get('tokenId')
        return header

    #获取每刻已导出的支付流水到CBS中间表
    def getPaymentall(self,timeStamp,header):
        PaymentUrl = 'https://uat.maycur.com/api/openapi/paymenttransaction/list'
        '''
        #'%\_%' escape nchr(92) 转义 _ 
        #sql = "select max(cast(erp_payment_id as int )) as seq from authorization_to_payment where  erp_payment_id  not like '%\_%' escape nchr(92) "
        sql = " select max(cast(erp_comment2 as int )) as seq from authorization_to_payment "
        mm = self.cxoracle.query(sql)
        sequence = mm[0][0]
        if sequence == None:
            sequence = -1
        #header = self.getHeader(timeStamp)
        '''
        data = {"timestamp": timeStamp, "data": {"sequence": -1}}
        result = self.getPayment(PaymentUrl, data, header)
        if (result['code'] == 'ACK'):

            paymentData = result.get('data')
            #print(paymentData)
            paymentList = []
            for i in range(0, len(paymentData)):
                dict = paymentData[i]
                sequence = dict['sequence']
                erpPaymentId = str(sequence)+timeStamp
                #print(erp_payment_id)
                payeeBankCode = dict['payeeBankCode']
                payeeBankCardNO = dict['payeeBankCardNO']
                paidAmount = dict['paidAmount']
                Amount = [str(paidAmount),int(paidAmount)][int(paidAmount)==paidAmount]
                payerBankAccount = dict['payerBankAccount']
                #payerBankAccount = '19082301040025838'
                payeeBankBranchNO = dict['payeeBankBranchNO']
                payeeName = dict['payeeName']
                acceptCcy = dict['acceptCcy']
                acceptCcy = self.currency(acceptCcy)
                payeeTargetBizCode = dict['payeeTargetBizCode']
                payeeBankBranchName = dict['payeeBankBranchName']
                reason = self.getReason(payeeTargetBizCode,header)
                if payeeBankCode == None or payeeBankCardNO == None or Amount == 0:
                    continue
                checkCode = self.getCheckCode(erpPaymentId,'Available',payeeBankCardNO,Amount,payerBankAccount)
                list = (erpPaymentId,'Available','401','2',payeeBankCardNO,payeeBankCode,paidAmount,reason,0,checkCode,payerBankAccount,payeeName,'5500',acceptCcy,payeeBankBranchNO,'0',sequence,payeeTargetBizCode,payeeBankBranchName)
                paymentList.append(list)
            #print(paymentList)
            insertSql = "insert into authorization_to_payment(erp_payment_id, record_status,payment_type_id,payment_method_type_id,deposit_accounts,deposit_bank_type,amount,purpose,version,check_code,payment_accounts,deposit_accounts_name,payment_cltnbr,currency_type,union_bank_number,erp_comment1,erp_comment2,erp_comment3,deposit_bank_name)VALUES(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17,:18,:19)"
            self.cxoracle.insert(insertSql,paymentList)
            print("######################################################")
            self.postExportstatus(timeStamp,header)     #回写已导出状态给每刻
        else:
            print("请求失败")
            print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    '''
    #获取支付失败的流水更新CBS中间表
    def getPaymentfailed(self,timeStamp,header):
        PaymentUrl = 'https://uat.maycur.com/api/openapi/paymenttransaction/list'
        #header = self.getHeader(timeStamp)
        #sql = " SELECT erp_payment_id FROM AUTHORIZATION_TO_PAYMENT   WHERE  RECORD_STATUS = 'Failed' and  erp_payment_id  not like '%\_' escape '\' "
        #sql = " SELECT erp_payment_id FROM AUTHORIZATION_TO_PAYMENT   WHERE  RECORD_STATUS = 'Failed' and  erp_payment_id  not like '%\_%' escape nchr(92) "
        sql = "select distinct erp_comment2 from authorization_to_payment a where a.cbs_last_update_time=(select max(cbs_last_update_time) from  authorization_to_payment b where      a.erp_comment2=b.erp_comment2 ) and record_status='Failed' "
        seq = self.cxoracle.query(sql)
        if seq == [] :
            print("无支付失败数据")
        else:
            for  i in range(0, len(seq)):
                sequence = seq[i][0]
                if sequence == None:
                    continue
                sequence = int(sequence) -1
                #data = {"timeStamp": timeStamp, "data": [{"sequence": sequence,"pageSize": 1 }]}
                data = {"timeStamp": timeStamp, "data": {"sequence": sequence,"pageSize": 1 }}
                result = self.getPayment(PaymentUrl, data, header)
                paymentData = result.get('data')
                #print(paymentData)
                paymentList = []
                dict = paymentData[0]
                #print(dict)
                sequence = dict['sequence']
                erpPaymentId = str(sequence)+timeStamp
                #print(erpPaymentId)
                payeeBankCode = dict['payeeBankCode']
                payeeBankCardNO = dict['payeeBankCardNO']
                paidAmount = dict['paidAmount']
                Amount = [str(paidAmount),int(paidAmount)][int(paidAmount)==paidAmount]
                #payerBankAccount = '19082301040025838'
                payerBankAccount = dict['payerBankAccount']
                payeeBankBranchNO = dict['payeeBankBranchNO']
                payeeName = dict['payeeName']
                acceptCcy = dict['acceptCcy']
                acceptCcy = self.currency(acceptCcy)
                payeeTargetBizCode = dict['payeeTargetBizCode']
                if payeeBankCode == None or payeeBankCardNO == None or Amount == 0:
                    continue
                checkCode = self.getCheckCode(erpPaymentId,'Available',payeeBankCardNO,Amount,payerBankAccount)
                list = (erpPaymentId,'Available','401','2',payeeBankCardNO,payeeBankCode,paidAmount,'报销',0,checkCode,payerBankAccount,payeeName,'5500',acceptCcy,payeeBankBranchNO,'1',sequence,payeeTargetBizCode)
                paymentList.append(list)
                #print(paymentList)
            insertsql = "insert into authorization_to_payment(erp_payment_id, record_status,payment_type_id,payment_method_type_id,deposit_accounts,deposit_bank_type,amount,purpose,version,check_code,payment_accounts,deposit_accounts_name,payment_cltnbr,currency_type,union_bank_number,erp_comment1,erp_comment2,erp_comment3)VALUES(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17,:18)"
            self.cxoracle.insert(insertsql,paymentList)
    '''
    def getAccessToken(self, url, post, header):
        return self.utils.apiCall(url, post, header)

    def getPayment(self, url, data, header):
        return self.utils.apiCall(url, data, header)

    def postPayment(self, url, data, header):
        return self.utils.apiCall(url, data, header)


    #计算校验码
    def getCheckCode(self,sequence,recordStatus,depositAccounts,amount,payerBankAccount):
        s = 0
        if payerBankAccount == None:
            string = str(sequence)+recordStatus+depositAccounts+str(amount)
        else:
            string = str(sequence)+recordStatus+depositAccounts+str(amount)+payerBankAccount  
        for i in string:
        #for i in str(0)+'Available'+'127876169497'+str(50.0)+'19082301040025838':
            s = s +ord(i)
        s = s + 39*6
        checkCode = ((s % 999) * (s % 2184)) % 9999
        return checkCode
    #加密
    def getSh256(self,res):
        return self.utils.Sha256(res)
    

    #获取CBS状态为0的支付流水
    def getStatus0(self):
        sql = "select  erp_payment_id,record_status,payment_accounts,cbs_last_update_time,cbs_comment,erp_comment2 from  authorization_to_payment where erp_comment1='0'  "
        result = self.cxoracle.query(sql)
        return result

    #获取CBS状态为1的支付流水
    def getStatus1(self):
        sql = "select  erp_payment_id,record_status,payment_accounts,cbs_last_update_time,cbs_comment,erp_comment2  from (select t.*,row_number() over(partition by t.erp_comment2 order by t.cbs_last_update_time desc) rn from authorization_to_payment t) c where rn = 1 and record_status  in ('Failed','Success') and erp_comment1='1' "
        result = self.cxoracle.query(sql)
        return result

    #每刻币种转换
    def currency(self,acceptCcy):
        return {
            'CNY': '10',
            #'b': 2,
            #'c': 3,
        }.get(acceptCcy,'error') 

    #更新CBS中间表erp_comment1标识     '1'表示已导出或导出失败  标识'2'表示支付成功或失败
    def updatePaymentFlag(self,erpPaymentId,type):
        if type == '1':  
            sql = "update authorization_to_payment set erp_comment1 = '1' where erp_payment_id = '"+erpPaymentId+"'"
        else:
            sql = "update authorization_to_payment set erp_comment1 = '2' where erp_payment_id = '"+erpPaymentId+"'"
        self.cxoracle.exec(sql)

    #获取报销事由
    def getReason(self,businessCode,header):
        import urllib.request
        import urllib.parse
        
        url = 'https://uat.maycur.com/api/openapi/report/personal/detail?businessCode='+businessCode
        entCode = header['entCode'] 
        tokenId = header['tokenId'] 
        request = urllib.request.Request(url)
        request.add_header('entCode',entCode)
        request.add_header('tokenId',tokenId)
        result = urllib.request.urlopen(request).read()
        result = self.utils.json(result,'decode')
        data = result['data'][0]
        reason = data['name']
        return reason


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
        self._reConnect()
    def _reConnect(self ):
        if not self._conn :
            self._conn = cx_Oracle.connect (self._user, self._pwd,self._tns)
        else:
            pass
    def __del__(self ):
        if self. _conn:
            self ._conn. close()
            self ._conn = None
    def _newCursor(self ):
        cur = self. _conn.cursor ()
        if cur:
            return cur
        else:
            print ("#Error# Get New Cursor Failed.")
        return None
    def _delCursor(self , cur):
        if cur:
            cur .close()
    def query(self , sql):
        rt = []
        cur = self. _newCursor()
        if not cur:
            return rt
        cur .execute(sql)
        #print(cur)
        rt = cur.fetchall()
        #print(rt)
        self ._delCursor(cur)
        return rt
  # 更新
    def exec(self ,sql):
        rt = None
        cur = self. _newCursor()
        if not cur:
            return rt
        rt = cur.execute(sql)
        self._conn.commit()
        self ._delCursor(cur)
        return rt 
    #批量插入
    def insert(self ,sql,param):
        rt = None
        cur = self. _newCursor()
        if not cur:
            return rt
        rt = cur. executemany(sql,param)
        self._conn.commit()
        self ._delCursor(cur)
        return rt 

'''
def pxb():
    pxb = Pxb()
    pxb.main()
'''
def maycur():
    maycur = Maycur()
    maycur.main()


