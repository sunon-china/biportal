from django.db import models
import django.utils 

# Create your models here.
class Company(models.Model):
    key = models.CharField(max_length=20, unique = True, default='')
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=200, blank=True, null=True)
    parent_company_key = models.CharField(max_length=20, blank=True, null=True)
    head_of_company_key = models.CharField(max_length=20, blank=True, null=True)
    status = models.IntegerField(default=1)
    effective_flag = models.IntegerField(default=0)
    created_job = models.CharField(max_length=100, blank=True, null=True)
    created_tr = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateField(default=django.utils.timezone.now)
    parent_company_key = models.ForeignKey('self', on_delete=models.CASCADE, default = '', db_column = 'parent_company_key', blank=True, null = True, to_field = 'key')
    def __str__(self):
        return self.name 
    class Meta:
        ordering = ('name',)

class Department(models.Model):
    key = models.CharField(max_length=20, unique = True)
    company_key = models.CharField(max_length=20, default = '')
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=200, blank=True, null=True)
    parent_dept_key = models.CharField(max_length=20, blank=True, null=True)
    dept_level_key = models.CharField(max_length=20)
    head_of_dept_key = models.CharField(max_length=20)
    base_key = models.CharField(max_length=20, blank=True, null=True)
    cost_center = models.CharField(max_length=20, blank=True, null=True)
    status = models.IntegerField(default=1)
    effective_flag = models.IntegerField(default=0)
    created_job = models.CharField(max_length=100, blank=True, null=True)
    created_tr = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateField()
    erp_code = models.CharField(max_length=20)
    parent_dept_key = models.ForeignKey('self', on_delete=models.CASCADE, default = '', db_column = 'parent_dept_key', blank=True, null = True, to_field = 'key')
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ('name',)
        
class Position(models.Model):
    key = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=200)
    dept_key = models.CharField(max_length=200)
    job_key = models.CharField(max_length=20)
    pos_series_key = models.CharField(max_length=20)
    job_grade_key = models.CharField(max_length=20)
    job_rank_key = models.CharField(max_length=20, blank=True, null=True)
    parent_pos_key = models.CharField(max_length=20)
    key_pos_flag = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    effective_flag = models.IntegerField(default=0)
    created_job = models.CharField(max_length=100, blank=True, null=True)
    created_tr = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateField()
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ('name',)
    
