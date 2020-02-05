# Generated by Django 3.0.3 on 2020-02-05 06:04

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.embeds.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0004_auto_20200205_0545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='content',
            field=wagtail.core.fields.StreamField([('paragraph', wagtail.core.blocks.RichTextBlock()), ('pro_paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('pro_image', wagtail.images.blocks.ImageChooserBlock()), ('embed', wagtail.embeds.blocks.EmbedBlock()), ('pro_embed', wagtail.embeds.blocks.EmbedBlock()), ('code', wagtail.core.blocks.StructBlock([('code', wagtail.core.blocks.TextBlock()), ('lang', wagtail.core.blocks.ChoiceBlock(choices=[('python', 'Python'), ('bash', 'Bash'), ('javascript', 'Javascript'), ('json', 'JSON')], icon='cup', required=False))])), ('pro_code', wagtail.core.blocks.StructBlock([('code', wagtail.core.blocks.TextBlock()), ('lang', wagtail.core.blocks.ChoiceBlock(choices=[('python', 'Python'), ('bash', 'Bash'), ('javascript', 'Javascript'), ('json', 'JSON')], icon='cup', required=False))]))], blank=True),
        ),
    ]
