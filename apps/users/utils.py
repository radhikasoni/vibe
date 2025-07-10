def user_filter(request):
    filter_string = {}
    filter_mappings = {
        'search': 'username__icontains'
    }
    for key in request.GET:
        if request.GET.get(key) and key != 'page':
            filter_string[filter_mappings[key]] = request.GET.get(key)

    return filter_string


def profile_user_filter(request):
    filter_string = {}

    search = request.GET.get('search')
    if search:
        # Broad search across multiple fields
        return {
            'user__username__icontains': search,
        }

    # Specific filters
    filter_mappings = {
        'username': 'user__username__icontains',
        'first_name': 'user__first_name__icontains',
        'last_name': 'user__last_name__icontains',
        'email': 'user__email__icontains',
        'role': 'role',
        'city': 'city__icontains',
        'country': 'country__icontains',
    }

    for key, lookup in filter_mappings.items():
        value = request.GET.get(key)
        if value:
            filter_string[lookup] = value

    return filter_string
