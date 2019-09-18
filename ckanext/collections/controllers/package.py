# encoding: utf-8

import re

import ckan.controllers.package as package
import ckan.plugins as plugins


class CollectionsPackageController(package.PackageController):
    def collections(self, id):
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'for_view': True,
                   'auth_user_obj': c.userobj, 'use_cache': False}
        data_dict = {'id': id}
        try:
            c.pkg_dict = get_action('package_show')(context, data_dict)
            dataset_type = c.pkg_dict['type'] or 'dataset'
        except (NotFound, NotAuthorized):
            abort(404, _('Dataset not found'))

        if request.method == 'POST':
            new_group = request.POST.get('group_added')
            if new_group:
                data_dict = {"id": new_group,
                             "object": id,
                             "object_type": 'package',
                             "capacity": 'public'}
                try:
                    get_action('member_create')(context, data_dict)
                except NotFound:
                    abort(404, _('Group not found'))

            removed_group = None
            for param in request.POST:
                if param.startswith('group_remove'):
                    removed_group = param.split('.')[-1]
                    break
            if removed_group:
                data_dict = {"id": removed_group,
                             "object": id,
                             "object_type": 'package'}

                try:
                    get_action('member_delete')(context, data_dict)
                except NotFound:
                    abort(404, _('Collection not found'))
            h.redirect_to(controller='package', action='groups', id=id)

        context['is_member'] = True
        users_groups = get_action('group_list_authz')(context, data_dict)

        pkg_group_ids = set(group['id'] for group
                            in c.pkg_dict.get('groups', []))
        user_group_ids = set(group['id'] for group
                             in users_groups)

        c.collection_dropdown = [[group['id'], group['display_name']]
                            for group in users_groups if
                            (group['id'] not in pkg_group_ids and group['type'] == 'collection')]

        for group in c.pkg_dict.get('groups', []):
            group['user_member'] = (group['id'] in user_group_ids)

        return render('package/collection_list.html',
                      {'dataset_type': dataset_type})


    def groups(self, id):
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'for_view': True,
                   'auth_user_obj': c.userobj, 'use_cache': False}
        data_dict = {'id': id}
        try:
            c.pkg_dict = get_action('package_show')(context, data_dict)
            dataset_type = c.pkg_dict['type'] or 'dataset'
        except (NotFound, NotAuthorized):
            abort(404, _('Dataset not found'))

        if request.method == 'POST':
            new_group = request.POST.get('group_added')
            if new_group:
                data_dict = {"id": new_group,
                             "object": id,
                             "object_type": 'package',
                             "capacity": 'public'}
                try:
                    get_action('member_create')(context, data_dict)
                except NotFound:
                    abort(404, _('Group not found'))

            removed_group = None
            for param in request.POST:
                if param.startswith('group_remove'):
                    removed_group = param.split('.')[-1]
                    break
            if removed_group:
                data_dict = {"id": removed_group,
                             "object": id,
                             "object_type": 'package'}

                try:
                    get_action('member_delete')(context, data_dict)
                except NotFound:
                    abort(404, _('Group not found'))
            h.redirect_to(controller='package', action='groups', id=id)

        context['is_member'] = True
        users_groups = get_action('group_list_authz')(context, data_dict)

        pkg_group_ids = set(group['id'] for group
                            in c.pkg_dict.get('groups', []))
        user_group_ids = set(group['id'] for group
                             in users_groups)

        for g in user_group_ids:
            print g['type']

        c.group_dropdown = [[group['id'], group['display_name']]
                            for group in users_groups if
                            group['id'] not in pkg_group_ids]


        for group in c.pkg_dict.get('groups', []):
            group['user_member'] = (group['id'] in user_group_ids)

        return render('package/group_list.html',
                      {'dataset_type': dataset_type})
