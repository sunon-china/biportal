

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
<<<<<<< HEAD
2018/07/18 Dong CHEN add class Maycur class CxOracle
2018/10/16.Dong Chen add CBS支付方式变更为202,
2018/10/18.Dong Chen add 获取每刻中的公司支付账号
=======
2018/07/18 Dong CHEN add class Maycur
>>>>>>> a5296a69b2bdebce27493a213ff17f720096c026
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

        auth = {'appId': 'hHvKkSxRt113b690', 'appSecret': '9E1D83DDC64A55020068AEA3F894621A5EA424DB'}
        header = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}

        accessToken = self.getAccessToken(accessTokenUrl, auth, header)
        if (accessToken['err'] == 0):
            header['ACCESS-TOKEN'] = accessToken['data']

            #Synchronize root company
            rootCompany = self.getRootCompany()
            #print(rootCompany)
            company = {}
            company['code'] = rootCompany[0]['code']
            company['organization_name'] = rootCompany[0]['name']
            updateReturn = self.synchronizeRootCompany(synchronizeRootCompanyUrl, company, header)
            if (updateReturn['err'] == 0):
                print(str(updateReturn['err']) + ' ' +str(updateReturn['data']))
            else:
                print(str(updateReturn['err']) + ' ' + updateReturn['data'])
                self.utils.postEmail('系统提醒', '培训宝公司信息同步失败！', 'chendong@sunon-china.com')
            #Synchronize organization
            departments = self.getDepartments()
            #删除组织信息
            #detailReturn = self.postDeleteOrganization(departments, header)
            #print('departments',departments)
            #同步组织
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
                self.utils.postEmail('系统提醒', '培训宝组织信息同步失败！', 'chendong@sunon-china.com')
            
            #Synchronize student 

            employees = self.getEmployees()

#删除人员信息
            #self.postDeleteEmployee(employees, header)
