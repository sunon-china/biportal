

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
test
test 2
test 3
test ljw
test ljw1
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

def pxb():
    pxb = Pxb()
    pxb.main()

