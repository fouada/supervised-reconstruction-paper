from setuptools import setup


setup(
    name='cldfbench_wkisemitic',
    py_modules=['cldfbench_wikisemitic'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'cldfbench.dataset': [
            'kogansemitic=cldfbench_wikisemitic:Dataset',
        ]
    },
    install_requires=[
        'cldfbench',
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)
