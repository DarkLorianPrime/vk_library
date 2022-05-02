from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setup(name='vk_dark_library',
      version='1.0.5',
      url='https://github.com/DarkLorianPrime/vk_library',
      license='Apache License, Version 2.0, see LICENSE file',
      author='Darklorian (Aleksander Kasimov)',
      author_email='lolpokens@mail.ru',
      description='Быстрое и удобное создание ботов в вк. Пока только LongPoll.',
      packages=find_packages(),
      long_description=readme,
      install_requires=["requests>=2"])