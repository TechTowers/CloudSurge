pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'cloudsurge'
gnome = import('gnome')

blueprints = custom_target('blueprints',
  input: files(
    # LIST YOUR BLUEPRINT FILES HERE
    'blueprints/window.blp'
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
]

install_data(cloudsurge_sources, install_dir: moduledir)