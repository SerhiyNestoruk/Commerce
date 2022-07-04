
from django.forms import ModelForm, ModelMultipleChoiceField, TextInput
from .models import Auction,Bid, Comment
from django.db import models

class AuctionForm(ModelForm):
    class Meta:
        model = Auction
        fields = ['item_name', 'item_description', 'start_bid', 'picture_url', 'category']
     
    
class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
   