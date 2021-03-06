# Generated by Django 4.0.4 on 2022-06-24 13:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auction_category_comment_bid_auction_categoy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='categoy',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='category', to='auctions.category'),
        ),
        migrations.AlterField(
            model_name='auction',
            name='picture_url',
            field=models.URLField(blank=True),
        ),
    ]
