"""Tasks specific to bootstrapping OCS."""

import os
import shutil
import stat
import bootstrapvz.base
from bootstrapvz.common import phases
from bootstrapvz.common import tools
from bootstrapvz.common.tasks import apt


class GenerateLocale(bootstrapvz.base.Task):
    description = 'Generating the selected locale (OCS)'
    phase = phases.package_installation

    @classmethod
    def run(cls, info):
        lang = '{locale}.{charmap}'.format(
            locale=info.manifest.system['locale'],
            charmap=info.manifest.system['charmap'])

        tools.log_check_call(['chroot', info.root, 'locale-gen', lang])
        tools.log_check_call(['chroot', info.root, 'update-locale',
                              'LANG=%s' % lang])


class AddDefaultSources(bootstrapvz.base.Task):
    description = 'Adding default release sources (OCS)'
    phase = phases.preparation
    predecessors = [apt.AddManifestSources]

    @classmethod
    def run(cls, info):
        components = ' '.join(
            info.manifest.packages.get('components', ['main']))

        info.source_lists.add(
            'main',
            'deb     {apt_mirror} {system.release} %s' % components)
        info.source_lists.add(
            'main',
            'deb-src {apt_mirror} {system.release} %s' % components)
        info.source_lists.add(
            'main',
            'deb     {apt_mirror} {system.release}-updates %s' % components)
        info.source_lists.add(
            'main',
            'deb-src {apt_mirror} {system.release}-updates %s' % components)
        info.source_lists.add(
            'main',
            'deb     {apt_mirror} {system.release}-security %s' % components)
        info.source_lists.add(
            'main',
            'deb-src {apt_mirror} {system.release}-security %s' % components)


class DefaultPackagesKVM(bootstrapvz.base.Task):
    description = 'Adding image packages required for kvm (OCS)'
    phase = phases.preparation
    predecessors = [apt.AddDefaultSources]

    @classmethod
    def run(cls, info):
        info.packages.add('linux-image-generic')


class InstallInitScripts(bootstrapvz.base.Task):
    desciprion = 'Installing startup scripts (OCS)'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        rwxr_xr_x = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                     stat.S_IRGRP                | stat.S_IXGRP |
                     stat.S_IROTH                | stat.S_IXOTH)

        for name, src in info.initd['install'].iteritems():
            dst = os.path.join(info.root, 'etc/init.d', name)
            shutil.copy(src, dst)
            os.chmod(dst, rwxr_xr_x)
            tools.log_check_call(
                ['chroot', info.root, 'update-rc.d', name, 'defaults'])

        for name in info.initd['disable']:
            tools.log_check_call(
                ['chroot', info.root, 'update-rc.d', name, 'disable'])
