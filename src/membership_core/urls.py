from django.urls import path
from rest_framework.routers import SimpleRouter

from .api import CountryManagement, SystemCurrencyManagement
from .catalogs import catalog_country, catalog_currency
from .views import UserListView, AddUser, EditUser, delete_user,\
    deactivate_user, groups_list, EditGroup, delete_group, index

router = SimpleRouter()
router.register('catalog/api/countries', CountryManagement, 'api-country')
router.register('catalog/api/currencies', SystemCurrencyManagement, 'api-currency')

urlpatterns = [
    path('home/', index, name="home"),
    path('users/list/', UserListView.as_view(), name="user_list"),
    path('users/create', AddUser.as_view(), name="create_user"),
    path('users/edit/<int:pk>', EditUser.as_view(), name="edit_user"),
    path('users/delete/<int:pk>/', delete_user, name="delete_user"),
    path('users/deactivate/<int:pk>/', deactivate_user, name="deactivate_user"),
    path('groups/', groups_list, name="groups_list"),
    path('groups/edit/<int:pk>', EditGroup.as_view(), name="edit_group"),
    path('groups/delete/<int:pk>/', delete_group, name="delete_group"),
    path('catalog/countries/', catalog_country, name="catalog_country"),
    path('catalog/currencies/', catalog_currency, name="catalog_currency"),
] + router.urls
