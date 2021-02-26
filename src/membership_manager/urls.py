from django.urls import path
from membership_manager import views as base_views
from . import user_view


urlpatterns = [
    path('home/', base_views.index, name="home"),
    path('users/list/', user_view.UserListView.as_view(), name="user_list"),
    path('users/create', user_view.AddUser.as_view(), name="create_user"),
    path('users/edit/<int:pk>', user_view.EditUser.as_view(), name="edit_user"),
    path('users/delete/<int:pk>/', user_view.delete_user, name="delete_user"),
    path('users/deactivate/<int:pk>/', user_view.deactivate_user, name="deactivate_user"),
    path('groups/', user_view.groups_list, name="groups_list"),
    path('groups/edit/<int:pk>', user_view.EditGroup.as_view(), name="edit_group"),
    path('groups/delete/<int:pk>/', user_view.delete_group, name="delete_group"),
]
