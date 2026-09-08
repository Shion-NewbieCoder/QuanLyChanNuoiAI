from django.db import migrations


ROLE_NAMES = (
    "quản lý",
    "kỹ thuật viên",
    "nhân viên",
)


def create_roles(apps, schema_editor):
    group_model = apps.get_model("auth", "Group")
    permission_model = apps.get_model("auth", "Permission")
    content_type_model = apps.get_model("contenttypes", "ContentType")

    for role_name in ROLE_NAMES:
        group_model.objects.get_or_create(name=role_name)

    management_group = group_model.objects.get(name="quản lý")
    user_content_type, _ = content_type_model.objects.get_or_create(
        app_label="auth",
        model="user",
    )
    view_user_permission, _ = permission_model.objects.get_or_create(
        content_type=user_content_type,
        codename="view_user",
        defaults={"name": "Can view user"},
    )
    management_group.permissions.add(view_user_permission)


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(create_roles, migrations.RunPython.noop),
    ]
