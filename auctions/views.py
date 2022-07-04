
from django.contrib.auth import authenticate, login, logout, get_user
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.forms import modelform_factory
from .models import Auction, User, Category, Bid, Comment
from .forms import AuctionForm, BidForm
from django.db.models import Max

def index(request):
 
    active_auctions = Auction.objects.filter(active=True)

    auctions = auctions_list_with_max_bids(active_auctions)

    return render(request, "auctions/index.html", {
        "auctions": auctions,
        "page_header": "Active auctions"
    })

@login_required
def my_lots(request):
    current_user = get_user(request=request) 
    a = Auction.objects.filter(author=current_user)  
    auctions = auctions_list_with_max_bids(a)
    return render(request, "auctions/index.html", {
        "auctions": auctions,
        "page_header": "My lots"
    }) 

def categoties(request):
    c = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": c
    })

def categoty_auctions(request, category_id):
    category = Category.objects.get(pk=category_id) 
    a = Auction.objects.filter(category=category)
    auctions = auctions_list_with_max_bids(a)
    return render(request, "auctions/index.html", {
        "auctions": auctions,
        "page_header": f"Auctions in category {category.name}"
    }) 

@login_required
def watchlist(request):
    current_user = get_user(request=request)
    auctions = Auction.objects.filter(watched_by_users=current_user)
    auctions = auctions_list_with_max_bids(auctions)
    return render(request, "auctions/index.html", {
        "auctions": auctions,
        "page_header": "My watchlist"
    }) 

@login_required
def related_auctions(request):
    current_user = get_user(request=request)
    auctions = set()
    for bid in Bid.objects.select_related("auction").filter(author=current_user):
        auctions.add(bid.auction)
   
    auctions = auctions_list_with_max_bids(auctions)
   
    return render(request, "auctions/index.html", {
        "auctions": auctions,
        "page_header": "Auctions with my bids"
    }) 

@login_required
def add_to_watchlist(request, auction_id):
    a = Auction.objects.get(pk=auction_id)
    current_user = get_user(request=request)
    a.watched_by_users.add(current_user)
    a.save()
    return HttpResponseRedirect(reverse("auction",kwargs={"auction_id": auction_id}))

@login_required
def remove_from_watchlist(request, auction_id):
    a = Auction.objects.get(pk=auction_id)
    current_user = get_user(request=request)
    a.watched_by_users.remove(current_user)
    a.save()
    return HttpResponseRedirect(reverse("auction",kwargs={"auction_id": auction_id}))


@login_required
def close_auction(request, auction_id):
    a = Auction.objects.get(pk=auction_id)
    current_user = get_user(request=request)
    if a.author == current_user:
        a.active = False
        a.save()
    return HttpResponseRedirect(reverse("auction",kwargs={"auction_id": auction_id}))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def new(request):
    if request.method == "POST" and request.user.is_authenticated:

        form = AuctionForm(request.POST)
        item_name = request.POST["item_name"]
        item_description = request.POST["item_description"]
        start_bid = request.POST["start_bid"]
        picture_url = request.POST["picture_url"]
        category_pk = request.POST["category"]

        if category_pk != "":
            category = categoy = Category.objects.get(pk=category_pk)
        else:
            category = None

        a = Auction(item_name=item_name, item_description=item_description,
                    start_bid=start_bid, picture_url=picture_url, category=category,
                    author=request.user)

        if form.is_valid():
            a.save()
            return HttpResponseRedirect(reverse("index"), {
                "message": f"{a}"
            })
        else:
            return HttpResponseRedirect(reverse("new"), {
                "form": form
            })
    else:
        form = AuctionForm()
        return render(request, "auctions/new.html", {
            "form": form
        })


def auction(request, auction_id):
    a = Auction.objects.get(pk=auction_id)
    authorFullName = a.author.get_full_name()
    if authorFullName == '':
        authorFullName = a.author.username
    start_bid = a.start_bid
    current_user = get_user(request=request)
    bid_error_message = ''
    
    # bids
    bidform = BidForm()
    lastbid = get_max_bid(a)
    winner_user = False
    if lastbid != None:
        if not a.active and lastbid.author == current_user:
            winner_user = True        
        lastbid = lastbid.amount

    # comments
    comments = Comment.objects.filter(auction=a).order_by("-date")

    # watchlist
    is_watched = auction_is_watched(a, current_user)

    if request.method == "POST" and "amount" in request.POST:
        amount = float(request.POST["amount"])

        if lastbid == None and amount >= start_bid:
            save_new_bid(author=current_user, amount=amount, auction=a)
        elif lastbid != None:
            if amount > lastbid:
                save_new_bid(author=current_user, amount=amount, auction=a)
            else:
                bid_error_message = f'Bid {amount} is less than current bid {lastbid}. Please make bigger bid.'
        else:
            bid_error_message = f'Bid {amount} is less than start bid {start_bid}. Please make bigger bid.'

        return render(request, "auctions/auction.html", {
            "auction": a,
            "authorFullName": authorFullName,
            "bidform": bidform,
            "current_bid": amount if bid_error_message == '' else lastbid,
            "bid_error_message": bid_error_message,
            "bid_successfull": True if bid_error_message == '' else False,
            "comments": comments,
            "winner_user": winner_user,
            "is_watched": is_watched
        })
    if request.method == "POST" and "comment_text" in request.POST:
        comment_text = request.POST["comment_text"]
        new_comment = Comment(author=current_user, auction=a, text=comment_text)
        new_comment.save()
        comments = Comment.objects.filter(auction=a).order_by("-date")

    return render(request, "auctions/auction.html", {
        "auction": a,
        "authorFullName": authorFullName,
        "bidform": bidform,
        "current_bid": lastbid,
        "comments": comments,
        "winner_user": winner_user,
        "is_watched": is_watched
    })

def save_new_bid(author, amount, auction):
    newBid = Bid(author=author, amount=amount, auction=auction)
    newBid.save()

def auction_is_watched(auction, user):
   
    a = User.objects.filter(watched_list=auction)

    if user in a:
        return True
    else:
        return False

def get_max_bid(auction):
    bids = Bid.objects.filter(auction=auction)
    bids.order_by('amount')
    lastbid = bids.last()
    return lastbid

def auctions_list_with_max_bids(auctions):
    auctionslist = []
    for auction in auctions:
        maxbid = get_max_bid(auction=auction)
        if maxbid == None:
            maxbid = auction.start_bid
        else:
            maxbid = maxbid.amount

        auc_set = {
            "auction": auction,
            "maxbid": maxbid
        }
        auctionslist.append(auc_set)
    return auctionslist