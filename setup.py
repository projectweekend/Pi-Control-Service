from distutils.core import setup

setup(
    name='Pi-Control-Service',
    version='1.1.2',
    author='Brian Hines',
    author_email='brian@projectweekend.net',
    packages=['pi_control_service'],
    url='http://projectweekend.github.io/Pi-Control-Service',
    license='LICENSE.txt',
    description='Control a Raspberry Pi from anywhere.',
    long_description=open('README.txt').read(),
    install_requires=[
        "Pika-Pack == 1.0.0",
        "Pi-Pin-Manager == 0.1.0",
    ],
)
