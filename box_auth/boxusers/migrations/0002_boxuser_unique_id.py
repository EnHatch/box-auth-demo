# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('boxusers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='boxuser',
            name='unique_id',
            field=models.TextField(default='0'),
            preserve_default=False,
        ),
    ]
