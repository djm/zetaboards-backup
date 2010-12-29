from django.contrib import admin

from forum.models import Forum, Thread, Post, User, UserGroup


class ForumAdmin(admin.ModelAdmin):
    list_display = ['title', 'zeta_id', 'parent', 'topics', 'replies', 'ordering']
    list_editable = ['ordering']
    search_fields = ['title', 'zeta_id']


class PostAdminInline(admin.StackedInline):
    model = Post
    extra = 0


class ThreadAdmin(admin.ModelAdmin):
    inlines = [PostAdminInline]
    list_display = ['title', 'user', 'zeta_id', 'forum', 'replies', 'views', 
                        'date_posted']
    search_fields = ['title', 'subtitle', 'zeta_id']


class PostAdmin(admin.ModelAdmin):
    list_display = ['zeta_id', 'thread', 'user', 'date_posted']
    search_fields = ['thread__title', 'zeta_id']


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'zeta_id', 'user_group', 'member_number']
    search_fields = ['username']

class UserGroupAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']

admin.site.register(Forum, ForumAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(UserGroup, UserGroupAdmin)
