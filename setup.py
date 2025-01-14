from setuptools import setup
import unittest
import logging
from unittest import TestSuite

logging.basicConfig(format='%(asctime)s:%(name)-35s %(levelname)s:%(message)s', level=logging.INFO,
                    datefmt='%H:%M:%S %z')

logger = logging.getLogger(__name__)


def my_test_suite():
    test_loader = unittest.TestLoader()

    test_suites = test_loader.discover('test', pattern='*_test.py')
    return test_suites

def get_long_desc() -> str:
    with open('README.md', 'r') as file_handle:
        lines = []
        for line in next(file_handle):
            if len(line.strip()) == 0:
                break
            else:
                lines.append(line)
        return "\n".join(lines)

setup(
    name='vectara-skunk-client',
    description='Vectara Skunk Client',
    long_description=get_long_desc(),
    long_description_content_type='text/markdown',
    version='0.5.9',
    author='David Levy',
    author_email='david.g.levy@gmail.com',
    url='https://github.com/davidglevy/vectara-skunk-client',
    license='GNU AFFERO GENERAL PUBLIC LICENSE v3',
    package_dir={
        'vectara_client': 'vectara_client'
    },
    packages=['vectara_client'],
    install_requires=['requests', 'dacite>=1.8.1', 'Authlib==1.3.1', 'pyaml==23.9.7', 'tqdm==4.66.1',
                      'requests-toolbelt==1.0.0', 'cryptography==40.0.2'],
    python_requires='>=3.4',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.12',
        'Topic :: Utilities'
    ],
    test_suite='setup.my_test_suite'
)