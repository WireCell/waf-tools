# -*- python -*-
'''This tool implements a source package following a few contentions.

Your source package may build any combination of the following:

 - shared libraries 
 - headers exposing an API to libraries
 - a ROOT dictionary for this API
 - main programs
 - test programs

This tool will produce various methods on the build context.  You can
avoid passing <name> to them if you set APPNAME in your wscript file.

'''

import os.path as osp
from waflib.Utils import to_list
from waflib.Configure import conf
import waflib.Context
from waflib.Logs import debug, info, error, warn

_tooldir = osp.dirname(osp.abspath(__file__))

def options(opt):
    opt.load('compiler_cxx')
    opt.load('waf_unit_test')
    opt.load('rootsys', tooldir=_tooldir)
    #opt.load('eigen3', tooldir=_tooldir)
    opt.load('boost', tooldir=_tooldir)
    

def configure(cfg):
    cfg.load('compiler_cxx')
    cfg.load('waf_unit_test')
    cfg.load('rootsys', tooldir=_tooldir)
    #cfg.load('eigen3', tooldir=_tooldir)
    cfg.load('boost', tooldir=_tooldir)

    cfg.env.append_unique('CXXFLAGS',['--std=c++11'])

    cfg.check_boost(lib='system filesystem graph thread')
    pass

def build(bld):
    from waflib.Tools import waf_unit_test
    bld.add_post_fun(waf_unit_test.summary)


@conf
def smplpkg(bld, name, use='', app_use='', test_use=''):
    use = list(set(to_list(use)))
    app_use = list(set(use + to_list(app_use)))
    test_use = list(set(use + to_list(test_use)))

    includes = []
    headers = []
    source = []

    incdir = bld.path.find_dir('inc')
    srcdir = bld.path.find_dir('src')
    dictdir = bld.path.find_dir('dict')

    testsrc = bld.path.ant_glob('test/test_*.cxx')
    appsdir = bld.path.find_dir('apps')

    if incdir:
        headers += incdir.ant_glob(name + '/*.h')
        includes += ['inc']
        bld.env['INCLUDES_'+name] = [incdir.abspath()]

    if headers:
        bld.install_files('${PREFIX}/include/%s' % name, headers)

    if srcdir:
        source += srcdir.ant_glob('*.cxx')

    # fixme: I should move this out of here.
    # root dictionary
    if dictdir:
        if not headers:
            error('No header files for ROOT dictionary "%s"' % name)
        #print 'Building ROOT dictionary: %s using %s' % (name,use)
        if 'ROOTSYS' in use:
            linkdef = dictdir.find_resource('LinkDef.h')
            bld.gen_rootcling_dict(name, linkdef,
                                   headers = headers,
                                   includes = includes, 
                                   use = use)
            source.append(bld.path.find_or_declare(name+'Dict.cxx'))
        else:
            warn('No ROOT dictionary will be generated for "%s" unless "ROOTSYS" added to "use"' % name)

    # the library
    if incdir and srcdir:
        #print "Building library: %s using %s"%(name, use)
        bld(features = 'cxx cxxshlib',
            name = name,
            source = source,
            target = name,
            includes = 'inc',
            export_includes = 'inc',
            use = use)            

    if testsrc:
        for test_main in testsrc:
            #print 'Building %s test: %s using %s' % (name, test_main, test_use)
            bld.program(features = 'test', 
                        source = [test_main], 
                        target = test_main.name.replace('.cxx',''),
                        install_path = None,
                        includes = ['inc','test','tests'],
                        use = test_use + [name])
    if appsdir:
        for app in appsdir.ant_glob('*.cxx'):
            #print 'Building %s app: %s using %s' % (name, app, app_use)
            bld.program(source = [app], 
                        target = app.name.replace('.cxx',''),
                        includes = 'inc',
                        use = app_use + [name])

    