#同步人员信息
            self.postUpdateEmployee(employees, header)
        #Get access token error
        else:
            print(str(accessToken['err']) + ' ' + accessToken['data'])
            self.utils.postEmail('系统提醒', '获取培训宝accessToken失败！', 'chendong@sunon-china.com')
        #send_mail('test', 'Here is the message.', 'noreply.bi@sunon-china.com ',['chendong@sunon-china.com'], fail_silently=False)
        #self.utils.postEmail('test','Here is the message.','chendong@sunon-china.com')

    #删除组织信息
    def postDeleteOrganization(self, departments, header):
        url = 'http://www.91pxb.com/api/Companies/DeleteOrganizations'
        organizationsList = []
        for d in departments:
            organizationsList.append({'code': d['code']})
        print(organizationsList)
        updateReturn = self.synchronizeOrganizations(url, organizationsList, header)
        if (updateReturn['err'] == 0):
            print(str(updateReturn['err']) + ' ' +str(updateReturn['data']))
        else:
            print(str(updateReturn['err']) + ' ' + updateReturn['data'])


    #同步人员信息
    def postUpdateEmployee(self, employees, header):
        
        url = 'http://www.91pxb.com/api/Employees/SynchronizeStudents'
        
        count = 1
        employeeList = []
        #print('+++++employees++++',employees)
            
        for i in range(0, len(employees)) :
            count += 1
            key = employees[i][0]
            name = employees[i][1]
            employeeId = employees[i][2]
            department = employees[i][3]
            position = employees[i][4]
            sex = employees[i][5]
            mobilePhone = employees[i][6]
            defaultCode = employees[i][7]
            organizationCode = employees[i][8]
            organizationCodeList = [organizationCode]
            #print(organizationCodeList)
            list = ({"code": key, "chinese_name": name, "employee_id": employeeId, "department": department, "position": position, "gender": sex, "mobile": mobilePhone, "default_code": defaultCode, "organization_codes": organizationCodeList })
            employeeList.append(list)
            #print(count)
            if count == 1000 :
                #print('同步一次',employeeList)
                updateReturn = self.synchronizeOrganizations(url, employeeList, header)
                if (updateReturn['err'] == 0):
                    print(str(updateReturn['err']) + ' ' +str(updateReturn['data']))
                else:
                    print(str(updateReturn['err']) + ' ' + updateReturn['data'])
                    #self.utils.postEmail('系统提醒', '培训宝人员信息同步失败！', 'chendong@sunon-china.com')
                count = 1
                list = ()
                employeeList = []
                print('+++++++++++++',list,'++++++++++++++',employeeList)
        print('postUpdateEmployee++++', count)
        updateReturn = self.synchronizeOrganizations(url, employeeList, header)
        if (updateReturn['err'] == 0):
            print(str(updateReturn['err']) + ' ok ' +str(updateReturn['data']))
        else:
            print(str(updateReturn['err']) + ' ' + updateReturn['data'])
            #self.utils.postEmail('系统提醒', '培训宝人员信息同步失败！', 'chendong@sunon-china.com')

    #删除pxb人员信息
    def postDeleteEmployee(self, employees, header): 
        
        url = 'http://www.91pxb.com/api/Employees/DeleteStudents'

        count = 1
        employeeList = []
            
        for i in range(0, len(employees)) :
            count += 1
            key = employees[i][0]
            #print(organizationCodeList)
            list = ({"code": key })
            employeeList.append(list)
            if count == 1000 :
                print(employeeList)
                updateReturn = self.synchronizeOrganizations(url, employeeList, header)
                if (updateReturn['err'] == 0):
                    print(str(updateReturn['err']) + ' ' +str(updateReturn['data']))
                else:
                    print(str(updateReturn['err']) + ' ' + updateReturn['data'])
                count = 1
                list = ()
                employeeList = []
        print('postDeleteEmployee+++++', employeeList)
        updateReturn = self.synchronizeOrganizations(url, employeeList, header)
        if (updateReturn['err'] == 0):
            print(str(updateReturn['err']) + ' ' +str(updateReturn['data']))
        else:
            print(str(updateReturn['err']) + ' ' + updateReturn['data'])
            self.utils.postEmail('系统提醒', '培训宝人员信息删除失败！', 'chendong@sunon-china.com')
        

    #Get 91PXB access token    
    def getAccessToken(self, url, post, header):
        return self.utils.apiCall(url, post, header)

    #Post company to 91PXB
    def synchronizeRootCompany(self, url, post, header):
        return self.utils.apiCall(url, post, header)

    #Get company from MDM db
    def getRootCompany(self):
        companies = self.company.objects.filter(status = 2, effective_flag = 0, parent_company_key = '').values('code', 'name')
        print(companies.query)
        return companies


    def getDepartments(self):
        departments = self.department.objects.filter(status = 2, effective_flag = 0).values('code', 'name', 'parent_dept_key__code')
        print(departments.query)
        return departments

    def synchronizeOrganizations(self, url, post, header):
        return self.utils.apiCall(url, post, header)

    def getEmployees(self):
        from django.db import connection
        cursor = connection.cursor()
<<<<<<< HEAD
        sql = "select mdm_employee.key, mdm_employee.name, mdm_employee.code, mdm_department.name, mdm_position.name, mdm_employee.sex, mdm_employee.mobile, mdm_department.code as default_code, mdm_department.code organization_codes from mdm_job_data a left join mdm_employee on a.empl_key = mdm_employee.key left join mdm_department on a.dept_key = mdm_department.key left join mdm_position on a.pos_key = mdm_position.key where a.effective_flag = 0 and mdm_employee.effective_flag = 0  and mdm_department.effective_flag = 0 and mdm_position.effective_flag = 0  and a.start_date = (select max(start_date) from mdm_job_data b where b.empl_key=a.empl_key) order by mdm_employee.id asc"
=======
        sql = "select mdm_employee.key, mdm_employee.name, mdm_employee.code, mdm_department.name, mdm_position.name, mdm_employee.sex, mdm_employee.mobile, mdm_department.code as default_code, mdm_department.code organization_codes from mdm_job_data a left join mdm_employee on a.empl_key = mdm_employee.key left join mdm_department on a.dept_key = mdm_department.key left join mdm_position on a.pos_key = mdm_position.key where a.effective_flag = 0 and mdm_employee.effective_flag = 0  and mdm_department.effective_flag = 0 and mdm_position.effective_flag = 0  and a.start_date = (select max(start_date) from mdm_job_data b where b.empl_key=a.empl_key) and  empl_status_key='1001A910000000000C1H'  order by mdm_employee.code asc"
