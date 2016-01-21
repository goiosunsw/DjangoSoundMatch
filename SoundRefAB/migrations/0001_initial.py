# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('created_date', models.DateTimeField(verbose_name=b'date created')),
                ('function', models.CharField(max_length=100, verbose_name=b'Sound generating function', choices=[(b'LoudnessAdjust', b'LoudnessAdjust'), (b'SlopeVibratoTripletRefAB', b'SlopeVibratoTripletRefAB'), (b'VibratoTripletRefAB', b'VibratoTripletRefAB')])),
                ('number_of_trials', models.IntegerField(default=1, verbose_name=b'Number of Trials')),
                ('design', models.CharField(default=b'soundpage', max_length=100, verbose_name=b'Design class', choices=[(b'soundpage', b'Reference presented with N sounds, single choice'), (b'soundadjustpage', b'Reference presented with single adjustable sound')])),
            ],
        ),
        migrations.CreateModel(
            name='ItemInScenario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('order', models.IntegerField(default=1, verbose_name=b'Order in Scenario')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('created_date', models.DateTimeField(verbose_name=b'date created')),
                ('template', models.CharField(default=b'', max_length=100, verbose_name=b'Page file', choices=[('pg_brightness_adj_intro.html', 'pg_brightness_adj_intro.html'), ('pg_loudness_adj_intro.html', 'pg_loudness_adj_intro.html'), ('pg_vibrato_intro.html', 'pg_vibrato_intro.html'), ('pg_welcome.html', 'pg_welcome.html')])),
            ],
        ),
        migrations.CreateModel(
            name='ParameterInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=100)),
                ('value', models.DecimalField(default=0.0, verbose_name=b'Value', max_digits=10, decimal_places=2)),
                ('position', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Scenario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('created_date', models.DateTimeField(verbose_name=b'date created')),
            ],
        ),
        migrations.CreateModel(
            name='SoundTriplet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shown_date', models.DateTimeField(auto_now_add=True, verbose_name=b'date triplet shown to user')),
                ('valid_date', models.DateTimeField(auto_now_add=True, verbose_name=b'date triplet validated by user')),
                ('confidence', models.IntegerField(default=0)),
                ('playseq', models.SlugField(default=b'')),
                ('trial', models.IntegerField(default=0)),
                ('choice', models.IntegerField(default=0)),
                ('experiment', models.ForeignKey(to='SoundRefAB.Experiment')),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateTimeField(auto_now_add=True, verbose_name=b'date Started')),
                ('finish_date', models.DateTimeField(auto_now_add=True, verbose_name=b'date Finished')),
                ('age_group', models.CharField(default=b'25', max_length=2, verbose_name=b'What is your age group?', choices=[(b'15', b'under 15'), (b'25', b'15-25'), (b'35', b'25-35'), (b'45', b'35-45'), (b'55', b'55-65'), (b'65', b'65-75'), (b'75', b'75 or more')])),
                ('music_experience', models.CharField(default=b'NO', max_length=2, verbose_name=b'Which better describes your musical experience?', choices=[(b'NO', b'No experience'), (b'AM', b'Amateur'), (b'ST', b'Music student, less than 8 years'), (b'AD', b'Music student, more than 8 years'), (b'RG', b'Non-professional but perform in public'), (b'PR', b'Professional')])),
                ('hearing_prob', models.BooleanField(default=False, verbose_name=b'Do you experience hearing loss?')),
                ('device', models.CharField(default=b'PH', max_length=2, verbose_name=b'How are you listening to the sounds in this test?', choices=[(b'CO', b'Computer loudspeakers'), (b'LA', b'Laptop loudspeakers'), (b'PD', b'Phone or tablet loudspeakers'), (b'EX', b'External amplified loudspeakers'), (b'PH', b'Headphones')])),
                ('exp_id', models.IntegerField(default=0)),
                ('trials_done', models.IntegerField(default=0)),
                ('stop_experiment', models.BooleanField(default=False)),
                ('difficulty_divider', models.DecimalField(default=1.0, max_digits=10, decimal_places=2)),
                ('scenario', models.ForeignKey(to='SoundRefAB.Scenario')),
            ],
        ),
        migrations.AddField(
            model_name='soundtriplet',
            name='subject',
            field=models.ForeignKey(to='SoundRefAB.Subject'),
        ),
        migrations.AddField(
            model_name='parameterinstance',
            name='subject',
            field=models.ForeignKey(to='SoundRefAB.Subject'),
        ),
        migrations.AddField(
            model_name='parameterinstance',
            name='trial',
            field=models.ForeignKey(to='SoundRefAB.SoundTriplet'),
        ),
        migrations.AddField(
            model_name='iteminscenario',
            name='scenario',
            field=models.ForeignKey(to='SoundRefAB.Scenario'),
        ),
    ]
