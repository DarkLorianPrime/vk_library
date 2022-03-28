from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setup(name='vk_dark_library',
      version='0.1.2',
      url='https://github.com/the-gigi/pathology',
      license='Apache License, Version 2.0, see LICENSE file',
      author='Darklorian (Aleksander Kasimov)',
      author_email='lolpokens@mail.ru',
      description='Быстрое и удобное создание ботов в вк. Как LongPoll так и Callback',
      packages=find_packages(),
      long_description=readme,
      install_requires=["requests>=2"])