# Generated by Django 3.1.2 on 2020-10-25 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_code', models.CharField(max_length=10)),
                ('customer_name', models.CharField(max_length=50)),
                ('birthday', models.DateField(blank=True, null=True)),
                ('gender', models.IntegerField(choices=[(0, 'Nam'), (1, 'Nữ')], default=0)),
                ('phone_number', models.CharField(max_length=10)),
                ('email', models.EmailField(default='', max_length=50)),
                ('address', models.CharField(default='', max_length=255)),
                ('note', models.TextField(default='')),
                ('group_type', models.IntegerField(choices=[(0, 'Normal'), (1, 'VIP')], default=0)),
                ('points', models.PositiveIntegerField(default=0)),
            ],
        ),
    ]