from django.db import migrations, models
import django.db.models.deletion


def copy_item_snapshots(apps, schema_editor):
    TransactionItem = apps.get_model("core", "TransactionItem")

    for line in TransactionItem.objects.select_related("item"):
        if line.item:
            line.item_name = line.item.name
            line.item_price = line.item.price
            line.save(update_fields=["item_name", "item_price"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="transactionitem",
            name="item_name",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name="transactionitem",
            name="item_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.RunPython(copy_item_snapshots, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="transactionitem",
            name="item",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="sales",
                to="core.item",
            ),
        ),
    ]
