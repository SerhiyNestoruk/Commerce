# Generated by Django 4.0.4 on 2022-07-03 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0013_alter_auction_start_bid_alter_bid_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='amount',
            field=models.PositiveIntegerField(),
        ),
    ]