>>>>>>> a5296a69b2bdebce27493a213ff17f720096c026
        cursor.execute(sql)
        row = cursor.fetchall()
        #print(row)
        return row 

    def synchronizeStudents(self, url, post, header):
        return self.utils.apiCall(url, post, header)
'''
    def biPortalConn(self):
        from django.db import connection
        cursor = connection.cursor()
        sql = "select mdm_employee.key, mdm_employee.name, mdm_employee.code, mdm_department.name, mdm_position.name, mdm_employee.sex, mdm_employee.mobile, mdm_department.code as default_code, mdm_department.code organization_codes from mdm_job_data a left join mdm_employee on a.empl_key = mdm_employee.key left join mdm_department on a.dept_key = mdm_department.key left join mdm_position on a.pos_key = mdm_position.key where a.effective_flag = 0 and mdm_employee.effective_flag = 0  and mdm_department.effective_flag = 0 and mdm_position.effective_flag = 0  and a.start_date = (select max(start_date) from mdm_job_data b where b.empl_key=a.empl_key) order by mdm_employee.id asc"
        cursor.execute(sql)
        row = cursor.fetchall()
        #print(row)
        return row 
'''

import os   
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8' 
class Maycur():

    def __init__(self):
        self.utils = Utils()
<<<<<<< HEAD
        #CBS测试地址
        #self.cxoracle = CxOracle('cbs', 'sunon$2018', '172.16.59.182', 1521, 'sunon')
        #CBS正式地址
        self.cxoracle = CxOracle('cbs', 'sunon$2018', '172.16.59.139', 1521, 'cbsdb')

=======
        self.cxoracle = CxOracle('cbs', 'sunon$2018', '172.16.59.182', 1521, 'orcl')
        
>>>>>>> a5296a69b2bdebce27493a213ff17f720096c026
    def main(self):
        import time
        timeStamp = str(int(time.time()*1000))
        header = self.getHeader(timeStamp)
        accountCorpDict = self.getCompanyPayAccount(header) #公司支付账号字典
        self.getAllPayment(timeStamp, header, accountCorpDict)
        #self.getPaymentfailed(timeStamp,header)
        self.postPaymentstatus(header)              #回写支付状态给每刻

    #回写每刻支付成功或支付失败状态
    def postPaymentstatus(self, header):
        import time
 
        postMaycurUrl = 'https://www.maycur.com/api/openapi/paymenttransaction/update'
   
        cbsData = self.getLabeled()
<<<<<<< HEAD
        print('回写每刻支付成功或支付失败状态cbsData++++++++++++++++++++++++++++++++++++++++++++++++',cbsData)
=======
        print('postPaymentstatus', cbsData)
>>>>>>> a5296a69b2bdebce27493a213ff17f720096c026

        if cbsData == [] :
            print("postPaymentstatus:暂无数据需要回写每刻")
        else:
            print('回写每刻支付状态——++++++++++++++++++++++++')
            for i in range(0, len(cbsData)):
                dataList = []
                paymentAccounts = cbsData[i][2]
                Status = cbsData[i][1]
                #if recordStatus == 'Success' and paymentAccounts == None:
                #    continue
                PayDate = cbsData[i][3]
                errorMsg = cbsData[i][4]
<<<<<<< HEAD
                #print('错误提醒+++++++++++',errorMsg)
                #if errorMsg != None:
                #    errorMsg = self.utils.json(errorMsg, 'decode')
=======
                #if errorMsg != None:
                #    errorMsg = self.utils.json(errorMsg, 'decode') 
>>>>>>> a5296a69b2bdebce27493a213ff17f720096c026
                sequence = cbsData[i][5]
                erpPaymentId = cbsData[i][0]
                depositBankType = cbsData[i][6]
                #if depositBankType == 'ABC':
                #paymentAccounts = '19'+paymentAccounts
                #print(paymentAccounts)
                if Status != 'Success':
                    recordStatus = 'PAY_FAIL'
                    
                else:
                    recordStatus = 'PAY_SUCCESS'
                    errorMsg = ''
                print('recordStatus++++++++',recordStatus)
                timeArray = time.strptime(PayDate, "%Y-%m-%d %H:%M:%S")
                #支付时间的时间戳:
                timeStamp = int(time.mktime(timeArray)*1000)
                list = ({"sequence": sequence, "paidDate": timeStamp, "payerBankAccount": paymentAccounts, "status": recordStatus, "errorMsg": errorMsg})
                #更新CBS中间表erp_comment1字段为"2"

                dataList.append(list)
                #当前时间的时间戳CBS_EXPORT_FAILED
                nowtimeStamp = int(time.time()*1000)
                data = {"timeStamp": nowtimeStamp, "data": dataList}
                print('data++++++++++++++++++++++++++++++++++++++++++++++++++',data)
                result = self.postPayment(postMaycurUrl, data, header)
