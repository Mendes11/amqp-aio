import setuptools

setuptools.setup(
    packages=setuptools.find_packages(exclude=["tests"]),
    name='amqp-aio',
    url='https://github.com/Mendes11/amqp-aio',
    version='0.0.1',
    description='Async AMQP Library',
    long_description= 'file: README.md',
    author = 'Rafael Mendes Pacini Bachiega',
    author_email = 'rafaelmpb11@hotmail.com',
    classifiers =
    ['Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9'],
    install_requires=[
        "aiormq<6"
    ],
)
