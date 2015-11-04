# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SoundRefAB', '0002_parameterinstance_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Scenario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('created_date', models.DateTimeField(verbose_name=b'date created')),
            ],
        ),
        migrations.AddField(
            model_name='experiment',
            name='design',
            field=models.CharField(default=b'Reference-A-B', max_length=100, verbose_name=b'Design class', choices=[(b'Reference-A-B', b'Reference presented with N sounds, single choice'), (b'Adjust', b'Reference presented with single adjustable sound')]),
        ),
        migrations.AddField(
            model_name='experiment',
            name='scenarios',
            field=models.ManyToManyField(to='SoundRefAB.Scenario'),
        ),
    ]
