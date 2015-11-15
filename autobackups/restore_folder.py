import os
import shutil


def recover_backup(source, destination):
    """
    Removes the autobackup timestamp and copies the newest version of the backup to destination.

    Note: Information about deleted files and directories can not be recovered, thus deleted files and folders will also
    be recovered.

    :param source: str
    :param destination: str
    :return: None
    """
    extension = os.path.splitext(source)[1]
    original_filename = os.path.basename(source).rsplit('_', 1)[0] + extension
    destination_path = os.path.join(os.path.dirname(destination), original_filename)
    if os.path.exists(destination_path):
        # XXX: This should never happen, since recover_backup is called with the last modified files first
        # Remove an existing, older file with the same name as the directory
        if os.path.isfile(destination_path) and os.stat(source).st_mtime_ns >= os.stat(destination_path).st_mtime_ns:
            os.remove(destination_path)

        # Skip if file isn't newer than the existing one
        elif not os.stat(source).st_mtime_ns >= os.stat(destination_path).st_mtime_ns:
            return

    destination_directory = os.path.dirname(destination_path)
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    # Set original last accessed and modified times for the file
    shutil.copy(source, destination_path)
    source_stat = os.stat(source)
    os.utime(destination_path, (source_stat.st_atime, source_stat.st_mtime))


def restore_folder(backups_path, normalized_path, recover_path):
    paths = []

    for directory in os.listdir(backups_path):
        backup_path = os.path.join(backups_path, directory)
        if not os.path.isdir(backup_path):
            continue

        target_path = os.path.join(backup_path, normalized_path)
        if not os.path.exists(target_path):
            continue

        for root, directories, filenames in os.walk(target_path):
            for filename in filenames:
                source_path = os.path.join(root, filename)
                destination_path = os.path.join(recover_path, os.path.relpath(os.path.join(root, filename), target_path))
                paths.append((source_path, destination_path))

    for source_path, destination_path in sorted(paths, key=lambda paths: os.stat(paths[0]).st_mtime_ns, reverse=True):
        recover_backup(source_path, destination_path)