<<<<<<< HEAD
                #print('result++++++++++++',result)
                #print('result+++++++++++++++++++++++++++++++++++++++++++++++++++++',result)
=======
                print('result', result)
>>>>>>> a5296a69b2bdebce27493a213ff17f720096c026
                if result['code'] == 'NACK':
                    print(result['data'])
                    continue
                self.updatePaymentFlag(erpPaymentId, '2')
                print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$回写每刻支付状态成功！')

    #post已导出状态给每刻
    def postExportstatus(self, timeStamp, header):

        postMaycurUrl = 'https://www.maycur.com/api/openapi/paymenttransaction/update'
        #获取每刻回写到CBS的流水数据
        cbsData = self.getUnlabel()
        print('postExportstatus-cbsdata',cbsData)
        dataList = []
        if cbsData == []:
            print("postExportstatus:CBS无新增数据")
        else:
            for i in range(0, len(cbsData)):
                sequence = cbsData[i][5]          #流水号
                erp_payment_id = cbsData[i][0]    #唯一编号
                list = ({"sequence": sequence, "status": 'CBS_EXPORTED'})
                dataList.append(list)
                self.updatePaymentFlag(erp_payment_id, '1')
            data = {"timestamp": timeStamp, "data": dataList}
            print('postExportstatus-data', data)
            result = self.postPayment(postMaycurUrl, data, header)
            print('postExportstatus-result', result)


    #获取带code、tokenid的header
    def getHeader(self, timeStamp):
        accessTokenUrl = 'https://www.maycur.com/api/openapi/auth/login'
        #PaymentUrl = 'https://www.maycur.com/api/openapi/paymenttransaction/list'
        appCode = 'UI180510Z0KSLOYSA'
        secret = '7TLzEHwtQWnKJvF8R9QCNFaZ4MeMaXkTgoAK4XygFkLZuuouuq9DCKPt4ywbUDxw'
        #加密
        res = self.getSh256(secret + ':' + appCode + ':' + timeStamp)
        auth = {'appCode': appCode,'timestamp': timeStamp, 'secret': res}
        header = {'content-type':'application/json'}
        accessToken = self.getAccessToken(accessTokenUrl, auth, header)
<<<<<<< HEAD
        print(accessToken)
=======
        #print(accessToken)
>>>>>>> a5296a69b2bdebce27493a213ff17f720096c026
        if (accessToken['code'] == 'ACK'):
            data = accessToken.get('data')
            header['entCode'] = data.get('entCode')
            header['tokenId'] = data.get('tokenId')
        else:
            print("获取Token失败！！")
        return header

    #获取每刻已导出的支付流水到CBS中间表
    def getAllPayment(self, timeStamp, header, accountCorpDict):
        PaymentUrl = 'https://www.maycur.com/api/openapi/paymenttransaction/list'
        data = {"timestamp": timeStamp, "data": {"sequence": -1}}
        result = self.getPayment(PaymentUrl, data, header)
        print('result+++++++++++++++++++++++++++',result)
        if (result['code'] == 'ACK'):

            paymentData = result.get('data')
<<<<<<< HEAD
            #print('paymentData++++++++++++++++++++++++++++++++++++++++',paymentData)
=======
            print('getAllPayment-paymentData', paymentData)
