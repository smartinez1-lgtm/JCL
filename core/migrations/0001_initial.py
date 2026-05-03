# Generated manually to provide a ready-to-run initial schema for the project.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Item",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("description", models.TextField(blank=True, null=True)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("quantity", models.IntegerField(default=0)),
                ("date_added", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateTimeField(auto_now_add=True)),
                ("total_amount", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ],
            options={
                "ordering": ["-date"],
            },
        ),
        migrations.CreateModel(
            name="TransactionItem",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.IntegerField()),
                ("subtotal", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sales",
                        to="core.item",
                    ),
                ),
                (
                    "transaction",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transaction_items",
                        to="core.transaction",
                    ),
                ),
            ],
        ),
    ]
