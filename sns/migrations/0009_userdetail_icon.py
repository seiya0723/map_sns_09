# Generated by Django 3.2.12 on 2022-08-20 02:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sns', '0008_userdetail'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdetail',
            name='icon',
            field=models.ImageField(blank=True, null=True, upload_to='sns/user_detail/icon/', verbose_name='アイコン'),
        ),
    ]