>>>>>>> a5296a69b2bdebce27493a213ff17f720096c026
            paymentList = []
            for i in range(0, len(paymentData)):
                dict = paymentData[i]
                sequence = dict['sequence']                                                          #流水号
                subSidiaryBizCode = dict['subsidiaryBizCode']                                        #公司编码
                newPayment = self.checkNewPayment(sequence)                                          #是否新标识
                failedPaymentExist = self.checkFailedPaymentExist(sequence)                          #是否支付失败标识
                if not newPayment and not failedPaymentExist:
                    continue
                erpPaymentId = str(sequence)+timeStamp                                               #CBS唯一编码
                #print(erp_payment_id)
                payeeBankCode = dict['payeeBankCode'].upper()                                        #收款方银行类型
                payeeBankCode = payeeBankCode[0:3]                                                   #保留前3位
                payeeBankCardNO = dict['payeeBankCardNO']                                            #收款方银行账号
                #payeeBankCardNO = payeeBankCardNO.upper()
                #print(payeeBankCode)
                paidAmount = dict['paidAmount']                                                      #金额
                Amount = [str(paidAmount),int(paidAmount)][int(paidAmount)==paidAmount]
                payerBankAccount = accountCorpDict[subSidiaryBizCode]                                          #公司支付账号
                #payerBankAccount = '19082301040025838'
                #payerBankAccount = '082301040004015'
                payeeBankBranchNO = dict['payeeBankBranchNO']                                        #收款人银行联行号
                payeeName = dict['payeeName']                                                        #收款人
                acceptCcy = dict['acceptCcy']                                                        #收款币种
                acceptCcy = self.currency(acceptCcy)
                payeeTargetBizCode = dict['payeeTargetBizCode']                                      #每刻报销--单据编号
                payeeBankBranchName = dict['payeeBankBranchName']                                    #开户行地址
                paymentStatus = dict['paymentStatus']                                                #状态
                payeeBankProvince = dict['payeeBankProvince']    #省
                payeeBankLocation = dict['payeeBankLocation']    #市
                #PaymentAccounts = '1111111111'    #付款方银行账号
                #print(paymentStatus)str.upper()
                if paymentStatus == 18 or paymentStatus == 66 :
                    flag = 1
                else:
                    flag = 0
                payeeTarget = dict['payeeTarget']                                                    #被支付方类型
                #获取单据事由
                reason = self.getReason(payeeTargetBizCode,header,payeeTarget)
                #获取公司编码
<<<<<<< HEAD

                paymentCltnbr = self.companyId(subSidiaryBizCode)
                if payeeBankCode == None or payeeBankCardNO == None or Amount == 0:
                    continue
                checkCode = self.getCheckCode(erpPaymentId, 'Available', payeeBankCardNO, Amount, payerBankAccount)
                list = (erpPaymentId, 'Available', '202', '2', payeeBankCardNO, payeeBankCode, paidAmount, reason, 0, checkCode, payerBankAccount, payeeName, '', acceptCcy, payeeBankBranchNO, flag, sequence, payeeTargetBizCode, payeeBankBranchName,payeeBankProvince,payeeBankLocation,'1','N','3')
                paymentList.append(list)
            print(paymentList)
            insertSql = "insert into authorization_to_payment(erp_payment_id, record_status,payment_type_id,payment_method_type_id,deposit_accounts,deposit_bank_type,amount,purpose,version,check_code,payment_accounts,deposit_accounts_name,payment_cltnbr,currency_type,union_bank_number,erp_comment1,erp_comment2,erp_comment3,deposit_bank_name,deposit_province,deposit_city,city_flag,priority_flag,operation_type)VALUES(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17,:18,:19,:20,:21,:22,:23,:24)"
=======
                subSidiaryBizCode = dict['subsidiaryBizCode']
                paymentCltnbr = self.companyId(subSidiaryBizCode)
                
                if payeeBankCode == None or payeeBankCardNO == None or Amount == 0:
                    continue
                checkCode = self.getCheckCode(erpPaymentId, 'Available', payeeBankCardNO, Amount, payerBankAccount)
                list = (erpPaymentId, 'Available', '401', '2', payeeBankCardNO, payeeBankCode, paidAmount, reason, 0, checkCode, payerBankAccount, payeeName, paymentCltnbr, acceptCcy, payeeBankBranchNO, flag, sequence, payeeTargetBizCode, payeeBankBranchName)
                paymentList.append(list)
            print('paymentList', paymentList)
            insertSql = "insert into authorization_to_payment(erp_payment_id, record_status,payment_type_id,payment_method_type_id,deposit_accounts,deposit_bank_type,amount,purpose,version,check_code,payment_accounts,deposit_accounts_name,payment_cltnbr,currency_type,union_bank_number,erp_comment1,erp_comment2,erp_comment3,deposit_bank_name)VALUES(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17,:18,:19)"
