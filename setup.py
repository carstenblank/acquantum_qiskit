#  Copyright (c) 2019.  Carsten Blank
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from setuptools import setup

with open("providers/_version.py") as f:
    version = f.readlines()[-1].split()[-1].strip("\"'")

with open("README.rst", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.readlines()

info = {
    'name': 'acquantum-qiskit',
    'version': version,
    'author': 'Carsten Blank',
    'author_email': 'blank@data-cybernetics.com',
    'description': 'A qiskit provider for the Alibaba\'s quantum computer.',
    'long_description': long_description,
    'url': 'https://github.com/sebboer/acquantum_qiskit',
    'install_requires': requirements,
    'packages': [
        'providers',
        'providers.acquantum',
        'providers.acquantum.credentials',
        'providers.acquantum.models'
    ],
    'license': 'Apache 2.0',
}

classifiers = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3 :: Only',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
]

setup(classifiers=classifiers, **info)
