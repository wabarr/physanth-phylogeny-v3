from __future__ import unicode_literals

from django.db import migrations

import re

def updateLinks(apps,schema_editor):
    PhDModel = apps.get_model("academicPhylogeny", "PhD")
    for each in PhDModel.objects.filter(pk__in=(191,1721,1041,1206,1066,1769,1726,1061,1737,1183,1493,1444,864,694,1093,761,392,1624,1497,235,1511,1081,2150,1660)):
        regex = r"\(|\)|\'|\""
        each.URL_for_detail = re.sub(regex, "", (each.firstName + "_" + each.lastName).replace(" ", "_"))
        each.save()


class Migration(migrations.Migration):

    dependencies = [
        ('academicPhylogeny', '0018_auto_20170801_1200'),
    ]

    operations = [
        migrations.RunPython(updateLinks)
    ]
