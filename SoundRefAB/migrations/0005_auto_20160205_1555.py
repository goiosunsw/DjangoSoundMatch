# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SoundRefAB', '0004_experiment_instruction_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='instrument',
            field=models.CharField(default=b'', max_length=100, verbose_name=b'Sing or play any instrument? Which?'),
        ),
        migrations.AddField(
            model_name='subject',
            name='student_ID',
            field=models.CharField(default=b'', max_length=100, verbose_name=b'Student ID'),
        ),
        migrations.AlterField(
            model_name='experiment',
            name='design',
            field=models.CharField(default=b'soundpage', max_length=100, verbose_name=b'Design class', choices=[(b'soundpage', b'Reference presented with N sounds, single choice'), (b'soundadjustpage', b'Reference presented with single adjustable sound'), (b'intropage', b'Intro page collecting confidence and comment')]),
        ),
        migrations.AlterField(
            model_name='experiment',
            name='function',
            field=models.CharField(max_length=100, verbose_name=b'Sound generating function', choices=[(b'BrightnessAdjust', b'BrightnessAdjust'), (b'BrightnessAdjust_process', b'BrightnessAdjust_process'), (b'BrightnessIntro', b'BrightnessIntro'), (b'BrightnessIntro_process', b'BrightnessIntro_process'), (b'LoudnessAdjust', b'LoudnessAdjust'), (b'LoudnessAdjust_process', b'LoudnessAdjust_process'), (b'SlopeVibratoRefABC', b'SlopeVibratoRefABC'), (b'SlopeVibratoTripletRefAB', b'SlopeVibratoTripletRefAB'), (b'VibratoTripletRefAB', b'VibratoTripletRefAB')]),
        ),
        migrations.AlterField(
            model_name='subject',
            name='hearing_prob',
            field=models.CharField(default=b'NH', max_length=2, verbose_name=b'Do you experience any hearing problems?', choices=[(b'NH', b'I have normal hearing'), (b'SL', b'I have slight hearing loss'), (b'HL', b'I have considerable hearing loss')]),
        ),
    ]
