from pip.req import parse_requirements
from setuptools import find_packages
from setuptools import setup

setup(
    name='flask-rest-jsonapi-requests',
    version='0.3.3',
    description='Flask-REST-JSONAPI client implementation. http://jsonapi.org/',
    author='Anurag Agarwal',
    author_email='anurag.a@practo.com',
    url='https://github.com/practo/jsonapi-requests',
    packages=find_packages(exclude=['tests']),
    install_requires=[str(ir.req) for ir in parse_requirements('requirements.txt', session=False)],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    use_2to3=True,
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
