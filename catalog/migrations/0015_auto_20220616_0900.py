# Generated by Django 3.2.7 on 2022-06-16 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0014_alter_bookinstance_status'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Status',
        ),
        migrations.AlterField(
            model_name='bookinstance',
            name='status',
            field=models.IntegerField(null=True),
        ),
    ]
