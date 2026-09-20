from setuptools import find_packages, setup

package_name = 'drone_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch',
         ['launch/drone_system.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='siva',
    maintainer_email='siva@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "uav1_node = drone_controller.uav1_node:main",
            "uav2_node = drone_controller.uav2_node:main",
            "coordinator = drone_controller.coordinator:main",
            "safety_monitor = drone_controller.safety_monitor:main"
        ],
    },
)
