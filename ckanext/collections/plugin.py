import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic.schema as ckan_schema

import routes


class CollectionsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IGroupForm, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)

    def group_types(self):
		return ('collection',)

    def group_controller(self):
    	return 'collection'

    def is_fallback(self):
		False

    def form_to_db_schema(self):
        schema = ckan_schema.group_form_schema()
        schema.update({
            'collection_id': [toolkit.get_validator('not_empty'), toolkit.get_converter('convert_to_extras')],
        })
        return schema

    def db_to_form_schema(self):
        schema = ckan_schema.group_form_schema()
        schema.update({
            'collection_id': [toolkit.get_converter('convert_from_extras')],
        })
        return schema

    def group_form(group_type='collection'):
        return 'collection/snippets/collection_form.html'

    def index_template(self):
        return 'collection/index.html'

    def read_template(self):
        return 'collection/read.html'

    def new_template(self):
        return 'collection/new.html'

    def edit_template(self):
        return 'collection/edit.html'

    def about_template(self):
        return 'collection/about.html'

    def history_template(self):
        return 'collection/history.html'

    def activity_template(self):
    	return 'collection/activity_stream.html'

    def admins_template(self):
    	return 'collection/admins.html'

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'collections')

    # IRoutes
    def before_map(self, map):
        '''
        Map custom controllers and endpoints
        '''
        package_controller = "ckanext.collections.controller:CollectionsPackageController"

        with routes.mapper.SubMapper(map, controller=package_controller) as m:
                m.connect('dataset_collections', '/dataset/collections/{id}',
                  action='collections', ckan_icon='group')
                m.connect('dataset_groups', '/dataset/groups/{id}',
                  action='groups', ckan_icon='group')


        collection_controller = 'ckanext.collections.controller:CollectionController'

        with routes.mapper.SubMapper(map, controller=collection_controller) as m:
	        m.connect('collection_index', '/collection', action='index')
	        m.connect('/collection/list', action='list')
	        m.connect('/collection/new', action='new')
	        m.connect('/collection/{action}/{id}',
	                requirements=dict(action='|'.join([
	                    'delete',
	                    'admins',
	                    'member_new',
	                    'member_delete',
	                    'history'
	                    'followers',
	                    'follow',
	                    'unfollow',
	                ])))
	        m.connect('collection_activity', '/collection/activity/{id}/{offset}',
	                action='activity', ckan_icon='time')
	        m.connect('collection_read', '/collection/{id}', action='read')
	        m.connect('collection_about', '/collection/about/{id}',
	                action='about', ckan_icon='info-sign')
	        m.connect('collection_read', '/collection/{id}', action='read',
	                ckan_icon='sitemap')
	        m.connect('collection_edit', '/collection/edit/{id}',
	                action='edit', ckan_icon='edit')
	        m.connect('collection_members', '/collection/members/{id}',
	                action='members', ckan_icon='group')
	        m.connect('collection_bulk_process',
	                '/collection/bulk_process/{id}',
                    action='bulk_process', ckan_icon='sitemap')
    	return map