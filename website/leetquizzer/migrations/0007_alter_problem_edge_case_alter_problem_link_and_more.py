# Generated by Django 4.2.2 on 2023-06-20 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leetquizzer', '0006_problem_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='edge_case',
            field=models.TextField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='problem',
            name='link',
            field=models.URLField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='problem',
            name='option1',
            field=models.TextField(max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='problem',
            name='option2',
            field=models.TextField(max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='problem',
            name='solution',
            field=models.TextField(max_length=300, null=True),
        ),
    ]