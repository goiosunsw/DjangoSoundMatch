# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SoundRefAB', '0003_auto_20160125_1401'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='instruction_text',
            field=models.CharField(default=b'Please pick a sound', max_length=1000),
        ),
    ]
