# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(default=b'')),
            ],
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('created_date', models.DateTimeField(verbose_name=b'date created')),
                ('instruction_text', models.CharField(default=b'Please pick a sound', max_length=1000)),
                ('function', models.CharField(max_length=100, verbose_name=b'Sound generating function', choices=[(b'BrightnessAdjust', b'BrightnessAdjust'), (b'BrightnessAdjust_process', b'BrightnessAdjust_process'), (b'BrightnessIntro', b'BrightnessIntro'), (b'BrightnessIntro_process', b'BrightnessIntro_process'), (b'DescribeVibrato', b'DescribeVibrato'), (b'DescribeVibrato_process', b'DescribeVibrato_process'), (b'LoudnessAdjust', b'LoudnessAdjust'), (b'LoudnessAdjust_process', b'LoudnessAdjust_process'), (b'LoudnessIntro', b'LoudnessIntro'), (b'LoudnessIntro_process', b'LoudnessIntro_process'), (b'MatchVibratoTypes', b'MatchVibratoTypes'), (b'SlopeVibratoRefABC', b'SlopeVibratoRefABC'), (b'SlopeVibratoRefABC_init', b'SlopeVibratoRefABC_init'), (b'SlopeVibratoTripletRefAB', b'SlopeVibratoTripletRefAB'), (b'VibratoTripletRefAB', b'VibratoTripletRefAB')])),
                ('number_of_trials', models.IntegerField(default=1, verbose_name=b'Number of Trials')),
                ('design', models.CharField(default=b'soundpage', max_length=100, verbose_name=b'Design class', choices=[(b'soundpage', b'Reference presented with N sounds, single choice'), (b'soundadjustpage', b'Reference presented with single adjustable sound'), (b'intropage', b'Intro page collecting confidence and comment')])),
            ],
        ),
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
                ('template', models.CharField(default=b'', max_length=100, verbose_name=b'Page file', choices=[('pg_brightness_adj_intro.html', 'pg_brightness_adj_intro.html'), ('pg_loudness_adj_intro.html', 'pg_loudness_adj_intro.html'), ('pg_quest_info.html', 'pg_quest_info.html'), ('pg_thanks.html', 'pg_thanks.html'), ('pg_vibrato_explanation.html', 'pg_vibrato_explanation.html'), ('pg_vibrato_intro.html', 'pg_vibrato_intro.html')])),
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
            name='Questionnaire',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('created_date', models.DateTimeField(verbose_name=b'date created')),
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
            name='StringParameterInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=100)),
                ('value', models.CharField(default=b'', max_length=50, verbose_name=b'Value')),
                ('position', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateTimeField(auto_now_add=True, verbose_name=b'date Started')),
                ('finish_date', models.DateTimeField(auto_now_add=True, verbose_name=b'date Finished')),
                ('age', models.IntegerField(default=20, verbose_name=b'How old are you?')),
                ('music_experience', models.CharField(default=b'NO', max_length=2, verbose_name=b'Which better describes your musical experience?', choices=[(b'NO', b'No experience'), (b'AM', b'Amateur'), (b'ST', b'Music student'), (b'RG', b'Non-professional but perform in public'), (b'PR', b'Professional')])),
                ('hearing_prob', models.CharField(default=b'NH', max_length=2, verbose_name=b'Do you experience any hearing problems?', choices=[(b'NH', b'I have normal hearing'), (b'SL', b'I have slight hearing loss'), (b'HL', b'I have considerable hearing loss')])),
                ('device', models.CharField(default=b'PH', max_length=2, verbose_name=b'How are you listening to the sounds in this test?', choices=[(b'CO', b'Computer loudspeakers'), (b'LA', b'Laptop loudspeakers'), (b'PD', b'Phone or tablet loudspeakers'), (b'EX', b'External amplified loudspeakers'), (b'PH', b'Headphones')])),
                ('final_comment', models.TextField(default=b'', verbose_name=b'Any final comments about the experiment?')),
                ('exp_id', models.IntegerField(default=0)),
                ('trials_done', models.IntegerField(default=0)),
                ('total_trials', models.IntegerField(default=0)),
                ('stop_experiment', models.BooleanField(default=False)),
                ('difficulty_divider', models.DecimalField(default=1.0, max_digits=10, decimal_places=2)),
                ('instrument', models.CharField(default=b'', max_length=100, verbose_name=b'Sing or play any instrument? Which?')),
                ('student_ID', models.CharField(default=b'', max_length=10, verbose_name=b'Student ID')),
                ('loudspeaker_model', models.CharField(default=b'', max_length=10, verbose_name=b'Model of headphones / speakers (if appliccable)')),
                ('vol_change', models.BooleanField(default=False, verbose_name=b'Did you adjust the volume during the experiment?')),
                ('scenario', models.ForeignKey(to='SoundRefAB.Scenario')),
            ],
        ),
        migrations.AddField(
            model_name='stringparameterinstance',
            name='subject',
            field=models.ForeignKey(to='SoundRefAB.Subject'),
        ),
        migrations.AddField(
            model_name='stringparameterinstance',
            name='trial',
            field=models.ForeignKey(to='SoundRefAB.SoundTriplet'),
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
        migrations.AddField(
            model_name='experimentresults',
            name='subject',
            field=models.ForeignKey(to='SoundRefAB.Subject'),
        ),
        migrations.AddField(
            model_name='comment',
            name='subject',
            field=models.ForeignKey(to='SoundRefAB.Subject'),
        ),
        migrations.AddField(
            model_name='comment',
            name='trial',
            field=models.ForeignKey(to='SoundRefAB.SoundTriplet'),
        ),
    ]
