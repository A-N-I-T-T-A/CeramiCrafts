from django.db import models
from django.contrib.auth.models import User

class userdetails(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    address=models.CharField(max_length=255)
    phone=models.CharField(max_length=255)
    prf_image=models.ImageField(upload_to="user/",null=True)
class category(models.Model):
    category_name=models.CharField(max_length=255)
class product(models.Model):
    category=models.ForeignKey(category,on_delete=models.CASCADE,null=True)
    pdname=models.CharField(max_length=255)
    nos=models.IntegerField()
    pdprice=models.DecimalField(max_digits=10, decimal_places=2)
    pd_desc=models.CharField(max_length=255)
    pdimage=models.ImageField(upload_to="product/",null=True)
class cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    product=models.ForeignKey(product,on_delete=models.CASCADE,null=True)
    quantity=models.IntegerField(default=1)
    total_price=models.DecimalField(max_digits=10, decimal_places=2)
class order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(product, on_delete=models.CASCADE)
    quantity=models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    

