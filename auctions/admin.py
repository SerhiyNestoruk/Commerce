from django.contrib import admin
from .models import Auction, User, Bid, Category, Comment

class AuctionAdmin(admin.ModelAdmin):
    list_display = ("id","item_name", "category", "author", "active")
    filter_horizontal = ("watched_by_users",)

class BidAdmin(admin.ModelAdmin):
    list_display = ("id","date", "amount", "author", "auction")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("id","date", "author", "auction")
   

# Register your models here.
admin.site.register(User)
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Category)
admin.site.register(Comment, CommentAdmin)