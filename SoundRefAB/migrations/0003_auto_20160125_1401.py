# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SoundRefAB', '0002_auto_20160122_1055'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExperimentResults',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=100)),
                ('value', models.DecimalField(default=0.0, verbose_name=b'Value', max_digits=10, decimal_places=2)),
                ('experiment', models.ForeignKey(to='SoundRefAB.Experiment')),
            ],
        ),
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('created_date', models.DateTimeField(verbose_name=b'date created')),
            ],
        ),
        migrations.RemoveField(
            model_name='subject',
            name='age_group',
        ),
        migrations.AddField(
            model_name='subject',
            name='age',
            field=models.IntegerField(default=20, verbose_name=b'How old are you?'),
        ),
        migrations.AddField(
            model_name='subject',
            name='final_comment',
            field=models.TextField(default=b'', verbose_name=b'Any final comments about the experiment?'),
        ),
        migrations.AlterField(
            model_name='page',
            name='template',
            field=models.CharField(default=b'', max_length=100, verbose_name=b'Page file', choices=[('pg_brightness_adj_intro.html', 'pg_brightness_adj_intro.html'), ('pg_loudness_adj_intro.html', 'pg_loudness_adj_intro.html'), ('pg_quest_info.html', 'pg_quest_info.html'), ('pg_thanks.html', 'pg_thanks.html'), ('pg_vibrato_intro.html', 'pg_vibrato_intro.html'), ('pg_welcome.html', 'pg_welcome.html')]),
        ),
        migrations.AlterField(
            model_name='subject',
            name='music_experience',
            field=models.CharField(default=b'NO', max_length=2, verbose_name=b'Which better describes your musical experience?', choices=[(b'NO', b'No experience'), (b'AM', b'Amateur'), (b'ST', b'Music student'), (b'RG', b'Non-professional but perform in public'), (b'PR', b'Professional')]),
        ),
        migrations.AddField(
            model_name='experimentresults',
            name='subject',
            field=models.ForeignKey(to='SoundRefAB.Subject'),
        ),
    ]
