from django.db import models

# Create your models here.
class CLIENT(models.Model):
    No       = models.CharField(max_length=10, unique=True)
    type     = models.SmallIntegerField()  #0 = 公司客户， 1 = 个人客户
    co_name  = models.CharField(max_length=100, null=True)
    co_addr  = models.CharField(max_length=100, null=True)
    co_tel   = models.CharField(max_length=20,  null=True)
    tax_id   = models.CharField(max_length=100, null=True)
    account_owner  = models.CharField(max_length=50,  null=True)
    account_number = models.CharField(max_length=20,  null=True)
    account_bank   = models.CharField(max_length=100, null=True)
    contact_name   = models.CharField(max_length=100, null=True)
    contact_tel    = models.CharField(max_length=20,  null=True)
    contact_role   = models.CharField(max_length=100, null=True)
    contract_start = models.CharField(max_length=20,  null=True)
    contract_end   = models.CharField(max_length=20,  null=True)
    contract_file  = models.CharField(max_length=100, null=True)
    class Meta:
        permissions=(
            ("view_client",            "Can access information of client"),
            #("add_client",             "Can insert new client"),
            #("change_client",          "Can change normal info of client"),
            ("change_client_contract", "Can edit contract of client"),
            ("change_client_tax",      "Can edit tax_id of client"),
            #("delete_client",          "Can delete a client"),
        )

class SUPPLIER(models.Model):
    No       = models.CharField(max_length=10, unique=True)
    type     = models.SmallIntegerField()  #0 = 公司供应商， 1 = 个人供应商
    co_name  = models.CharField(max_length=100, null=True)
    co_addr  = models.CharField(max_length=100, null=True)
    co_tel   = models.CharField(max_length=20,  null=True)
    tax_id   = models.CharField(max_length=100, null=True)
    account_owner  = models.CharField(max_length=50,  null=True)
    account_number = models.CharField(max_length=20,  null=True)
    account_bank   = models.CharField(max_length=100, null=True)
    contact_name   = models.CharField(max_length=100, null=True)
    contact_tel    = models.CharField(max_length=20,  null=True)
    contact_role   = models.CharField(max_length=100, null=True)
    contract_start = models.CharField(max_length=20,  null=True)
    contract_end   = models.CharField(max_length=20,  null=True)
    contract_file  = models.CharField(max_length=100, null=True)
    class Meta:
        permissions=(
            ("view_supplier",            "Can access information of supplier"),
            #("add_supplier",             "Can insert new supplier"),
            #("change_supplier",          "Can change normal info of supplier"),
            ("change_supplier_contract", "Can edit contract of supplier"),
            ("change_supplier_tax",      "Can edit tax_id of supplier"),
            #("delete_supplier",          "Can delete a supplier"),
        )

class ORDER(models.Model):
    No        = models.CharField(max_length=12, unique=True)
    status    = models.SmallIntegerField() #6个状态 用数字代替
    client_id = models.IntegerField()
    dep_place = models.CharField(max_length=200)
    dep_city  = models.CharField(max_length=50)
    des_place = models.CharField(max_length=200)
    des_city  = models.CharField(max_length=50)
    rec_name  = models.CharField(max_length=50, default="")
    rec_tel   = models.CharField(max_length=50, default="")
    cargo_name     = models.CharField(max_length=100)
    cargo_weight   = models.FloatField(max_length=100)
    cargo_quantity = models.IntegerField()
    note           = models.CharField(max_length=500, null=True)
    receiveables   = models.FloatField(null=True)
    received       = models.FloatField(null=True)
    create_time    = models.DateTimeField(auto_now_add=True)
    clear_time     = models.DateTimeField(null=True)
    if_delete      = models.SmallIntegerField()
    class Meta:
        permissions=(
            ("view_order", "Can access information of orders"),
            ("view_trash_order", "Can access information of trash box"),
        )

class SUP_STEP(models.Model): #供应商操作环节的列表
    name = models.CharField(max_length=100)

class PAYABLES(models.Model):
    status      = models.SmallIntegerField()
    order_id    = models.IntegerField()
    step        = models.IntegerField()     #环节主码
    description = models.CharField(max_length=200)
    supplier_id = models.IntegerField()
    payables    = models.FloatField(null=True)
    paid_cash   = models.FloatField(null=True)
    paid_oil    = models.FloatField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    clear_time  = models.DateTimeField(null=True)

class RECEIVEABLES(models.Model):
    status      = models.SmallIntegerField()
    order_id    = models.IntegerField()
    description = models.CharField(max_length=200)
    receiveables= models.FloatField(null=True)
    received    = models.FloatField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    clear_time  = models.DateTimeField(null=True)


class LOG_TRACE(models.Model):
    order_id = models.IntegerField()
    status = models.CharField(max_length=50)
    time   = models.DateTimeField()
    desc   = models.CharField(max_length=50, null=True)