# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SoundRefAB', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(default=b'')),
                ('subject', models.ForeignKey(to='SoundRefAB.Subject')),
                ('trial', models.ForeignKey(to='SoundRefAB.SoundTriplet')),
            ],
        ),
        migrations.CreateModel(
            name='StringParameterInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=100)),
                ('value', models.CharField(default=b'', max_length=50, verbose_name=b'Value')),
                ('position', models.IntegerField(default=0)),
                ('subject', models.ForeignKey(to='SoundRefAB.Subject')),
                ('trial', models.ForeignKey(to='SoundRefAB.SoundTriplet')),
            ],
        ),
        migrations.AlterField(
            model_name='experiment',
            name='function',
            field=models.CharField(max_length=100, verbose_name=b'Sound generating function', choices=[(b'BrightnessAdjust', b'BrightnessAdjust'), (b'LoudnessAdjust', b'LoudnessAdjust'), (b'SlopeVibratoTripletRefAB', b'SlopeVibratoTripletRefAB'), (b'VibratoTripletRefAB', b'VibratoTripletRefAB')]),
        ),
        migrations.AlterField(
            model_name='page',
            name='template',
            field=models.CharField(default=b'', max_length=100, verbose_name=b'Page file', choices=[('pg_brightness_adj_intro.html', 'pg_brightness_adj_intro.html'), ('pg_loudness_adj_intro.html', 'pg_loudness_adj_intro.html'), ('pg_thanks.html', 'pg_thanks.html'), ('pg_vibrato_intro.html', 'pg_vibrato_intro.html'), ('pg_welcome.html', 'pg_welcome.html')]),
        ),
    ]
