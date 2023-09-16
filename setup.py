from setuptools import setup, find_packages

setup(
    name="chatgpt_conversations",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # Add your project's dependencies here
    ],
    entry_points={
        "console_scripts": [
            "chatgpt_conversations=chatgpt_conversations.main:main",
        ],
    },
)
