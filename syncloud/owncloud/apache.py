import os


def create_link(instrall_path, apache_link):
    print("create link for apache")
    os.symlink(instrall_path, apache_link)


def drop_link(apache_link):
    print("drop link for apache")
    if os.path.islink(apache_link):
        os.unlink(apache_link)
