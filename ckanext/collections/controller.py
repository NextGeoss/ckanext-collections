# encoding: utf-8

import re
import logging
from urllib import urlencode
import datetime
import mimetypes
import cgi

import ckan.plugins as plugins
import ckan.model as model
import ckan.logic as logic
import ckan.lib.render
import ckan.lib.base as base
import ckan.lib.i18n as i18n
import ckan.lib.helpers as h

from ckan.common import OrderedDict, _, json, request, c, response

from ckan.controllers.group import GroupController
from ckan.controllers.package import PackageController

log = logging.getLogger(__name__)

render = base.render
abort = base.abort

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
flatten_to_string_key = logic.flatten_to_string_key


class CollectionController(GroupController):
    ''' The collection controller is for Collections, which are implemented
    as Groups with group_type='collection'.

    '''

    group_types = ['collection']


class CollectionsPackageController(PackageController):
    ''' Override of the package controller in order to list only Groups in
    the Group tab available on Dataset edit, and add a Collections tab which
    will allow the users to associate a Dataset with a Collection and
    remove the association.
    '''

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

        context['is_member'] = True
        users_groups = get_action('group_list_authz')(context, data_dict)

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

            package_groups = set(group['id'] for group in users_groups if group['type'] == 'group')
            new_pkg_dict = [group for group in c.pkg_dict.get('groups') if group['id'] in package_groups]

            c.pkg_dict['groups'] = new_pkg_dict

            h.redirect_to(controller='package', action='groups', id=id)

        pkg_group_ids = set(group['id'] for group
                            in c.pkg_dict.get('groups', []))
        user_group_ids = set(group['id'] for group
                             in users_groups)

        # groups that
        package_groups = set(group['id'] for group in users_groups if group['type'] == 'group')
        new_pkg_dict = [group for group in c.pkg_dict.get('groups') if group['id'] in package_groups]

        c.pkg_dict['groups'] = new_pkg_dict

        c.group_dropdown = [[group['id'], group['display_name']]
                            for group in users_groups if
                            group['id'] not in pkg_group_ids and group['type'] == 'group']

        for group in c.pkg_dict.get('groups', []):
            group['user_member'] = (group['id'] in user_group_ids)


        return render('package/group_list.html',
                      {'dataset_type': dataset_type})


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

        context['is_member'] = True
        users_groups = get_action('group_list_authz')(context, data_dict)

        if request.method == 'POST':
            new_group = request.POST.get('collection_added')

            if new_group:
                data_dict = {"id": new_group,
                             "object": id,
                             "object_type": 'package',
                             "capacity": 'public'}
                try:
                    get_action('member_create')(context, data_dict)
                except NotFound:
                    abort(404, _('Collection not found'))

            removed_group = None
            for param in request.POST:
                if param.startswith('collection_remove'):
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

            package_groups = set(group['id'] for group in users_groups if group['type'] == 'collection')
            new_pkg_dict = [group for group in c.pkg_dict.get('groups') if group['id'] in package_groups]

            c.pkg_dict['groups'] = new_pkg_dict

            package_controller = "ckanext.collections.controller:CollectionsPackageController"
            h.redirect_to(controller=package_controller, action='collections', id=id)

        pkg_group_ids = set(group['id'] for group
                            in c.pkg_dict.get('groups', []))
        user_group_ids = set(group['id'] for group
                             in users_groups)

        package_groups = set(group['id'] for group in users_groups if group['type'] == 'collection')
        new_pkg_dict = [group for group in c.pkg_dict.get('groups') if group['id'] in package_groups]

        c.pkg_dict['groups'] = new_pkg_dict

        c.collection_dropdown = [[group['id'], group['display_name']]
                            for group in users_groups if
                            group['id'] not in pkg_group_ids and group['type'] == 'collection']

        for group in c.pkg_dict.get('groups', []):
            group['user_member'] = (group['id'] in user_group_ids)

        return render('package/collection_list.html',
                      {'dataset_type': dataset_type})