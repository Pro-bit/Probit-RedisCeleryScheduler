import os
from setuptools import setup, find_packages

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

REQUIREMENTS = ["redis", "redlock-py", "celery==5.2.2", "billiard==3.3.0.21", "kombu==3.0.37"]

README = """
probit-scheduler - redis backed scheduler for celery beat. This scheduler was made from https://github.com/SPSCommerce/swiss-chard.git with some modifications.

The MIT License (MIT)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

setup(
    name='probit-scheduler',
    version='0.1.7',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    description='probit scheduler - JSON redis backed scheduler for celery beat.',
    long_description=README,
    url='https://github.com/Pro-bit/Probit-RedisCeleryScheduler',
    author='ProBitDeveloper',
    author_email='pro4.developer@gmail.com',
    install_requires=REQUIREMENTS
)
