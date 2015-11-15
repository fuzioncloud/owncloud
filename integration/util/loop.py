from integration.util.ssh import run_ssh


def loop_device_cleanup(num=0):
    print('cleanup')
    for mount in run_ssh('mount', debug=False).splitlines():
        if 'loop' in mount:
            print(mount)

    for loop in run_ssh('losetup').splitlines():
        if 'loop{0}'.format(num) in loop:
            run_ssh('losetup -d /dev/loop{0}'.format(num), throw=False)

    run_ssh('losetup')

    for loop in run_ssh('dmsetup ls').splitlines():
        if 'loop{0}'.format(num) in loop:
            run_ssh('sudo dmsetup remove loop{0}p1'.format(num))

    for loop_disk in run_ssh('ls -la /tmp').splitlines():
        if '/tmp/disk{0}'.format(num) in loop_disk:
            run_ssh('rm -fr /tmp/disk{0}'.format(num), throw=False)


def loop_device_add(fs='ext4', dev_num=0):

    print('adding loop device')
    run_ssh('dd if=/dev/zero bs=1M count=10 of=/tmp/disk{0}'.format(dev_num))

    run_ssh('losetup /dev/loop{0} /tmp/disk{0}'.format(dev_num))
    run_ssh('file -s /dev/loop{0}'.format(dev_num))
    run_ssh('mkfs.{0} /dev/loop{1}'.format(fs, dev_num))
    return '/dev/loop{0}'.format(dev_num)
