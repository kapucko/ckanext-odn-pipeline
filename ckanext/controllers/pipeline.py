'''
Created on 12.11.2014

@author: mvi
'''

import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.plugins
import ckan.logic as logic
import ckan.model as model

from ckan.common import _, request, c
from ckanext.model.pipelines import Pipelines
from ckanext.pipeline.plugin import get_pipeline

import pylons.config as config
uv_url = config.get('odn.uv.url', None)

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized

render = base.render
abort = base.abort
lookup_package_plugin = ckan.lib.plugins.lookup_package_plugin
check_access = logic.check_access
get_action = logic.get_action


class ICController(base.BaseController):

    
    def _get_package_type(self, id):
        """
        Given the id of a package it determines the plugin to load
        based on the package's type name (type). The plugin found
        will be returned, or None if there is no plugin associated with
        the type.
        """
        pkg = model.Package.get(id)
        if pkg:
            return pkg.type or 'dataset'
        return None

    def _load(self, id):
        package_type = self._get_package_type(id.split('@')[0])
        data_dict = {'id': id}
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'auth_user_obj': c.userobj}
        
        try:
            check_access('package_update', context, data_dict)
        except NotAuthorized, e:
            abort(401, _('User {user} not authorized to edit {id}').format(user=c.user, id=id))
        # check if package exists
        try:
            c.pkg_dict = get_action('package_show')(context, data_dict)
            c.pkg = context['package']
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read package {id}').format(id=id))
        
        lookup_package_plugin(package_type).setup_template_variables(context, {'id': id})
    
    
    def show(self, id):
        self._load(id)
        vars = {'uv_edit_url': uv_url + '/unifiedviews/#!PipelineEdit/{pipe_id}'}
        return render('package/pipelines.html', extra_vars = vars)
    
    
    def choose_pipeline(self, id):
        data = request.POST
        if u'action' in data:
            action = data[u'action']
            if action == 'existing':
                self._load(id)
                return render('pipeline/assign_pipeline.html')
            else:
                abort(404, _('Not implemented yet'))
        else:
            abort(404, _('Action was not choosed!'))
    
    
    def choose_action(self, id):
        self._load(id) 
        return render('pipeline/choose_assign_action.html')
    
    
    def assign(self, id):
        pipe = None
        data = request.POST
        if u'pipeline' in data:
            pipe_id = data[u'pipeline']
            pipe, err_msg = get_pipeline(pipe_id)

        data_dict = {'id': id}
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'auth_user_obj': c.userobj}

        if not pipe:
            h.flash_notice(_("No pipeline selected."))
            base.redirect(h.url_for('dataset_pipelines', id=id))
            return

        try:
            check_access('package_update', context, data_dict)
            package = get_action('package_show')(context, data_dict)
            
            # checks if already exists
            if Pipelines.by_pipeline_id(pipe['id']):
                h.flash_error(_('Pipeline is already associated to some dataset.'))
                base.redirect(h.url_for('pipe_assign', id=id))
            else:
                # adds pipe association
                package_pipe = Pipelines(package['id'], pipe['id'], name=pipe['name'])
                package_pipe.save() # this adds and commits too
                h.flash_success(_("Pipeline assigned successfully."))
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized, e:
            abort(401, _('User {user} not authorized to edit {id}').format(user=c.user, id=id))
        
        base.redirect(h.url_for('pipe_assign', id=id))
    
    def remove_pipe(self, id, pipeline_id):
        assert id
        assert pipeline_id
        
        try:
            data_dict = {'id': id}
            context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'auth_user_obj': c.userobj}
            check_access('package_update', context, data_dict)
            package = get_action('package_show')(context, data_dict)
            # id is most probably is package.name so we have to get actual id
            pipe = Pipelines(package['id'], pipeline_id).get()
            
            if not pipe:
                h.flash_error(_("Couldn't remove pipeline, because\
                there is no such pipeline assigned to this dataset."))
                base.redirect(h.url_for('pipe_assign', id=id))
            else:
                pipe.delete()
                pipe.commit()
                h.flash_success(_('Pipeline removed from dataset successfully'))
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized, e:
            abort(401, _('User {user} not authorized to edit {id}').format(user=c.user, id=id))
        
        base.redirect(h.url_for('pipe_assign', id=id))
