from setuptools import setup, find_packages

version = '0.1.0-SNAPSHOT'

setup(
    name='ckanext-odn-pipeline',
    version=version,
    description="""
    Extension for administring pipelines
    """,
    long_description="""
    Extension for administring pipelines
    """,
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Martin Virag',
    author_email='martin.virag@eea.sk',
    uv_url='',
    license='',
    packages=find_packages(exclude=['examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.pipeline', 'ckanext.model',\
                        'ckanext.commands', 'ckanext.controllers'],
    package_data={'': [
                       'fanstatic/*.css',\
                       'fanstatic/*.js',\
                       'templates/*.html',\
                       'templates/package/*.html',\
                       'templates/pipeline/*.html',\
                       'templates/pipeline/snippets/*.html']},
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points=\
    """
    [ckan.plugins]
    pipeline=ckanext.pipeline.plugin:PipelinePlugin
    [paste.paster_command]
    pipeline-cmd = ckanext.commands.pipeline_cmd:PipelineCmd
    """,
)