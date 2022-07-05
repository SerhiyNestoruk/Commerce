from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

class User(AbstractUser):
    pass



class Auction(models.Model):
    item_name = models.CharField(max_length=200, blank=False)
    item_description = models.TextField(max_length=500, blank=False)
    start_bid = models.DecimalField(max_digits=15, decimal_places=2, blank=False)
    picture_url = models.URLField(blank=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=True)
    author = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    watched_by_users = models.ManyToManyField(User, blank=True, related_name="watched_list")

    def __str__(self):
        if self.active:
            state = "Active"
        else:
            state = "Closed"
         
        return f"No {self.pk} - {self.item_name}. State: {state}"
        
class Bid(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2, blank=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.date} by {self.author}, {self.auction.item_name} for amount {self.amount}" 


class Comment(models.Model):
    text = models.TextField(max_length=500)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return f"{self.date} by {self.author}, Text: {self.text}" 