class Employee(models.Model):
    key = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    sex = models.IntegerField(default=1)
    nationality_key = models.CharField(max_length=20)
    birthday = models.DateField()
    work_start_date = models.DateField()
    id_number = models.CharField(max_length=25)
    id_card_expiry_date = models.DateField()
    political_status_key = models.CharField(max_length=20, blank=True, null=True)
    marital_staus_key = models.CharField(max_length=20, blank=True, null=True)
    native_place_key = models.CharField(max_length=20, blank=True, null=True)
    household_type_key = models.CharField(max_length=20, blank=True, null=True)
    permanent_residence = models.CharField(max_length=250, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    private_emial = models.EmailField(max_length=50, blank=True, null=True)
    company_email = models.EmailField(max_length=50, blank=True, null=True)
    telephone =  models.CharField(max_length=30, blank=True, null=True)
    mobile=  models.CharField(max_length=30)
    emergency_contact = models.CharField(max_length=200, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    recruitment_type_key = models.CharField(max_length=20)
    labour_union_flag = models.IntegerField(default=0)
    mutual_fund_flag = models.IntegerField(default=0)
    biz_card_dept_cn = models.CharField(max_length=200, blank=True, null=True)
    biz_card_dept_en = models.CharField(max_length=200, blank=True, null=True)
    biz_card_pos_cn = models.CharField(max_length=200, blank=True, null=True)
    biz_card_pos_en = models.CharField(max_length=200, blank=True, null=True)
    status = models.IntegerField(default=1)    
    effective_flag = models.IntegerField(default=0)
    created_job = models.CharField(max_length=100, blank=True, null=True)
    created_tr = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateField()
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ('name',)
        
class Org_Relation(models.Model):
    key = models.CharField(max_length=20)
    empl_id = models.CharField(max_length=20)
    previous_serving_age = models.IntegerField(default=0)
    serving_age = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    join_company_date = models.DateField()
    last_work_day = models.DateField()
    last_flag = models.CharField(max_length=1)
    effective_flag = models.IntegerField(default=0)
    created_job = models.CharField(max_length=100, blank=True, null=True)
    created_tr = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateField()
    erp_code = models.CharField(max_length=20)
    def __str__(self):
        return self.empl_id
    
    class Meta:
        ordering = ('empl_id',)
        
class Job_Data(models.Model):
    key = models.CharField(max_length=20)
    dept_key = models.CharField(max_length=20)
    company_key = models.CharField(max_length=20)
    empl_key = models.CharField(max_length=20)
    org_relation_key = models.CharField(max_length=20)
    dept_l2 = models.CharField(max_length=200,blank=True, null=True)
    dept_l3 = models.CharField(max_length=200,blank=True, null=True)
    dept_l4 = models.CharField(max_length=200,blank=True, null=True)
    dept_l5 = models.CharField(max_length=200,blank=True, null=True)
    dept_l6 = models.CharField(max_length=200,blank=True, null=True)
    pos_series_key = models.CharField(max_length=20,blank=True, null=True)
    pos_key = models.CharField(max_length=20)
    job_key = models.CharField(max_length=20,blank=True, null=True)
    job_grade_key = models.CharField(max_length=20,blank=True, null=True)
    job_rank_key = models.CharField(max_length=20,blank=True, null=True)
    empl_class_key = models.CharField(max_length=20)
    empl_type_key = models.CharField(max_length=20,blank=True, null=True)
    empl_status_key = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    supervisor_key = models.CharField(max_length=20,blank=True, null=True)
    team_leader_key = models.CharField(max_length=20,blank=True, null=True)    
    work_city_key = models.CharField(max_length=20,blank=True, null=True)
    action = models.IntegerField()
    transfer_type_key = models.CharField(max_length=20,blank=True, null=True)
    resign_apply_date = models.DateField()
    action_reason_key = models.CharField(max_length=20,blank=True, null=True)
    seq = models.IntegerField()  
    last_flag = models.CharField(max_length=1)
    effective_flag = models.IntegerField(default=0)
    created_job = models.CharField(max_length=100, blank=True, null=True)
    created_tr = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateField()
    is_main_job = models.CharField(max_length=20, default='Y')
    workplace_1 = models.CharField(max_length=200,blank=True, null=True)
    workplace_2 = models.CharField(max_length=200,blank=True, null=True)
    workplace_3 = models.CharField(max_length=200,blank=True, null=True)
    workplace_4 = models.CharField(max_length=200,blank=True, null=True)
    workplace_5 = models.CharField(max_length=200,blank=True, null=True)

    empl_key = models.ForeignKey('Employee', on_delete=models.CASCADE, default = '', db_column = 'empl_key', to_field = 'key', related_name = 'empl')
    dept_key = models.ForeignKey('Department', on_delete=models.CASCADE, default = '', db_column = 'dept_key', to_field = 'key', related_name = 'dept')
    pos_key = models.ForeignKey('Position', on_delete=models.CASCADE, default = '', db_column = 'pos_key', to_field = 'key', related_name = 'pos')
    def __str__(self):
        return self.company_key
    
    class Meta:
        ordering = ('company_key',)
        
class Probation_Data(models.Model):
    key = models.CharField(max_length=20)
    empl_key = models.CharField(max_length=20)
    job_data_key = models.CharField(max_length=20)
    start_date = models.DateField()
    expected_end_probation_date = models.DateField()
    actual_end_probation_date = models.DateField()
    probation_reason = models.CharField(max_length=1024,blank=True, null=True)
    probation_result = models.IntegerField() 
    effective_flag = models.IntegerField(default=0)
    created_job = models.CharField(max_length=100, blank=True, null=True)
    created_tr = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateField()
    #def __str__(self):
     #   return self.empl_key
    
    class Meta:
        ordering = ('empl_key',)
        
class Dept_Supervisor(models.Model):
    key = models.CharField(max_length=20)
    dept_key = models.CharField(max_length=20)
    supervisor_key = models.CharField(max_length=20,blank=True, null=True)
    effective_flag = models.IntegerField(default=0)
    created_job = models.CharField(max_length=100, blank=True, null=True)
    created_tr = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateField()
    def __str__(self):
        return self.supervisor_key
    
    class Meta:
        ordering = ('supervisor_key',)
        
class Conf(models.Model):
    key = models.CharField(max_length=20)
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=200,blank=True, null=True)
    scope = models.CharField(max_length=20,blank=True, null=True)
    effective_flag = models.IntegerField(default=0)
    created_job = models.CharField(max_length=100, blank=True, null=True)
    created_tr = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateField()
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ('name',)

class Legal_Entity(models.Model):
    key = models.CharField(max_length=20, unique = True, default='')
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=200, blank=True, null=True)
    parent_company_key = models.CharField(max_length=20, blank=True, null=True)
    status = models.IntegerField(default=1)
    effective_flag = models.IntegerField(default=0)
    created_job = models.CharField(max_length=100, blank=True, null=True)
    created_tr = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateField(default=django.utils.timezone.now)
    parent_company_key = models.ForeignKey('self', on_delete=models.CASCADE, default = '', db_column = 'parent_company_key', blank=True, null = True, to_field = 'key')
    def __str__(self):
        return self.name 
    class Meta:
        ordering = ('name',)


class Contract(models.Model):
    key = models.CharField(max_length=20)
    empl_key = models.CharField(max_length=20)
    org_relation_key = models.CharField(max_length=20)
    job_data_key = models.CharField(max_length=20)
    company_key = models.CharField(max_length=20)
    contract_sign_company = models.CharField(max_length=100)
    contract_main_company = models.CharField(max_length=100)
    business_type = models.CharField(max_length=20)
    contract_start_date = models.DateField()
    contract_end_date = models.DateField()
    seq = models.IntegerField(null=True)  
    last_flag = models.CharField(max_length=1,null=True)
    isrefer = models.CharField(max_length=1,null=True)
    effective_flag = models.IntegerField(default=0)
    created_job = models.CharField(max_length=100, blank=True, null=True)
    created_tr = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateField()
    #def __str__(self):
     #   return self.empl_key
    
    class Meta:
        ordering = ('key',)


        

    


