#ZUERST IN DIE DOCKER KONSOLE WECHSELN UND DJANGO SHELL STARTEN:
#docker exec -it webshop-web-1 bash
#python manage.py shell

# user erstellen
from django.contrib.auth.models import User
user = User.objects.create_user("tim", "tim131103@gmail.com", "1234")
user.first_name = "Tim"
user.last_name = "Lietzow"
user.save()

user = User.objects.create_user("zoe", "zoe.hartmann@gmail.com", "1234")
user.first_name = "Zoe"
user.last_name = "Hartmann"
user.save()

user = User.objects.create_user("vicent", "vincent.thach@gmail.com", "1234")
user.first_name = "Vincent"
user.last_name = "Thach"
user.save()

# group erstellen
from django.contrib.auth.models import Group, Permission
admins = Group.objects.create(name="Admins")
editors = Group.objects.create(name="Editors")
readers = Group.objects.create(name="Readers")

# user Gruppe zuweisen
from django.contrib.auth.models import User, Group
user = User.objects.get(username="tim")
readers.user_set.add(user)

user = User.objects.get(username="lykka")
editors.user_set.add(user)

user = User.objects.get(username="zoe")
admins.user_set.add(user)
user = User.objects.get(username="vincent")
admins.user_set.add(user)

# permissions zuweisen
from django.contrib.auth.models import Group, Permission
admins = Group.objects.get(name="Admins")
editors = Group.objects.get(name="Editors")
readers = Group.objects.get(name="Readers")

# alle Rechte für Admins
all_permissions = Permission.objects.all()
admins.permissions.set(all_permissions)
admins.save()

# Rechte für Editors
from django.contrib.auth.models import Permission, Group

editors = Group.objects.get(name="Editors")
perms_codenames = [
    "add_cart", "change_cart", "delete_cart", "view_cart",
    "add_cartitem", "change_cartitem", "delete_cartitem", "view_cartitem",
    "add_category", "change_category", "delete_category", "view_category",
    "add_customer", "change_customer", "delete_customer", "view_customer",
    "add_order", "change_order", "delete_order", "view_order",
    "add_orderitem", "change_orderitem", "delete_orderitem", "view_orderitem",
    "add_product", "change_product", "delete_product", "view_product",
    "add_wishlist", "change_wishlist", "delete_wishlist", "view_wishlist",
    "add_wishlistitem", "change_wishlistitem", "delete_wishlistitem", "view_wishlistitem",
]

perms = Permission.objects.filter(codename__in=perms_codenames)
editors.permissions.add(*perms)

# Rechte für Readers
from django.contrib.auth.models import Permission, Group

perms = Permission.objects.filter(codename__in=["view_cart", "view_cartitem", "view_category", "view_customer", "view_order", "view_orderitem", "view_product", "view_wishlist", "view_wishlistitem"])
readers = Group.objects.get(name="Readers")
readers.permissions.add(*perms)



