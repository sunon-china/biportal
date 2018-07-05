

'''
@Author Feng ZHAO
@Date 2018/07/02
@Purpose Cron jobs 

ChangeLog
2018/07/02 Feng ZHAO Initial Draft
2018/07/02 Feng ZHAO Class PXB & Utils  debug comand = /usr/local/python/bin/python3 /www/python/biportal/manage.py crontab run 9da3a107c107d7271341ba543a223a78
2018/07/04 Feng ZHAO Using Django model to get queryset 
'''

class Pxb():

    #Construction function
    def __init__(self):
        from mdm.models import Company 

        self.company = Company
        self.utils = Utils()


    #Main function for post company, org, employee to 91PXB
    def main(self):

        accessTokenUrl = 'http://www.91pxb.com/api/AccessToken/Get'
        rootCompanyUrl = 'http://www.91pxb.com/api/Companies/SynchronizeRootCompany' 
        auth = {'appId': 'hHvKkSxRt113b690', 'appSecret': '98F2709A98B91FD3BEEFB32697DD144971246D0A'}
        header = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}


        accessToken = self.getAccessToken(accessTokenUrl, auth, header)
        if (accessToken['err'] == 0):
            header['ACCESS-TOKEN'] = accessToken['data']
            rootCompany = self.getRootCompany()

            for c in rootCompany:
                company = []
                company.append({
                    'code': c['code'],
                    'organization_name': c['name'],
                })
                print(company)
                #updateReturn = self.updateRootCompany(rootCompanyUrl, company, header)

        else:
            print(accessToken['err'] + accessToken['data'])
        

    #Get 91PXB access token    
    def getAccessToken(self, url, post, header):
        return self.utils.apiCall(url, post, header)

    #Post company to 91PXB
    def updateRootCompany(self, url, post, header):
        return self.utils.apiCall(url, post, header)

    #Get company from MDM db
    def getRootCompany(self):
        companies = self.company.objects.filter(status=2).values('code', 'name')

        return companies


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

