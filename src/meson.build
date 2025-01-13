pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'cloudsurge'
gnome = import('gnome')

blueprints = custom_target('blueprints',
  input: files(
    # LIST YOUR BLUEPRINT FILES HERE
    'blueprints/window.blp',
    'blueprints/new.blp',
    'blueprints/vm_settings_window.blp',
    'blueprints/provider_settings_window.blp',
    'blueprints/wait_popup.blp',
    'blueprints/error.blp',
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources('cloudsurge',
  'cloudsurge.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: blueprints,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'cloudsurge.in',
  output: 'cloudsurge',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)

cloudsurge_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'new.py',
  'vm_settings_window.py',
  'provider_settings_window.py',
  'wait_popup_window.py',
  'error_window.py',
  'backend/db.py',
  'backend/aws_provider.py',
  'backend/digitalocean_provider.py',
  'backend/vm.py',
  'backend/no_provider.py',
  'backend/reached_cost_limits.py',
  'backend/server_is_active.py',
]

install_data(cloudsurge_sources, install_dir: moduledir)