>>>>>>> a5296a69b2bdebce27493a213ff17f720096c026
            self.cxoracle.insert(insertSql, paymentList)
            print("######################################################")
            #回写已导出状态给每刻
            self.postExportstatus(timeStamp, header)  
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        else:
            print("请求失败")
            self.utils.postEmail('系统提醒', '获取每刻已导出的支付流水失败！', 'chendong@sunon-china.com')
            print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

    def getAccessToken(self, url, post, header):
        return self.utils.apiCall(url, post, header)

    def getPayment(self, url, data, header):
        return self.utils.apiCall(url, data, header)

    def postPayment(self, url, data, header):
        return self.utils.apiCall(url, data, header)


    #计算校验码
    def getCheckCode(self, sequence, recordStatus, depositAccounts, amount, payerBankAccount):
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
    def getSh256(self, res):
        return self.utils.Sha256(res)
    

    #获取CBS状态为0的支付流水
    def getUnlabel(self):
        sql = "select  erp_payment_id,record_status,payment_accounts,cbs_last_update_time,cbs_comment,erp_comment2 from  authorization_to_payment where erp_comment1='0'  "
        result = self.cxoracle.query(sql)
        return result

    #获取CBS状态为1的支付流水
    def getLabeled(self):
        sql = "select  erp_payment_id,record_status,payment_accounts,cbs_last_update_time,cbs_comment,erp_comment2,deposit_bank_type, erp_comment3 from authorization_to_payment a where cbs_last_update_time=(select max(cbs_last_update_time) from authorization_to_payment b where b.erp_comment3=a.erp_comment3  ) and record_status  in ('Failed','Success') and erp_comment1='1' "
        result = self.cxoracle.query(sql)
        return result

    #获取SEQ流水号在CBS中的记录数，用来判断是否需要再插入中间表
    def checkFailedPaymentExist(self, sequence):
        sequence = str(sequence)
        sql = "select   count(*) cnt  from (select t.*,row_number() over(partition by t.erp_comment2 order by t.cbs_last_update_time desc) rn from authorization_to_payment t) c where rn = 1 and record_status ='Failed' and erp_comment2='"+sequence+"'"
        result = self.cxoracle.query(sql)
        if (result[0][0] == 0):
            return False
        else:
            return True

    def checkNewPayment(self, sequence):
        sequence = str(sequence)
        sql = "select   count(*) cnt  from (select t.*,row_number() over(partition by t.erp_comment2 order by t.cbs_last_update_time desc) rn from authorization_to_payment t) c where erp_comment2='"+sequence+"'"
        result = self.cxoracle.query(sql)
        if (result[0][0] == 0):
            return True 
        else:
            return False 

    #每刻币种转换
    def currency(self, acceptCcy):
        return {
            'CNY': '10',
            #'b': 2,
            #'c': 3,
        }.get(acceptCcy, 'error') 

    #CBS公司编码转换
    def companyId(self,subSidiaryBizCode):
        return {
            'SA':'0000',
            'XS':'0001',
            'PC':'0012',
            'HN':'0003',
            'SK':'0004',
            'ZY':'0010',
            'AC':'0011',
            'OY':'0005',
        }.get(subSidiaryBizCode,'error')

    #更新CBS中间表erp_comment1标识     '1'表示已导出或导出失败  标识'2'表示支付成功或失败
    def updatePaymentFlag(self, erpPaymentId, type):
        if type == '1':  
            sql = "update authorization_to_payment set erp_comment1 = '1' where erp_payment_id = '"+erpPaymentId+"'"
        else:
            sql = "update authorization_to_payment set erp_comment1 = '2' where erp_payment_id = '"+erpPaymentId+"'"
        self.cxoracle.exec(sql)

    #获取对私报销事由   
    def getReason(self, businessCode, header, payeeTarget):
        import urllib.request
        import urllib.parse

        #获取对私报销事由的url
        if payeeTarget == 'PERSONAL' :
            url = 'https://www.maycur.com/api/openapi/report/personal/detail?businessCode='+businessCode
        #获取对公报销事由的url
        if payeeTarget == 'CORP' :
            url = 'https://www.maycur.com/api/openapi/report/corp/detail?businessCode='+businessCode
        #获取消费申请事由的url
        if payeeTarget == 'EXPENSE' :
            url = 'https://www.maycur.com/api/openapi/report/consume/detail?businessCode='+businessCode

        entCode = header['entCode'] 
        tokenId = header['tokenId'] 
        request = urllib.request.Request(url)
        request.add_header('entCode', entCode)
        request.add_header('tokenId', tokenId)
        result = urllib.request.urlopen(request).read()
        result = self.utils.json(result, 'decode')
        print('getReason', result)
        data = result['data'][0]
        reason = data['name']
        return reason

    #获取每刻支付账号列表
    def getCompanyPayAccount(self, header):
        getMaycurUrl = 'https://www.maycur.com/api/openapi/account/corp/list'
        result = self.postPayment(getMaycurUrl, '', header)
        if (result['code'] == 'ACK'):
            accountCorpDict = {}  #创建一个空的DICT
            data = result['data']
            for i in range(0, len(data)):
                accountCorpList = data[i]
                subsidiaryBizCode = accountCorpList['subsidiaryBizCode']
                account = accountCorpList['account']
                accountCorpDict[subsidiaryBizCode] = account    #公司账号填入DICT
                #accountCorpDict1.append(accountCorpDict) 
        return accountCorpDict


