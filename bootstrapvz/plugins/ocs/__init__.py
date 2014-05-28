import os.path

from bootstrapvz.common.tasks import apt
from bootstrapvz.common.tasks import initd
from bootstrapvz.common.tasks import locale
from bootstrapvz.plugins.ocs import tasks as ocstasks
from bootstrapvz.providers import kvm


def validate_manifest(data, validator, error):
    schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                                'manifest-schema.json'))
    validator(data, schema_path)


def resolve_tasks(taskset, manifest):
    #settings = manifest.plugins['ocs']
    discard_tasks = [locale.GenerateLocale,
                     apt.AddDefaultSources,
                     initd.InstallInitScripts]
    for task in discard_tasks:
        taskset.discard(task)

    taskset.add(ocstasks.GenerateLocale)
    taskset.add(ocstasks.AddDefaultSources)
    taskset.add(ocstasks.InstallInitScripts)

    if manifest.provider == 'kvm':
        taskset.discard(kvm.tasks.packages.DefaultPackages)
        taskset.add(ocstasks.DefaultPackagesKVM)
