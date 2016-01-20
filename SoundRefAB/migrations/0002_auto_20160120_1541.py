# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SoundRefAB', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='function',
        ),
        migrations.AddField(
            model_name='page',
            name='template',
            field=models.CharField(default=b'', max_length=100, verbose_name=b'Page file'),
        ),
        migrations.AddField(
            model_name='soundtriplet',
            name='playseq',
            field=models.SlugField(default=b''),
        ),
    ]
