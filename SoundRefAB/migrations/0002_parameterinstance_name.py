# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SoundRefAB', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameterinstance',
            name='name',
            field=models.CharField(default=b'', max_length=100),
        ),
    ]
