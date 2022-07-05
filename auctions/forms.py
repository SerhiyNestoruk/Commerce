
from django import forms
from django.forms import Form
from django.forms import ModelForm, ModelMultipleChoiceField, TextInput
from .models import Auction,Bid, Comment
from django.db import models

class AuctionForm(ModelForm):
    start_bid = forms.DecimalField(min_value=0, max_digits=15, decimal_places=2)
    class Meta:
        model = Auction
        fields = ['item_name', 'item_description', 'picture_url', 'category']
        
    
class BidForm(Form):
    amount = forms.DecimalField(min_value=0, max_digits=15, decimal_places=2)

        