'''
    #获取支付失败的流水更新CBS中间表
    def getPaymentfailed(self,timeStamp,header):
        PaymentUrl = 'https://www.maycur.com/api/openapi/paymenttransaction/list'
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


class Utils():
    
    #Using python urllib to get or post 
    def apiCall(self, url, post, header):
        import urllib.request
        import urllib.parse
        post = self.json(post, 'encode')
        post = bytes(post, 'utf8')
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
    def Sha256(self, res):
        import hashlib
        sha256 = hashlib.sha256()
        sha256.update(res.encode('utf-8'))
        result = sha256.hexdigest()
        return result

    #发送邮件
    def postEmail(self, title, content, addressee):
        from django.core.mail import send_mail
        from django.conf import settings
<<<<<<< HEAD
        res = send_mail(title, content, 'noreply.bi@sunon-china.com ', [addressee], fail_silently=False)
=======
        res = send_mail(title, content, 'noreply.bi@sunon-china.com', [addressee], fail_silently=False)
>>>>>>> a5296a69b2bdebce27493a213ff17f720096c026
        return res

import cx_Oracle

class CxOracle():


    def __init__(self, user, pwd, host, port, service_name ):
        self._user = user
        self._pwd = pwd
        self._tns = cx_Oracle.makedsn(host, port, service_name)
        self._conn = None
        self._reConnect()
    def _reConnect(self):
        if not self._conn :
            self._conn = cx_Oracle.connect (self._user, self._pwd, self._tns)
        else:
            pass
    def __del__(self):
        if self. _conn:
            self._conn. close()
            self._conn = None
    def _newCursor(self):
        cur = self._conn.cursor()
        if cur:
            return cur
        else:
            print ("#Error# Get New Cursor Failed.")
        return None
    def _delCursor(self, cur):
        if cur:
            cur.close()
    def query(self, sql):
        rt = []
        cur = self._newCursor()
        if not cur:
            return rt
        cur.execute(sql)
        #print(cur)
        rt = cur.fetchall()
        #print(rt)
        self._delCursor(cur)
        return rt
  # 更新
    def exec(self, sql):
        rt = None
        cur = self._newCursor()
        if not cur:
            return rt
        rt = cur.execute(sql)
        self._conn.commit()
        self._delCursor(cur)
        return rt 
    #批量插入
    def insert(self, sql, param):
        #print(param)
        rt = None
        cur = self._newCursor()
        if not cur:
            return rt
        rt = cur.executemany(sql, param)
        self._conn.commit()
        self._delCursor(cur)
        return rt 


def pxb():
    pxb = Pxb()
    pxb.main()

def maycur():
    maycur = Maycur()
    maycur.main()
<<<<<<< HEAD

maycur()
=======
>>>>>>> a5296a69b2bdebce27493a213ff17f720096c026

maycur()
'''
